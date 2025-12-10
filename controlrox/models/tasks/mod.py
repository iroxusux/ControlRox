"""PLC Controller Modifaction Schema."""
from typing import (
    Optional,
)
from pyrox.services import log
from controlrox.interfaces import (
    IController,
    IRoutine,
    IRung,
    ITag,
    TAG
)
from controlrox.services import ControllerInstanceManager


class ControllerModificationSchema:
    """
    Defines a schema for modifying a controller, such as migrating assets between controllers,
    or importing assets from an L5X dictionary.
    """

    def __init__(
        self
    ) -> None:
        self.source = None

        self._destination = ControllerInstanceManager.get_controller()

        self.actions: list[dict] = []  # List of migration actions

    @property
    def destination(self) -> IController:
        if not self._destination:
            raise ValueError("Destination controller is not set for this ControllerModificationSchema.")
        return self._destination

    def _execute_add_controller_tag(
        self,
        action: dict
    ) -> None:
        tag_data = action.get('asset')
        if not tag_data:
            log(self).warning('No tag data provided for add_controller_tag action.')
            return

        tag = self.destination.create_tag(
            meta_data=tag_data,
            container=self.destination
        )

        try:
            self.destination.add_tag(tag)
            log(self).info(f'Added tag {tag.name} to destination controller.')
        except ValueError as e:
            log(self).warning(f'Failed to add tag {tag.name}:\n{e}')

    def _execute_add_datatype(
        self,
        action: dict
    ) -> None:
        datatype_data = action.get('asset')
        if not datatype_data:
            log(self).warning('No datatype data provided for add_datatype action.')
            return

        datatype = self.destination.create_datatype(meta_data=datatype_data)

        try:
            self.destination.add_datatype(datatype)
            log(self).info(f'Added datatype {datatype.name} to destination controller.')
        except ValueError as e:
            log(self).warning(f'Failed to add datatype {datatype.name}:\n{e}')

    def _execute_add_program_tag(
        self,
        action: dict
    ) -> None:
        program_name = action.get('program')
        tag_data = action.get('asset')
        if not program_name or not tag_data:
            log(self).warning('Program name or tag data missing for add_program_tag action.')
            return

        program = self.destination.programs.get(program_name)
        if not program:
            log(self).warning(f'Program {program_name} not found in destination controller.')
            return

        tag = self.destination.create_tag(
            meta_data=tag_data,
            container=program
        )

        try:
            program.add_tag(tag)
            log(self).info(f'Added tag {tag.name} to program {program_name}.')
        except ValueError as e:
            log(self).warning(f'Failed to add tag {tag.name} to program {program_name}:\n{e}')

    def _execute_add_routine(
        self,
        action: dict
    ) -> None:
        program_name = action.get('program')
        routine_data = action.get('routine')
        if not program_name or not routine_data:
            log(self).warning('Program name or routine data missing for add_routine action.')
            return

        program = self.destination.programs.get(program_name)
        if not program:
            log(self).warning(f'Program {program_name} not found in destination controller.')
            return

        routine = self.destination.create_routine(
            meta_data=routine_data,
            container=program
        )

        try:
            program.add_routine(routine)
            log(self).info(f'Added routine {routine.name} to program {program_name}.')
        except ValueError as e:
            log(self).warning(f'Failed to add routine {routine.name} to program {program_name}:\n{e}')

    def _execute_add_rung(
        self,
        action: dict
    ) -> None:
        program_name = action.get('program')
        routine_name = action.get('routine')
        rung_data = action.get('new_rung')
        rung_number = action.get('rung_number', -1)
        if not program_name or not routine_name or not rung_data:
            log(self).warning('Program name, routine name, or rung data missing for add_rung action.')
            return

        program = self.destination.programs.get(program_name)
        if not program:
            log(self).warning(f'Program {program_name} not found in destination controller.')
            return

        routine = program.routines.get(routine_name)
        if not routine:
            log(self).warning(f'Routine {routine_name} not found in program {program_name}.')
            return

        rung = self.destination.create_rung(
            meta_data=rung_data,
            routine=routine,
            rung_number=rung_number
        )

        try:
            routine.add_rung(rung)
            log(self).info(f'Added rung {rung.number} to routine {routine_name} in program {program_name}.')
        except ValueError as e:
            log(self).warning(f'Failed to add rung {rung.number} to routine {routine_name} in program {program_name}:\n{e}')

    def _execute_add_safety_tag_mapping(
        self,
        action: dict
    ) -> None:
        std_tag = action.get('standard')
        sfty_tag = action.get('safety')
        if not std_tag or not sfty_tag:
            log(self).warning('Standard or safety tag missing for add_safety_tag_mapping action.')
            return

        try:
            self.destination.safety_info.add_safety_tag_mapping(std_tag, sfty_tag)
            log(self).info(f'Added safety tag mapping: {std_tag} -> {sfty_tag}')
        except ValueError as e:
            log(self).warning(f'Failed to add safety tag mapping {std_tag} -> {sfty_tag}:\n{e}')

    def _execute_controller_tag_migration(
        self,
        action: dict
    ) -> None:
        if not self.source:
            log(self).warning('No source controller defined for tag migration.')
            return

        tag_name = action.get('name')
        tag = self.source.tags.get(tag_name)
        if not tag:
            log(self).warning(f'Tag {tag_name} not found in source controller.')
            return

        try:
            self.destination.add_tag(tag)
            log(self).info(f'Migrated tag {tag_name} to destination controller.')
        except ValueError as e:
            log(self).warning(f'Failed to migrate tag {tag_name}:\n{e}')

    def _execute_datatype_migration(
        self,
        action: dict
    ) -> None:
        if not self.source:
            log(self).warning('No source controller defined for datatype migration.')
            return

        datatype_name = action.get('name')
        datatype = self.source.datatypes.get(datatype_name)
        if not datatype:
            log(self).warning(f'Datatype {datatype_name} not found in source controller.')
            return

        try:
            self.destination.add_datatype(datatype)
            log(self).info(f'Migrated datatype {datatype_name} to destination controller.')
        except ValueError as e:
            log(self).warning(f'Failed to migrate datatype {datatype_name}:\n{e}')

    def _execute_import_assets_from_file(
        self,
        action: dict
    ) -> None:
        file_location = action.get('file')
        asset_types = action.get('asset_types')
        if not file_location:
            log(self).warning('No file location provided for import_datatypes_from_file action.')
            return

        try:
            self.destination.import_assets_from_file(file_location, asset_types)
            log(self).info(f'Imported assets from file {file_location} to destination controller.')
        except Exception as e:
            log(self).warning(f'Failed to import assets from file {file_location}:\n{e}')
            raise e

    def _execute_remove_controller_tag(
        self,
        action: dict
    ) -> None:
        tag_name = action.get('name')
        tag = self.destination.tags.get(tag_name)
        if not tag:
            log(self).warning(f'Tag {tag_name} not found in destination controller.')
            return

        self.destination.remove_tag(tag)
        log(self).info(f'Removed tag {tag_name} from destination controller.')

    def _execute_remove_datatype(
        self,
        action: dict
    ) -> None:
        datatype_name = action.get('name')
        datatype = self.destination.datatypes.get(datatype_name)
        if not datatype:
            log(self).warning(f'Datatype {datatype_name} not found in destination controller.')
            return

        self.destination.remove_datatype(datatype)
        log(self).info(f'Removed datatype {datatype_name} from destination controller.')

    def _execute_remove_program_tag(
        self,
        action: dict
    ) -> None:
        program_name = action.get('program')
        tag_name = action.get('name')

        program = self.destination.programs.get(program_name)
        if not program:
            log(self).warning(f'Program {program_name} not found in destination controller.')
            return

        tag = program.tags.get(tag_name)
        if not tag:
            log(self).warning(f'Tag {tag_name} not found in program {program_name}.')
            return

        program.remove_tag(tag)
        log(self).info(f'Removed tag {tag_name} from program {program_name}.')

    def _execute_remove_routine(
        self,
        action: dict
    ) -> None:
        program_name = action.get('program')
        routine_name = action.get('name')

        if not program_name or not routine_name:
            log(self).warning('Program name or routine name missing for remove_routine action.')
            return

        program = self.destination.programs.get(program_name)
        if not program:
            log(self).warning(f'Program {program_name} not found in destination controller.')
            return

        routine = program.routines.get(routine_name)
        if not routine:
            log(self).warning(f'Routine {routine_name} not found in program {program_name}.')
            return

        program.remove_routine(routine)
        log(self).info(f'Removed routine {routine_name} from program {program_name}.')
        log(self).debug('Searching for JSR instructions to %s...', routine_name)
        jsr = program.get_instructions('JSR', routine_name)
        if jsr:
            for op in jsr:
                rung = op.rung
                if not rung:
                    raise ValueError('JSR instruction has no parent rung!')
                jsr_routine = program.routines.get(rung.routine.name)
                if not jsr_routine:
                    raise ValueError('Rung has no parent routine!')
                log(self).debug('Found JSR in rung %s of routine %s. Removing rung...', rung.number, jsr_routine.name)
                jsr_routine.remove_rung(rung)

    def _execute_remove_safety_tag_mapping(
        self,
        action: dict
    ) -> None:
        std_tag = action.get('standard')
        sfty_tag = action.get('safety')
        if not std_tag or not sfty_tag:
            log(self).warning('Standard or safety tag missing for remove_safety_tag_mapping action.')
            return

        log(self).debug(f'Removing safety tag mapping: {std_tag} -> {sfty_tag}')
        self.destination.safety_info.remove_safety_tag_mapping(std_tag, sfty_tag)

    def _execute_routine_migration(
        self,
        action: dict
    ) -> None:
        if self.source is None:
            log(self).warning('No source controller defined for routine migration.')
            return

        source_program_name = action.get('source_program')
        destination_program_name = action.get('destination_program')
        routine_name = action.get('routine')
        rung_updates = action.get('rung_updates', {})

        source_program = self.source.programs.get(source_program_name)
        if not source_program:
            log(self).warning(f'Program {source_program_name} not found in source controller.')
            return

        source_routine = source_program.routines.get(routine_name)
        if not source_routine:
            log(self).warning(f'Routine {routine_name} not found in program {source_program_name}.')
            return

        destination_program = self.destination.programs.get(destination_program_name)
        if not destination_program:
            log(self).warning(f'Program {destination_program_name} not found in destination controller.')
            return

        destination_program.add_routine(source_routine)
        log(self).info(f'Migrated routine {routine_name} from program {source_program_name} to program {destination_program_name}.')

        dest_prog = self.destination.programs.get(destination_program_name)
        if not dest_prog:
            log(self).warning(f'Program {destination_program_name} not found in destination controller.')
            return

        dest_routine = dest_prog.routines.get(routine_name)
        if not dest_routine:
            log(self).warning(f'Routine {routine_name} not found in program {destination_program_name}.')
            return

        for rung_num, new_rung in rung_updates.items():
            dest_routine.rungs[rung_num] = new_rung
            log(self).info(f'Updated rung {rung_num} in routine {routine_name} of program {destination_program_name}.')

    def _safe_register_action(
        self,
        action: dict
    ) -> None:
        if action not in self.actions:
            self.actions.append(action)
        else:
            log(self).debug('Action already registered, skipping duplicate.')

    def add_controller_tag(
        self,
        tag: TAG
    ) -> TAG:
        """Add an individual tag to import directly to the destination controller.

        Args:
            tag (Tag): The tag to add.

        Raises:
            ValueError: If the provided tag is not an instance of the Tag class.
        """
        if not isinstance(tag, ITag):
            raise ValueError('Tag must be an instance of Tag class.')

        self._safe_register_action({
            'type': 'add_controller_tag',
            'asset': tag.meta_data,
            'method': self._execute_add_controller_tag
        })

        return tag

    def add_controller_tag_migration(
        self,
        tag_name: str
    ) -> None:
        """Specify a tag to migrate from source to destination.

        Args:
            tag_name (str): The name of the tag to migrate.
        """
        self._safe_register_action({
            'type': 'migrate_controller_tag',
            'name': tag_name,
            'method': self._execute_controller_tag_migration
        })

    def add_datatype_migration(
        self,
        datatype_name: str
    ) -> None:
        """Specify a datatype to migrate from source to destination.

        Args:
            datatype_name (str): The name of the datatype to migrate.
        """
        self._safe_register_action({
            'type': 'migrate_datatype',
            'name': datatype_name,
            'method': self._execute_datatype_migration
        })

    def add_program_tag(
        self,
        program_name: str,
        tag: TAG
    ) -> TAG:
        """Add a tag to import directly to the destination controller within a specific program.

        Args:
            program_name (str): The name of the program to add the tag to.
            tag (Tag): The tag to add.

        Raises:
            ValueError: If the provided tag is not an instance of the Tag class.
        """
        if not isinstance(tag, ITag):
            raise ValueError('Tag must be an instance of Tag class.')

        self._safe_register_action({
            'type': 'add_program_tag',
            'program': program_name,
            'asset': tag.meta_data,
            'method': self._execute_add_program_tag
        })

        return tag

    def add_routine(
        self,
        program_name: str,
        routine: IRoutine
    ) -> IRoutine:
        """Add a routine to import directly to the destination controller.

        Args:
            program_name (str): The name of the program to add the routine to.
            routine (Routine): The routine to add.

        Raises:
            ValueError: If the provided routine is not an instance of the Routine class.
        """
        if not isinstance(routine, IRoutine):
            raise ValueError('Routine must be an instance of Routine class.')

        self._safe_register_action({
            'type': 'add_routine',
            'program': program_name,
            'routine': routine.meta_data,
            'method': self._execute_add_routine
        })

        return routine

    def add_routine_migration(
        self,
        source_program_name: str,
        routine_name: str,
        destination_program_name: str = '',
        rung_updates: Optional[dict] = None
    ) -> None:
        """Specify a routine to migrate, with optional rung updates.

        Args:
            source_program_name (str): The name of the program containing the routine from the source controller.
            routine_name (str): The name of the routine to migrate.
            destination_program_name (str, optional): The name of the program to add the routine to in the destination controller.
                                                        \n\tIf None, uses the same program name as the source.
            rung_updates (dict, optional): A dictionary of rung updates to apply during migration.
        """
        self._safe_register_action({
            'type': 'migrate_routine',
            'source_program': source_program_name,
            'routine': routine_name,
            'destination_program': destination_program_name or source_program_name,
            'rung_updates': rung_updates or {},
            'method': self._execute_routine_migration
        })

    def add_rung(
        self,
        program_name: str,
        routine_name: str,
        rung: IRung,
        rung_number: Optional[int] = None
    ) -> IRung:
        """Add a rung to import directly to the destination controller.

        Args:
            program_name (str): The name of the program containing the routine.
            routine_name (str): The name of the routine to add the rung to.
            new_rung (Rung): The rung to add.
            rung_number (Optional[int]): The index at which to insert the new rung. If None, appends to the end.

        Raises:
            ValueError: If the provided rung is not an instance of the Rung class.
        """
        if not isinstance(rung, IRung):
            raise ValueError('Rung must be an instance of Rung class.')

        if not rung.meta_data:
            raise ValueError('Rung meta_data cannot be None or empty.')

        self._safe_register_action({
            'type': 'add_rung',
            'program': program_name,
            'routine': routine_name,
            'rung_number': rung_number,
            'new_rung': rung.meta_data,
            'method': self._execute_add_rung
        })

        return rung

    def add_import_from_file(
        self,
        file_location: str,
        asset_types: Optional[list[str]]
    ) -> None:
        """
        Add actions to import assets from an L5X file.

        Args:
            file_location (str): The path to the L5X file.
            asset_types (list[str], optional): List of asset types to import, e.g. ['DataTypes', 'Tags', 'Programs'].
                                                \n\tDefaults to all if None.

        Raises:
            ValueError: If no valid L5X data is found in the specified file.
        """

        self._safe_register_action({
            'type': 'import_from_file',
            'file': file_location,
            'asset_types': asset_types,
            'method': self._execute_import_assets_from_file
        })

    def add_safety_tag_mapping(
        self,
        std_tag: str,
        sfty_tag: str
    ) -> None:
        """Add a mapping for tags from standard to safety code space.

        Args:
            std_tag (str): The standard tag name.
            sfty_tag (str): The safety tag name.

        Raises:
            ValueError: If either tag name is not a string.
        """
        if not isinstance(std_tag, str) or not isinstance(sfty_tag, str):
            raise ValueError('Source and destination tags must be strings.')
        self._safe_register_action({
            'type': 'safety_tag_mapping',
            'standard': std_tag,
            'safety': sfty_tag,
            'method': self._execute_add_safety_tag_mapping
        })

    def remove_controller_tag(
        self,
        tag_name: str
    ) -> None:
        """Specify a tag to remove from the destination controller.

        Args:
            tag_name (str): The name of the tag to remove.
        """
        self._safe_register_action({
            'type': 'remove_controller_tag',
            'name': tag_name,
            'method': self._execute_remove_controller_tag
        })

    def remove_datatype(
        self,
        datatype_name: str
    ) -> None:
        """Specify a datatype to remove from the destination controller.

        Args:
            datatype_name (str): The name of the datatype to remove.
        """
        self._safe_register_action({
            'type': 'remove_datatype',
            'name': datatype_name,
            'method': self._execute_remove_datatype
        })

    def remove_program_tag(
        self,
        program_name: str,
        tag_name: str
    ) -> None:
        """Specify a tag to remove from a specific program in the destination controller.

        Args:
            program_name (str): The name of the program containing the tag.
            tag_name (str): The name of the tag to remove.
        """
        self._safe_register_action({
            'type': 'remove_program_tag',
            'program': program_name,
            'name': tag_name,
            'method': self._execute_remove_program_tag
        })

    def remove_routine(
        self,
        program_name: str,
        routine_name: str
    ) -> None:
        """Specify a routine to remove from a specific program in the destination controller.

        Args:
            program_name (str): The name of the program containing the routine.
            routine_name (str): The name of the routine to remove.
        """
        self._safe_register_action({
            'type': 'remove_routine',
            'program': program_name,
            'name': routine_name,
            'method': self._execute_remove_routine
        })

    def remove_safety_tag_mapping(
        self,
        std_tag: str,
        sfty_tag: str
    ) -> None:
        """Specify a safety tag mapping to remove from the destination controller.

        Args:
            std_tag (str): The standard tag name.
            sfty_tag (str): The safety tag name.
        """
        self._safe_register_action({
            'type': 'remove_safety_tag_mapping',
            'standard': std_tag,
            'safety': sfty_tag,
            'method': self._execute_remove_safety_tag_mapping
        })

    def execute(self):
        """Perform all migration and import actions."""
        log(self).info('Executing controller modification schema...')

        if not self.destination:
            raise ValueError('Destination controller is not set.')

        # call all action's methods
        for action in self.actions:
            method = action.get('method')
            if callable(method):
                method(action)
            else:
                log(self).warning(f"No method defined for action type: {action['type']}. Skipping...")

        # Compile after all imports
        self.destination.compile()


__all__ = [
    'ControllerModificationSchema',
]
