"""Logix (Allen-Bradley / Rockwell) PLC tag source for scene bindings.

Provides :class:`LogixSource`, a source object that exposes live PLC tags as
plain instance attributes so that
:meth:`~pyrox.models.scene.sceneboundlayer.SceneBoundLayer.enumerate_source_properties`
discovers them automatically and the scene bridge browser shows them without
any special-casing.

Tags are discovered at construction time by querying the connected PLC via
:class:`~controlrox.services.plc.PlcConnectionManager`.  The same manager
supplies the connection parameters used by :meth:`refresh` and
:meth:`write_tag`, so a :class:`LogixSource` always targets the PLC that
the application is currently connected to.

Quick start::

    from controlrox.models.scene.sources.logix import LogixSource

    # Build once per scene — seeds attributes from live PLC tag list.
    source = LogixSource()

    # Register so the bridge picks it up automatically on every scene load.
    SceneBridgeService.register_source_factory("logix", lambda: LogixSource())

    # In your scene update loop (or on a timer):
    source.refresh()   # polls the PLC and updates every attribute

Tag-name sanitisation
---------------------
Base tag names returned by pylogix are already valid Python identifiers, so
they map directly to attributes.  If you call :meth:`track_tag` with a
member-access path such as ``"Drive.RunCmd"``, the dot is replaced with an
underscore (``Drive_RunCmd``) for the attribute name while the original path
is retained internally so reads and writes address the PLC correctly.
"""
from __future__ import annotations

from typing import Any

from pylogix import PLC

from controlrox.services.plc.connection import PlcConnectionManager, PlcConnectionEventBus, PlcConnectionEventType
from pyrox.services.logging import log
from pyrox.services.scene import SceneBridgeService


