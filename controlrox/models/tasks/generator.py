"""Emulation Generator module for pyrox applications.
"""
from typing import Optional

from controlrox.interfaces import (
    IEmulationGenerator,
    IModule,
    IRoutine,
    IRung,
    ITag,
    ModuleControlsType,
)
from controlrox.interfaces import IController
from controlrox.models.plc.controller import Controller
from controlrox.models.tasks.mod import ControllerModificationSchema
from controlrox.services import ControllerInstanceManager
from controlrox.services.tasks.generator import EmulationGeneratorFactory
from controlrox.services.plc.introspective import IntrospectiveModuleWarehouseFactory
from pyrox.models import FactoryTypeMeta
from pyrox.services.logging import log

from controlrox.models.plc.meta import PlcObject


class EmulationGenerator(
    IEmulationGenerator,
    PlcObject,
    metaclass=FactoryTypeMeta[
        'EmulationGenerator',
        EmulationGeneratorFactory
    ]
):
    """Base class for emulation logic generators."""
    supporting_class: Optional[type] = None
    supports_registering: bool = False

    def __init__(
        self,
        controller: Controller
    ) -> None:
        super().__init__(controller=controller)
        self.schema = ControllerModificationSchema(
            source=None,
            destination=self.controller
        )
        self._emulation_standard_routine = None
        self._emulation_safety_routine = None

    def __init_subclass__(cls, **kwargs):
        cls.supports_registering = True
        return super().__init_subclass__(**kwargs)

    @property
    def controller(self) -> IController:
        if not self._controller:
            raise ValueError("Controller is not set for this EmulationGenerator.")
        return self._controller

    @controller.setter
    def controller(self, controller: Optional[IController]) -> None:
        self._controller = controller

    @classmethod
    def get_factory(cls):
        return EmulationGeneratorFactory

    def _add_rung_common(
        self,
        rung: IRung,
        program_name: str,
        routine_name: str
    ) -> None:
        """Helper to add a rung to a specified routine.

        Args:
            rung: The rung to add
            program_name: Name of the program
            routine_name: Name of the routine
        """
        self.schema.add_rung(
            program_name=program_name,
            routine_name=routine_name,
            rung=rung
        )

    def _get_active_controller(self) -> None:
        """Helper to ensure the controller is set."""
        if not self._controller:
            ctrl = ControllerInstanceManager.get_controller()
            if not ctrl:
                raise ValueError("No active controller found for emulation generation.")
            self._controller = ctrl

    def add_l5x_imports(
        self,
        imports: list[tuple[str, list[str]]]
    ) -> None:
        """Helper to schedule imports in the modification schema.

        Args:
            imports: list of tuples (file_location, [asset_types])
        """
        for file_location, asset_types in imports:
            log(self).debug(f"Scheduling import of {asset_types} from {file_location}")
            self.schema.add_import_from_file(
                file_location=file_location,
                asset_types=asset_types
            )

    def add_program_tag(
        self,
        program_name: str,
        tag_name: str,
        datatype: str,
        **kwargs
    ) -> ITag:
        """Helper method to add a tag to a program.

        Args:
            program_name: Name of the program
            tag_name: Name of the tag
            datatype: Datatype of the tag
            **kwargs: Additional tag properties

        Returns:
            Tag: The created tag
        """
        log(self).debug(f"Adding program tag: {tag_name} with datatype {datatype} to program {program_name}")
        return self.schema.add_program_tag(
            program_name=program_name,
            tag=self.controller.create_tag(
                name=tag_name,
                **kwargs
            ))

    def add_controller_tag(
        self,
        tag_name: str,
        datatype: str,
        description: str = "",
        constant: bool = False,
        external_access: str = "Read/Write",
        tag_class: str = 'Standard',
        tag_type: str = 'Base',
        **kwargs
    ) -> ITag:
        """Helper method to add a controller-scoped tag.

        Args:
            tag_name: Name of the tag
            datatype: Datatype of the tag
            **kwargs: Additional tag properties

        Returns:
            Tag: The created tag
        """
        log(self).debug(f"Scheduling controller tag: {tag_name} with datatype {datatype}.")
        return self.schema.add_controller_tag(
            self.controller.create_tag(
                name=tag_name,
                description=description,
                datatype=datatype,
                constant=constant,
                external_access=external_access,
                tag_type=tag_type,
                tag_class=tag_class,
                **kwargs
            ))

    def add_controller_tags(
        self,
        tags: list[dict]
    ) -> None:
        """Helper method to add multiple controller-scoped tags.

        Args:
            tags: list of tag dictionaries with keys matching Tag properties
        """
        for tag_info in tags:
            self.add_controller_tag(**tag_info)

    def add_routine(
        self,
        program_name: str,
        routine_name: str,
        routine_description: str,
        call_from_main: bool = True,
        rung_position: int = -1
    ) -> IRoutine:
        """Helper method to add an emulation routine to a program.

        Args:
            program_name: Name of the program to add routine to
            routine_name: Name of the new routine
            routine_description: Description for the routine
            call_from_main: Whether to add JSR call from main routine
            rung_position: Position to insert JSR call (-1 for end)

        Returns:
            Routine: The created routine
        """
        log(self).debug(f"Adding emulation routine '{routine_name}' to program '{program_name}' to schema.")
        # Create the routine
        rout: IRoutine = self.controller.create_routine()
        rout.set_name(routine_name)
        rout.set_description(routine_description)
        rout.clear_rungs()

        # Add routine to program
        self.schema.add_routine(
            program_name=program_name,
            routine=rout
        )

        # Add JSR call if requested
        if call_from_main:
            program = self.controller.programs.get(program_name)
            if not program:
                return rout
            main_routine = program.get_main_routine()
            if not main_routine:
                return rout

            if main_routine.check_for_jsr(routine_name):
                log(self).debug(f"JSR to '{routine_name}' already exists in main routine of program '{program_name}'")
            else:
                log(self).debug(f"Adding JSR call to '{routine_name}' in main routine of program '{program_name}'")
                jsr_rung = self.controller.create_rung(
                    rung_text=f'JSR({routine_name},0);',
                    comment=f'Call the {routine_name} routine.'
                )
                self.schema.add_rung(
                    program_name=program_name,
                    routine_name=main_routine.name,
                    rung_number=rung_position,
                    rung=jsr_rung
                )

        return rout

    def add_rung(
        self,
        program_name: str,
        routine_name: str,
        new_rung: IRung,
        rung_number: Optional[int] = None
    ) -> IRung:
        """Helper method to add a rung to a routine.

        Args:
            program_name: Name of the program
            routine_name: Name of the routine
            new_rung: The rung to add
            rung_number: Position to insert the rung (-1 for end)
        """
        log(self).debug(
            f"Adding rung to routine '{routine_name}' in program '{program_name}' at rung {rung_number if rung_number is not None else 'end'}"
        )
        return self.schema.add_rung(
            program_name=program_name,
            routine_name=routine_name,
            rung_number=rung_number,
            rung=new_rung
        )

    def add_rung_to_safety_routine(self, rung: IRung) -> None:
        """Helper to add a rung to the safety emulation routine."""
        if not self.emulation_safety_routine:
            raise ValueError("Safety emulation routine has not been created yet.")
        self._add_rung_common(
            rung=rung,
            program_name=self.emulation_safety_program_name,
            routine_name=self.get_emulation_safety_routine_name()
        )

    def add_rung_to_standard_routine(self, rung: IRung) -> None:
        """Helper to add a rung to the standard emulation routine."""
        if not self.emulation_standard_routine:
            raise ValueError("Emulation routine has not been created yet.")
        self._add_rung_common(
            rung=rung,
            program_name=self.emulation_standard_program_name,
            routine_name=self.get_emulation_standard_routine_name()
        )

    def add_rungs(
        self,
        program_name: str,
        routine_name: str,
        new_rungs: list[IRung],
        rung_number: Optional[int] = None
    ) -> None:
        """Helper method to add multiple rungs to a routine.

        Args:
            program_name: Name of the program
            routine_name: Name of the routine
            new_rungs: list of rungs to add
            rung_number: Position to insert the first rung (-1 for end)
        """
        for i, r in enumerate(new_rungs):
            position = rung_number + i if rung_number is not None and rung_number >= 0 else -1
            self.add_rung(
                program_name=program_name,
                routine_name=routine_name,
                new_rung=r,
                rung_number=position
            )

    def add_safety_tag_mapping(
        self,
        standard_tag: str,
        safety_tag: str,
    ) -> None:
        """Helper method to add a safety tag mapping.

        Args:
            standard_tag: Name of the standard tag
            safety_tag: Name of the safety tag
        """
        if not standard_tag or not safety_tag:
            return
        self.schema.add_safety_tag_mapping(
            std_tag=standard_tag,
            sfty_tag=safety_tag
        )

    def block_routine_jsr(
        self,
        program_name: str,
        routine_name: str
    ) -> None:
        """Helper method to block a JSR call to a routine.

        Args:
            program_name: Name of the program
            routine_name: Name of the routine
        """
        log(self).debug(f"Blocking JSR call to routine '{routine_name}' in program '{program_name}'")
        ...

    def generate_emulation_logic(self) -> ControllerModificationSchema:
        """Main entry point to generate emulation logic.

        Returns:
            ControllerModificationSchema: The modification schema with all changes.
        """
        log(self).info(f"Starting emulation generation for {self.controller.name}")
        self._get_active_controller()
        self._generate_base_emulation()
        self._generate_custom_module_emulation()
        self._generate_custom_logic()

        self.schema.execute()
        log(self).info(f"Emulation generation completed for {self.controller.name}")
        return self.schema

    def _generate_base_emulation(self) -> None:
        """Generate the base emulation logic common to all controllers."""
        self._generate_base_tags()
        self._generate_custom_tags()

        self._generate_base_standard_routine()
        self._generate_base_standard_rungs()

        self._generate_base_safety_routine()
        self._generate_base_safety_rungs()

        self._generate_base_module_emulation()

        self._generate_custom_standard_routines()
        self._generate_custom_standard_rungs()
        self._generate_custom_safety_routines()
        self._generate_custom_safety_rungs()

    def _generate_base_tags(self) -> None:
        """Generate base tags common to all controllers."""
        log(self).info("Generating base tags...")
        for tag_name, datatype, description in self.base_tags:
            self.add_controller_tag(
                tag_name,
                datatype,
                description=description
            )

    def _generate_custom_tags(self) -> None:
        """Generate custom tags. Override in subclasses if needed."""
        log(self).info("Generating custom tags...")
        for tag_name, datatype, description, dimensions in self.custom_tags:
            self.add_controller_tag(
                tag_name,
                datatype,
                description=description,
                dimensions=dimensions
            )

    def _generate_base_standard_routine(self) -> None:
        """Generate a standard base routine common to all controllers."""
        log(self).info("Generating base standard routine...")
        self.set_emulation_standard_routine(
            self.add_routine(
                program_name=self.emulation_standard_program_name,
                routine_name=self.get_emulation_standard_routine_name(),
                routine_description=self.get_emulation_standard_routine_description(),
                call_from_main=True,
                rung_position=0
            )
        )

    def _generate_base_standard_rungs(self) -> None:
        """Generate base rungs in the standard emulation routine."""
        log(self).info("Generating base standard rungs...")
        if not self.emulation_standard_routine:
            raise ValueError("Emulation routine has not been created yet.")

        self.emulation_standard_routine.clear_rungs()
        self.add_rung_to_standard_routine(
            self.controller.create_rung(
                rung_text='NOP();',
                comment='// Emulation Logic Routine\n// Auto-generated\n// Do not modify.'
            ))

        # Setup Rung
        branch1 = f'XIC(S:FS)OTL({self.toggle_inhibit_tag})OTL({self.test_mode_tag})'
        branch2 = f'MOVE(0,{self.uninhibit_tag})MOVE(4,{self.inhibit_tag})'
        self.add_rung_to_standard_routine(
            self.controller.create_rung(
                rung_text=f'[{branch1},{branch2}];',
                comment='// This routine is auto-generated.\n// Do not modify.'
            ))

        # Inhibit Logic Rung
        branch1 = f'XIO({self.toggle_inhibit_tag})MOVE({self.uninhibit_tag},{self.local_mode_tag})'
        branch2 = f'XIC({self.toggle_inhibit_tag})MOVE({self.inhibit_tag},{self.local_mode_tag})'
        self.add_rung_to_standard_routine(
            self.controller.create_rung(
                rung_text=f'[{branch1},{branch2}];',
                comment='// Handle toggle inhibit.'
            ))

        self._generate_module_inhibit_rungs()

    def _generate_base_safety_routine(self) -> None:
        """Generate a safety routine common to all controllers."""
        log(self).debug("Generating base safety routine...")
        self.set_emulation_safety_routine(
            self.add_routine(
                program_name=self.emulation_safety_program_name,
                routine_name=self.get_emulation_safety_routine_name(),
                routine_description=self.get_emulation_safety_routine_description(),
                call_from_main=True,
                rung_position=0
            )
        )

    def _generate_base_safety_rungs(self) -> None:
        """Generate base rungs in the safety emulation routine."""
        log(self).info("Generating base safety rungs...")
        if not self.emulation_safety_routine:
            raise ValueError("Safety emulation routine has not been created yet.")

        self.emulation_safety_routine.clear_rungs()
        self.add_rung_to_safety_routine(
            self.controller.create_rung(
                rung_text='NOP();',
                comment='// Emulation Safety Logic Routine\n// Auto-generated\n// Do not modify.'
            )
        )

    def _generate_base_module_emulation(self) -> None:
        """Generate base module emulation logic common to all controllers."""
        log(self).info("Generating base module emulation...")
        for controller_type in ModuleControlsType:
            self._generate_builtin_common(controller_type)

    def _generate_builtin_common(
        self,
        generation_type: ModuleControlsType
    ) -> None:
        imodules = IntrospectiveModuleWarehouseFactory.filter_modules_by_type(
            self.controller.modules,
            generation_type
        )
        log(self).info(
            "Generating built-in common emulation for %d modules of type %s...",
            len(imodules),
            generation_type.value
        )

        for introspective_module in imodules:
            if not introspective_module:
                log(self).warning("Module has no introspective_module, skipping...")
                continue
            if not introspective_module.base_module:
                log(self).warning("IntrospectiveModule has no associated module, skipping...")
                continue
            log(self).info(
                "Generating emulation for %s %s of class %s",
                generation_type.value,
                introspective_module.base_module.name,
                introspective_module.__class__.__name__
            )

            self.add_l5x_imports(introspective_module.get_required_imports())
            self.add_controller_tags(introspective_module.get_required_tags())
            self.add_safety_tag_mapping(*introspective_module.get_required_standard_to_safety_mapping())
            self.add_rungs(
                self.emulation_standard_program_name,
                self.get_emulation_standard_routine_name(),
                introspective_module.get_required_standard_rungs()
            )
            self.add_rungs(
                self.emulation_safety_program_name,
                self.get_emulation_safety_routine_name(),
                introspective_module.get_required_safety_rungs()
            )

    def _generate_custom_logic(self) -> None:
        """Generate custom emulation logic. Override in subclasses if needed."""
        pass

    def _generate_custom_module_emulation(self) -> None:
        """Generate module-specific emulation logic."""
        pass

    def _generate_custom_safety_routines(self) -> None:
        """Generate custom safety routines. Override in subclasses if needed."""
        pass

    def _generate_custom_safety_rungs(self) -> None:
        """Generate custom safety rungs. Override in subclasses if needed."""
        pass

    def _generate_custom_standard_routines(self) -> None:
        """Generate custom standard routines. Override in subclasses if needed."""
        pass

    def _generate_custom_standard_rungs(self) -> None:
        """Generate custom standard rungs. Override in subclasses if needed."""
        pass

    def _generate_module_inhibit_rungs(self) -> None:
        """Generate inhibit logic for modules."""
        if not self.emulation_standard_routine:
            raise ValueError("Emulation routine has not been created yet.")

        log(self).info("Generating module inhibit rungs...")

        for mod in self.controller.modules:
            if mod.name == 'Local':
                continue
            self.add_rung_to_standard_routine(
                self.controller.create_rung(
                    rung_text=f'SSV(Module,{mod.name},Mode,{self.local_mode_tag});',
                    comment=f'// Inhibit logic for module {mod.name}'
                ))

    def get_base_tags(self) -> list[tuple[str, str, str]]:
        raise NotImplementedError("Subclasses must implement get_base_tags")

    def get_custom_tags(self) -> list[tuple[str, str, str, Optional[str]]]:
        raise NotImplementedError("Subclasses must implement get_custom_tags")

    def get_emulation_safety_program_name(self) -> str:
        raise NotImplementedError("Subclasses must implement get_emulation_safety_program_name")

    def get_emulation_safety_routine(self) -> Optional[IRoutine]:
        return self._emulation_safety_routine

    def get_emulation_safety_routine_name(self) -> str:
        raise NotImplementedError("Subclasses must implement get_emulation_safety_routine_name")

    def get_emulation_safety_routine_description(self) -> str:
        return "Emulation Safety Logic Routine"

    def get_emulation_standard_program_name(self) -> str:
        raise NotImplementedError("Subclasses must implement get_emulation_standard_program_name")

    def get_emulation_standard_routine(self) -> Optional[IRoutine]:
        return self._emulation_standard_routine

    def get_emulation_standard_routine_name(self) -> str:
        raise NotImplementedError("Subclasses must implement get_emulation_standard_routine_name")

    def get_emulation_standard_routine_description(self) -> str:
        return "Emulation Logic Routine"

    def get_inhibit_tag(self) -> str:
        raise NotImplementedError("Subclasses must implement get_inhibit_tag")

    def get_local_mode_tag(self) -> str:
        raise NotImplementedError("Subclasses must implement get_local_mode_tag")

    def get_test_mode_tag(self) -> str:
        raise NotImplementedError("Subclasses must implement get_test_mode_tag")

    def get_toggle_inhibit_tag(self) -> str:
        raise NotImplementedError("Subclasses must implement get_toggle_inhibit_tag")

    def get_uninhibit_tag(self) -> str:
        raise NotImplementedError("Subclasses must implement get_uninhibit_tag")

    def get_modules_by_type(self, module_type: str) -> list[IModule]:
        """Get all modules of a specific type.

        Args:
            module_type: The module type to filter by

        Returns:
            list[Module]: list of matching modules
        """
        mods = []
        for module in self.controller.modules:
            imodule = IntrospectiveModuleWarehouseFactory.get_imodule_from_meta_data(module, True)
            if not imodule:
                continue
            if imodule.module_controls_type == module_type:
                mods.append(module)

        log(self).info('Found %d modules of type %s...', len(mods), module_type)
        return mods

    def get_modules_by_description_pattern(self, pattern: str) -> list[IModule]:
        """Get modules matching a description pattern.

        Args:
            pattern: Pattern to match in module description

        Returns:
            list[Module]: list of matching modules
        """
        mods = [m for m in self.controller.modules if m.description and pattern in m.description]
        log(self).info('Found %d modules matching description pattern "%s"...', len(mods), pattern)
        return mods

    def remove_base_emulation(self) -> None:
        """Remove the base emulation logic common to all controllers."""
        pass

    def remove_module_emulation(self) -> None:
        """Remove module-specific emulation logic."""
        pass

    def remove_emulation_logic(self) -> ControllerModificationSchema:
        """Remove previously added emulation logic.

        Returns:
            ControllerModificationSchema: The modification schema with all removals.
        """
        log(self).info(f"Starting emulation removal for {self.controller.name}")

        # Remove emulation logic
        self.remove_base_emulation()
        self.remove_module_emulation()
        self.remove_custom_logic()

        # Execute the schema to remove added elements
        self.schema.execute()

        log(self).info(f"Emulation removal completed for {self.controller.name}")
        return self.schema

    def remove_custom_logic(self) -> None:
        """Remove custom emulation logic."""
        pass

    def remove_controller_tag(
        self,
        tag_name: str
    ) -> None:
        """Helper method to remove a controller-scoped tag.

        Args:
            tag_name: Name of the tag to remove
        """
        log(self).debug(f"Removing controller tag '{tag_name}'")

        self.schema.remove_controller_tag(
            tag_name=tag_name
        )

    def remove_datatype(
        self,
        datatype_name: str
    ) -> None:
        """Helper method to remove a datatype from the controller.

        Args:
            datatype_name: Name of the datatype to remove
        """
        log(self).debug(f"Removing datatype '{datatype_name}' from controller")

        self.schema.remove_datatype(
            datatype_name=datatype_name
        )

    def remove_program_tag(
        self,
        program_name: str,
        tag_name: str
    ) -> None:
        """Helper method to remove a tag from a program.

        Args:
            program_name: Name of the program
            tag_name: Name of the tag to remove
        """
        log(self).debug(f"Removing tag '{tag_name}' from program '{program_name}'")

        self.schema.remove_program_tag(
            program_name=program_name,
            tag_name=tag_name
        )

    def remove_routine(
            self,
            program_name: str,
            routine_name: str
    ) -> None:
        """Helper method to remove a routine from the controller.

        Args:
            program_name: Name of the program containing the routine
            routine_name: Name of the routine to remove
        """
        log(self).debug(f"Removing routine '{routine_name}' from controller")

        self.schema.remove_routine(
            program_name,
            routine_name
        )

    def set_emulation_safety_routine(self, routine: Optional[IRoutine]) -> None:
        self._emulation_safety_routine = routine

    def set_emulation_safety_routine_description(self, description: str) -> None:
        if not self._emulation_safety_routine:
            raise ValueError("Safety emulation routine has not been created yet.")
        self._emulation_safety_routine.set_description(description)

    def set_emulation_safety_routine_name(self, name: str) -> None:
        if not self._emulation_safety_routine:
            raise ValueError("Safety emulation routine has not been created yet.")
        self._emulation_safety_routine.set_name(name)

    def set_emulation_standard_routine(self, routine: Optional[IRoutine]) -> None:
        self._emulation_standard_routine = routine

    def set_emulation_standard_routine_description(self, description: str) -> None:
        if not self._emulation_standard_routine:
            raise ValueError("Emulation routine has not been created yet.")
        self._emulation_standard_routine.set_description(description)

    def set_emulation_standard_routine_name(self, name: str) -> None:
        if not self._emulation_standard_routine:
            raise ValueError("Emulation routine has not been created yet.")
        self._emulation_standard_routine.set_name(name)
