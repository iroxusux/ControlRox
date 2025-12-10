"""AddOn Instruction Definition for a rockwell plc
"""
from __future__ import annotations
from typing import (
    Optional,
)

from pyrox.models.abc.factory import FactoryTypeMeta

from controlrox.interfaces import (
    IAddOnInstruction,
)

from controlrox.models.plc.protocols import (
    HasInstructions,
    HasRoutines,
    HasTags,
)

from controlrox.services import ControllerInstanceManager
from controlrox.services.plc.aoi import AOIFactory

from .meta import RaPlcObject, PLC_AOI_FILE


class RaAddOnInstruction(
    IAddOnInstruction,
    HasInstructions,
    HasRoutines,
    HasTags,
    RaPlcObject,
    metaclass=FactoryTypeMeta['RaAddOnInstruction', AOIFactory]
):
    """AddOn Instruction Definition for a rockwell plc
    """

    default_l5x_file_path = PLC_AOI_FILE
    default_l5x_asset_key = 'AddOnInstructionDefinition'

    def __init__(
        self,
        meta_data: Optional[dict] = None,
        name: str = '',
        description: str = '',
    ) -> None:
        """type class for plc AddOn Instruction Definition

        Args:
            l5x_meta_data (str): meta data
            controller (Self): controller dictionary
        """

        super().__init__(
            meta_data=meta_data,
            name=name,
            description=description,
        )
        # this is due to a weird rockwell issue with the character '<' in the revision extension
        if self.revision_extension is not None:
            self.revision_extension = self.revision_extension  # force the setter logic to replace anything that is input

    @property
    def dict_key_order(self) -> list[str]:
        return [
            '@Name',
            '@Class',
            '@Revision',
            '@ExecutePrescan',
            '@ExecutePostscan',
            '@ExecuteEnableInFalse',
            '@CreatedDate',
            '@CreatedBy',
            '@EditedDate',
            '@EditedBy',
            '@SoftwareRevision',
            'Description',
            'RevisionNote',
            'Parameters',
            'LocalTags',
            'Routines',
        ]

    @property
    def execute_prescan(self) -> str:
        return self['@ExecutePrescan']

    @execute_prescan.setter
    def execute_prescan(self, value: str):
        if isinstance(value, bool):
            value = 'true' if value else 'false'
        if not self.is_valid_rockwell_bool(value):
            raise self.InvalidNamingException

        self['@ExecutePrescan'] = value

    @property
    def execute_postscan(self) -> str:
        return self['@ExecutePostscan']

    @execute_postscan.setter
    def execute_postscan(self, value: str):
        if isinstance(value, bool):
            value = 'true' if value else 'false'
        if not self.is_valid_rockwell_bool(value):
            raise self.InvalidNamingException

        self['@ExecutePostscan'] = value

    @property
    def execute_enable_in_false(self) -> str:
        return self['@ExecuteEnableInFalse']

    @execute_enable_in_false.setter
    def execute_enable_in_false(self, value: str):
        if isinstance(value, bool):
            value = 'true' if value else 'false'
        if not self.is_valid_rockwell_bool(value):
            raise self.InvalidNamingException

        self['@ExecuteEnableInFalse'] = value

    @property
    def created_date(self) -> str:
        return self['@CreatedDate']

    @property
    def created_by(self) -> str:
        return self['@CreatedBy']

    @property
    def edited_date(self) -> str:
        return self['@EditedDate']

    @property
    def edited_by(self) -> str:
        return self['@EditedBy']

    @property
    def revision(self) -> str:
        """get the full revision string for this AOI

        Returns:
            :class:`str`: full revision string
        """
        return self.get_revision()

    @property
    def software_revision(self) -> str:
        return self['@SoftwareRevision']

    @software_revision.setter
    def software_revision(self, value: str):
        if not self.is_valid_revision_string(value):
            raise self.InvalidNamingException

        self['@SoftwareRevision'] = value

    @property
    def revision_extension(self) -> str:
        """get the revision extension for this AOI

        Returns:
            :class:`str`: revision extension
        """
        return self['@RevisionExtension']

    @revision_extension.setter
    def revision_extension(self, value: str):
        if not isinstance(value, str):
            raise ValueError("Revision extension must be a string!")

        self['@RevisionExtension'] = value.replace('<', '&lt;')

    @property
    def revision_note(self) -> str:
        return self['RevisionNote']

    @revision_note.setter
    def revision_note(self, value: str):
        if not isinstance(value, str):
            raise ValueError("Revision note must be a string!")

        self['RevisionNote'] = value

    @property
    def parameters(self) -> list[dict]:
        if not self['Parameters']:
            return []

        if not isinstance(self['Parameters']['Parameter'], list):
            return [self['Parameters']['Parameter']]
        return self['Parameters']['Parameter']

    @property
    def local_tags(self) -> list[dict]:
        if not self['LocalTags']:
            return []

        if not isinstance(self['LocalTags']['LocalTag'], list):
            return [self['LocalTags']['LocalTag']]
        return self['LocalTags']['LocalTag']

    @property
    def raw_tags(self) -> list[dict]:
        # rockwell is weird and this is the only instance they use 'local tags' instead of 'tags'
        if not self['LocalTags']:
            self['LocalTags'] = {'LocalTag': []}
        if not isinstance(self['LocalTags']['LocalTag'], list):
            self['LocalTags']['LocalTag'] = [self['LocalTags']['LocalTag']]
        return self['LocalTags']['LocalTag']

    @classmethod
    def get_factory(cls):
        return AOIFactory

    def compile_tags(self) -> None:
        """Compile the tags (local tags) for this AOI.

        Overrides HasTags.compile_tags to handle LocalTags structure and compile
        tag objects with appropriate container reference.
        """
        ctrl = ControllerInstanceManager.get_controller()
        if not ctrl:
            raise RuntimeError("No controller instance available for tag compilation.")

        self._tags.clear()
        self._safety_tags.clear()
        self._standard_tags.clear()

        for tag_meta in self.raw_tags:
            tag = ctrl.create_tag(
                meta_data=tag_meta,
                container=self
            )
            self._tags.append(tag)

            if tag.is_safe():
                self._safety_tags.append(tag)
            else:
                self._standard_tags.append(tag)

    def compile_instructions(self) -> None:
        """Compile instructions from routines in this AOI.

        Overrides HasInstructions.compile_instructions to aggregate instructions
        from all routines in the AOI.
        """
        self._instructions.clear()
        self._input_instructions.clear()
        self._output_instructions.clear()

        for routine in self.routines:
            self._instructions.extend(routine.get_instructions())
            self._input_instructions.extend(routine.get_input_instructions())
            self._output_instructions.extend(routine.get_output_instructions())

    def block_routine(
        self,
        routine_name: str,
        blocking_bit: str
    ) -> None:
        """Block a routine in this AOI.

        Args:
            routine_name: Name of the routine to block
            blocking_bit: Tag name of the bit to use for blocking
        """
        raise NotImplementedError("block_routine is not yet implemented for AOIs")

    def unblock_routine(
        self,
        routine_name: str,
        blocking_bit: str
    ) -> None:
        """Unblock a routine in this AOI.

        Args:
            routine_name: Name of the routine to unblock
            blocking_bit: Tag name of the bit to use for blocking
        """
        raise NotImplementedError("unblock_routine is not yet implemented for AOIs")

    def get_main_routine(self):
        """Get the main routine of this AOI.

        For AOIs, the Logic routine is typically the main routine.

        Returns:
            The Logic routine if found, otherwise the first routine, or None
        """
        if 'Logic' in self.routines:
            return self.routines['Logic']
        if len(self.routines) > 0:
            return self.routines[0]
        return None

    def get_revision(self) -> str:
        """get the full revision string for this AOI

        Returns:
            :class:`str`: full revision string
        """
        return self['@Revision']

    def set_revision(self, revision: str) -> None:
        """set the full revision string for this AOI

        Args:
            revision (str): revision string
        """
        if not self.is_valid_revision_string(revision):
            raise self.InvalidNamingException
        self['@Revision'] = revision