class LogixSource:
    """Scene-bridge source that presents live Logix PLC tag values as attributes.

    Tags are discovered automatically by querying the connected PLC via
    :class:`~controlrox.services.plc.PlcConnectionManager`.  Each discovered
    tag is exposed as a plain instance attribute (value ``None`` until the
    first :meth:`refresh` call) so that
    :meth:`~pyrox.models.scene.sceneboundlayer.SceneBoundLayer.enumerate_source_properties`
    finds them via ``dir()`` without any special-casing.

    All connection parameters (IP address, slot) are read directly from
    :attr:`PlcConnectionManager.connection_parameters`, so this source always
    targets whichever PLC the application is currently connected to.

    Typical workflow:

    1. Ensure :class:`~controlrox.services.plc.PlcConnectionManager` has been
       configured and connected.
    2. Construct ``LogixSource()``.  Tag attributes are seeded from
       ``GetTagList()`` immediately.
    3. Register with :class:`~pyrox.services.scene.SceneBridgeService` so the
       bridge receives a fresh instance on every scene load.
    4. Call :meth:`refresh` periodically (scene update loop / timer) to keep
       values current.

    Example bridge binding path: ``"logix.Motor1_Speed"``

    Attributes:
        <tag_name>: One attribute per discovered tag (e.g. ``source.Motor1``).
                    Values default to ``None`` and are updated by
                    :meth:`refresh`.
    """

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    def __init__(self, scalar_only: bool = True) -> None:
        """Initialise the source and seed attributes from the live PLC tag list.

        Calls ``PlcConnectionManager.read_plc_tag_table()`` to enumerate
        controller-scope tags.  If the PLC is unreachable at construction
        time, the tag set is empty; you can call :meth:`reseed` later once
        connectivity is established, or add tags individually with
        :meth:`track_tag`.

        Args:
            scalar_only: When ``True`` (default) only atomic/scalar tags
                         (non-struct, non-array) are auto-discovered.  Set to
                         ``False`` to also track UDT and array tags; their
                         attribute values will be whatever pylogix returns.
        """
        # Use object.__setattr__ for all *internal* state so that tag-name
        # attributes never collide with private bookkeeping fields.

        # {sanitised_attr_name: original_plc_tag_name}
        object.__setattr__(self, '_tag_map', {})

        PlcConnectionEventBus.subscribe(
            PlcConnectionEventType.CONNECTED,
            lambda _: self.reseed(scalar_only=scalar_only)
        )

        self._seed_from_plc(scalar_only=scalar_only)

    def __getattribute__(self, name: str) -> Any:
        # Override to provide a clearer error message when accessing an unknown tag.
        tag_map: dict = object.__getattribute__(self, '_tag_map')
        if name in tag_map:
            return self._track_tag_value(name)
        else:
            return super().__getattribute__(name)

    def __setattr__(self, name: str, value: Any) -> None:
        if name in object.__getattribute__(self, '_tag_map'):
            self._write_tag_value(name, value)
        else:
            super().__setattr__(name, value)

    # ------------------------------------------------------------------
    # Tag discovery
    # ------------------------------------------------------------------

    def _track_tag_value(self, plc_tag_name: str) -> Any:
        """Helper to read a single tag value from the PLC for initial seeding.
        """
        watched_tags = PlcConnectionManager.get_watch_table()
        if plc_tag_name in watched_tags:  # We're already watching this tag, so we have a value cached.
            return object.__getattribute__(self, plc_tag_name)

        if object.__getattribute__(self, plc_tag_name) is None:
            # Attempt to read a value to see if it's worth tracking
            val = PlcConnectionManager.read_plc_tag(plc_tag_name).Value

            if val is None:
                log(self).debug(
                    "LogixSource: tag '%s' read returned None, skipping watch setup",
                    plc_tag_name,
                )
                return None

            # Set up a watched tag with the connection manager for future requests
            PlcConnectionManager.add_watch_tag(
                plc_tag_name,
                data_type=0,  # Let pylogix infer the type on first read
                callback=lambda value: object.__setattr__(self, plc_tag_name, value.Value)
            )
            return val

    def _write_tag_value(self, plc_tag_name: str, value: Any) -> None:
        """Helper to write a single tag value to the PLC for initial seeding.
        """
        if plc_tag_name not in object.__getattribute__(self, '_tag_map'):
            raise AttributeError(f"Tag '{plc_tag_name}' is not tracked; cannot write value")
        PlcConnectionManager.write_watch_tag(plc_tag_name, value)

    def _seed_from_plc(self, scalar_only: bool = True) -> None:
        """Query the PLC for its tag list and pre-declare one attribute per tag.

        Uses :meth:`PlcConnectionManager.read_plc_tag_table` which calls
        pylogix ``comm.GetTagList()``.  Each ``LGXTag`` in the response is
        inspected:

        * When *scalar_only* is ``True``, tags where ``Struct != 0`` (UDTs)
          or ``Array != 0`` (arrays) are skipped.
        * All other tags are registered via :meth:`track_tag`.

        A failed or empty response is treated as a no-op with a warning so
        that offline construction still succeeds.

        Args:
            scalar_only: Filter to atomic/scalar tags only.
        """
        try:
            response = PlcConnectionManager.read_plc_tag_table(all_tags=False)
        except Exception as exc:
            log(self).warning("LogixSource: tag list query failed — %s", exc)
            return

        if not response or response.Status != 'Success' or not response.Value:
            log(self).warning(
                "LogixSource: GetTagList returned no data (status=%s)",
                getattr(response, 'Status', 'N/A'),
            )
            return

        for tag in response.Value:
            if not tag or not getattr(tag, 'TagName', None):
                continue

            if scalar_only:
                # Struct != 0 → UDT/structure; Array != 0 → array type.
                if getattr(tag, 'Struct', 0) != 0 or getattr(tag, 'Array', 0) != 0:
                    continue

            self.track_tag(tag.TagName)

        log(self).debug("LogixSource: seeded %d tags from PLC", len(object.__getattribute__(self, '_tag_map')))

    def reseed(self, scalar_only: bool = True) -> None:
        """Re-query the PLC tag list and refresh the attribute set.

        Clears all existing tracked tags then calls :meth:`_seed_from_plc`
        again.  Useful after reconnecting to a different controller or when the
        PLC program has changed.

        Args:
            scalar_only: Passed through to :meth:`_seed_from_plc`.
        """
        tag_map: dict = object.__getattribute__(self, '_tag_map')
        for attr_name in list(tag_map):
            try:
                object.__delattr__(self, attr_name)
            except AttributeError:
                pass
        tag_map.clear()
        self._seed_from_plc(scalar_only=scalar_only)

    def track_tag(self, plc_tag_name: str, initial_value: Any = None) -> str:
        """Add a tag to the tracked set and declare it as an instance attribute.

        Safe to call multiple times for the same tag — idempotent once a tag
        is already registered.

        Args:
            plc_tag_name:  PLC tag address to track.  May be a base tag name
                           (``"Motor1"``) or a member-access path
                           (``"Drive.RunCmd"``).
            initial_value: Attribute value before the first :meth:`refresh`.
                           Defaults to ``None``.

        Returns:
            The Python-safe attribute name (dots replaced with underscores).
        """
        attr_name = plc_tag_name.replace('.', '_')
        tag_map: dict = object.__getattribute__(self, '_tag_map')

        if attr_name not in tag_map:
            tag_map[attr_name] = plc_tag_name
            object.__setattr__(self, attr_name, initial_value)

        return attr_name

    def untrack_tag(self, plc_tag_name: str) -> None:
        """Stop tracking a tag and remove its attribute.

        Args:
            plc_tag_name: The PLC tag address originally passed to
                          :meth:`track_tag`.
        """
        attr_name = plc_tag_name.replace('.', '_')
        tag_map: dict = object.__getattribute__(self, '_tag_map')

        if attr_name in tag_map:
            del tag_map[attr_name]
            try:
                object.__delattr__(self, attr_name)
            except AttributeError:
                pass

    # ------------------------------------------------------------------
    # Live PLC I/O
    # ------------------------------------------------------------------

    def refresh(self) -> None:
        """Read all tracked tags from the PLC and update their attributes.

        Opens a short-lived pylogix session using
        :attr:`PlcConnectionManager.connection_parameters`, performs a single
        batch read of every tracked tag, then closes the session.  Call this
        from a periodic timer or your scene's update loop.

        No-op if no tags are currently tracked.
        """
        tag_map: dict = object.__getattribute__(self, '_tag_map')
        if not tag_map:
            return

        params = PlcConnectionManager.connection_parameters
        plc_tag_names = list(tag_map.values())

        try:
            with PLC(
                ip_address=str(params.ip_address),
                slot=params.slot,
            ) as comm:
                responses = comm.Read(plc_tag_names)

                # pylogix returns a single Response for one tag, a list for many.
                if not isinstance(responses, list):
                    responses = [responses]

                for resp in responses:
                    if resp is None:
                        continue

                    if resp.Status != 'Success':
                        log(self).debug(
                            "LogixSource: tag '%s' read failed — %s",
                            resp.TagName,
                            resp.Status,
                        )
                        continue

                    attr_name = resp.TagName.replace('.', '_')
                    object.__setattr__(self, attr_name, resp.Value)

        except Exception as exc:
            log(self).warning("LogixSource.refresh() error: %s", exc)

    def write_tag(self, plc_tag_name: str, value: Any) -> bool:
        """Write *value* to a PLC tag and update the local attribute on success.

        Uses :attr:`PlcConnectionManager.connection_parameters` for the
        connection.

        Args:
            plc_tag_name: The PLC tag address to write (dots preserved,
                          e.g. ``"Drive.InhibitBit"``).
            value:        The value to write.

        Returns:
            ``True`` if the PLC acknowledged the write as successful,
            ``False`` otherwise.
        """
        params = PlcConnectionManager.connection_parameters

        try:
            with PLC(
                ip_address=str(params.ip_address),
                slot=params.slot,
            ) as comm:
                resp = comm.Write(plc_tag_name, value)
                if isinstance(resp, list):
                    resp = resp[0]

                if resp.Status == 'Success':
                    attr_name = plc_tag_name.replace('.', '_')
                    object.__setattr__(self, attr_name, value)
                    return True

                log(self).debug(
                    "LogixSource.write_tag('%s') failed: %s",
                    plc_tag_name,
                    resp.Status,
                )
                return False

        except Exception as exc:
            log(self).warning(
                "LogixSource.write_tag('%s') error: %s",
                plc_tag_name,
                exc,
            )
            return False

    # ------------------------------------------------------------------
    # Introspection helpers
    # ------------------------------------------------------------------

    def tracked_tags(self) -> dict[str, str]:
        """Return a ``{attr_name: plc_tag_name}`` snapshot of tracked tags."""
        tag_map: dict = object.__getattribute__(self, '_tag_map')
        return dict(tag_map)

    # ------------------------------------------------------------------
    # Representation
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        tag_map: dict = object.__getattribute__(self, '_tag_map')
        ip = str(PlcConnectionManager.connection_parameters.ip_address)
        return f"LogixSource(ip={ip!r}, tags={len(tag_map)})"


# ---------------------------------------------------------------------------
# Auto-register with SceneBridgeService
#
# Importing this module is enough to make "logix" available as a source in
# every scene that loads after import.  The lambda defers construction so that
# PlcConnectionManager is queried at scene-load time (when the PLC is most
# likely already connected) rather than at import time.
# ---------------------------------------------------------------------------
SceneBridgeService.register_source_factory("logix", lambda: LogixSource())
