"""Ford Controller Validator Class
"""
from pyrox.models.network import Ipv4Address
from controlrox.models.plc.rockwell import (
    RaController,
    RaDatatype,
    RaModule,
    RaModuleControlsType
)
from pyrox.services.logging import log
from pyrox.services.logic import function_list_or_chain
from controlrox.applications.validator import BaseControllerValidator
from .ford import FordController


# def success(message: str) -> bool: return BaseControllerValidator.success(message)
# def fail(message: str) -> bool: return BaseControllerValidator.fail(message)
# def warning(message: str) -> bool: return BaseControllerValidator.warning(message)
# def debug_success(message: str) -> bool: return BaseControllerValidator.debug_success(message)


class FordControllerValidator(BaseControllerValidator):
    """Validator for Ford controllers.
    """
    supporting_class = FordController
    std_module_rpi = 20.0  # 20ms RPI for standard modules
    drive_module_rpi = 30.0  # 30ms RPI for drives
    sfty_module_input_rpi = 20.0  # 20ms RPI for safety input modules
    sfty_module_output_rpi = 50.0  # 50ms RPI for safety output modules

    @classmethod
    def _check_module_has_logic_tag(
        cls,
        controller: RaController,
        module_object: RaModule
    ) -> bool:
        """Check if a common PLC object has logic tag.

        Args:
            controller: The controller to check.
            common_plc_object: The common PLC object to check.
        Returns:
            True if the common PLC object has logic tag, False otherwise.
        """
        instr = controller.find_instruction('GSV', module_object.name)
        if not instr:
            raise Exception()
        instr = instr[0]
        target_operand = instr.operands[-1]  # The last operand is the target tag

        if target_operand is None or target_operand == '':
            return warning(f'{module_object.__class__.__name__} {module_object.name} has no logic tag!')

        tag_name = target_operand.meta_data.split('.')[0]
        if tag_name not in controller.tags:
            return warning(f'{module_object.__class__.__name__} {module_object.name} has no logic tag!')

        return debug_success(f'{module_object.__class__.__name__} {module_object.name} has logic tag.')

    @classmethod
    def _check_module_has_valid_network_address(
        cls,
        controller: RaController,
        module_object: RaModule
    ) -> bool:
        """Check if a common PLC object has a valid network address.

        Args:
            controller: The controller to check.
            common_plc_object: The common PLC object to check.
        Returns:
            True if the common PLC object has a valid network address, False otherwise.
        """
        address = Ipv4Address(module_object.address)
        if address.octects[0] != 136:
            return warning(f'{module_object.__class__.__name__} {module_object.name} has invalid network address {address}!'
                           'Must start with 136.129.x.x')
        if address.octects[1] != 129:
            return warning(f'{module_object.__class__.__name__} {module_object.name} has invalid network address {address}!'
                           'Must start with 136.129.x.x')
        if 1 > address.octects[2] > 16:
            return warning(f'{module_object.__class__.__name__} {module_object.name} has invalid network address {address}!'
                           'Third octet must be between 1 and 16.')

        match module_object.introspective_module.controls_type:
            case (
                RaModuleControlsType.INPUT_BLOCK |
                RaModuleControlsType.OUTPUT_BLOCK |
                RaModuleControlsType.INPUT_OUTPUT_BLOCK |
                RaModuleControlsType.BLOCK
            ):
                if address.octects[2] != 1:
                    return warning(f'{module_object.__class__.__name__} {module_object.name} has invalid network address {address}!'
                                   'IO blocks must be in the 136.129.1.x subnet.')

            case (
                RaModuleControlsType.SAFETY_BLOCK |
                RaModuleControlsType.SAFETY_INPUT_BLOCK |
                RaModuleControlsType.SAFETY_OUTPUT_BLOCK |
                RaModuleControlsType.SAFETY_INPUT_OUTPUT_BLOCK
            ):
                if address.octects[2] != 4:
                    return warning(f'{module_object.__class__.__name__} {module_object.name} has invalid network address {address}!'
                                   'Safety blocks must be in the 136.129.4.x subnet.')

            case (
                RaModuleControlsType.DRIVE |
                RaModuleControlsType.ENCODER
            ):
                if address.octects[2] != 6:
                    return warning(f'{module_object.__class__.__name__} {module_object.name} has invalid network address {address}!'
                                   'Drives and Encoders must be in the 136.129.6.x subnet.')
        return debug_success(f'{module_object.__class__.__name__} {module_object.name} has valid network address.')

    @classmethod
    def _check_module_location_in_program(
        cls,
        controller: RaController,
        module_object: RaModule
    ) -> bool:
        """Check if a module is located in the proper part of a program
        Args:
            controller: The controller to check.
            module_object: The module to check.
        Returns:
            True if the module is located in the proper part of a program, False otherwise.
        """
        in_instr = controller.find_instruction('COP', module_object.name + ':I')
        out_instr = controller.find_instruction('COP', module_object.name + ':O')
        if in_instr is None or len(in_instr) == 0:
            return warning(f'{module_object.__class__.__name__} {module_object.name} is missing COP instruction(s)!')
        in_ = in_instr[0]

        out_ = out_instr[0] if out_instr and len(out_instr) > 0 else None

        if out_:
            if in_.container != out_.container:
                return warning(f'{module_object.__class__.__name__} {module_object.name} has COP instructions in different programs!')

        container = in_.container
        if not container:
            return warning(f'{module_object.__class__.__name__} {module_object.name} COP instructions are not in a program!')

        if container.name.lower() not in module_object.name.lower():
            if container.name != 'MainProgram':  # Allow MainProgram as a valid container for any module
                return warning(f'{module_object.__class__.__name__} {module_object.name} is not located in a program with a matching name!')

        return debug_success(f'{module_object.__class__.__name__} {module_object.name} is located in a valid program.')

    @classmethod
    def validate_datatype(
        cls,
        controller: RaController,
        datatype: RaDatatype
    ) -> bool:
        if datatype.name.lower().startswith('fud'):
            return True
        if datatype.name.lower().startswith('rac_'):
            return True
        if datatype.name.lower().startswith('raudt_'):
            return True
        any_failures = not super().validate_datatype(controller, datatype)
        return not any_failures

    @classmethod
    def _validate_module_drive(
        cls,
        controller,
        module
    ) -> bool:
        log(cls).info(f'Validating Ford Drive Module: {module.name}')
        return function_list_or_chain([
            lambda: cls.check_module_has_logic_gsv(controller, module),
            lambda: cls.check_module_has_cop_in_instruction(controller, module),
            lambda: cls.check_module_has_cop_out_instruction(controller, module),
            lambda: cls.check_module_has_valid_network_rpi(controller, module, cls.drive_module_rpi),
            lambda: cls._check_module_has_valid_network_address(controller, module),
            lambda: cls._check_module_tag_exists(controller, module),
            lambda: cls._check_module_location_in_program(controller, module)
        ])

    @classmethod
    def _validate_module_encoder(
        cls,
        controller,
        module
    ) -> bool:
        log(cls).info(f'Validating Ford Method Encoder: {module.name}')
        return function_list_or_chain([
            lambda: cls.check_module_has_logic_gsv(controller, module),
            lambda: cls.check_module_has_cop_in_instruction(controller, module),
            lambda: cls.check_module_has_valid_network_rpi(controller, module, cls.std_module_rpi),
            lambda: cls._check_module_has_valid_network_address(controller, module),
            lambda: cls._check_module_tag_exists(controller, module),
            lambda: cls._check_module_location_in_program(controller, module)
        ])

    @classmethod
    def _validate_module_io_block(
        cls,
        controller,
        module,
    ) -> bool:
        if module.introspective_module.controls_type is RaModuleControlsType.INPUT_BLOCK:
            return cls._validate_standard_input_block(controller, module)
        elif module.introspective_module.controls_type is RaModuleControlsType.OUTPUT_BLOCK:
            return cls._validate_standard_output_block(controller, module)
        elif module.introspective_module.controls_type is RaModuleControlsType.INPUT_OUTPUT_BLOCK:
            return cls._validate_standard_io_block(controller, module)
        elif module.introspective_module.controls_type in [
            RaModuleControlsType.SAFETY_BLOCK,
            RaModuleControlsType.SAFETY_INPUT_BLOCK,
            RaModuleControlsType.SAFETY_OUTPUT_BLOCK,
            RaModuleControlsType.SAFETY_INPUT_OUTPUT_BLOCK
        ]:
            return cls._validate_safety_io_block(controller, module)
        else:
            log(cls).warning(
                f'No specific IO block validation implemented for module type: {module.introspective_module.controls_type}'
            )
            return False

    @classmethod
    def _validate_module_plc(
        cls,
        controller,
        module
    ) -> bool:
        log(cls).info(f'Validating Ford PLC Module: {module.name}')
        return True  # TODO: Implement PLC module validation if needed

    @classmethod
    def _check_module_tag_exists(
        cls,
        controller,
        module
    ) -> bool:
        if module.name not in controller.tags:
            log(cls).error(f'Module {module.name} does not have a corresponding tag in the controller.')
            return False
        return True

    @classmethod
    def _validate_rack_comm_card(
        cls,
        controller,
        module
    ) -> bool:
        log(cls).info(f'Validating Ford Rack Communication Card: {module.name}')
        return True  # TODO: Implement PLC module validation if needed

    @classmethod
    def _validate_standard_input_block(
        cls,
        controller,
        module
    ) -> bool:
        log(cls).info(f'Validating Ford Standard Input Block: {module.name}')
        return function_list_or_chain([
            lambda: cls.check_module_has_logic_gsv(controller, module),
            lambda: cls.check_module_has_cop_in_instruction(controller, module),
            lambda: cls.check_module_has_valid_network_rpi(controller, module, cls.std_module_rpi),
            lambda: cls._check_module_has_valid_network_address(controller, module),
            lambda: cls._check_module_tag_exists(controller, module),
            lambda: cls._check_module_location_in_program(controller, module)
        ])

    @classmethod
    def _validate_standard_io_block(
        cls,
        controller,
        module
    ) -> bool:
        log(cls).info(f'Validating Ford Standard IO Block: {module.name}')
        return function_list_or_chain([
            lambda: cls._validate_standard_input_block(controller, module),
            lambda: cls.check_module_has_cop_out_instruction(controller, module),
        ])

    @classmethod
    def _validate_standard_output_block(
        cls,
        controller,
        module
    ) -> bool:
        log(cls).info(f'Validating Ford Standard Output Block: {module.name}')
        return function_list_or_chain([
            lambda: cls.check_module_has_logic_gsv(controller, module),
            lambda: cls.check_module_has_cop_out_instruction(controller, module),
            lambda: cls.check_module_has_valid_network_rpi(controller, module, cls.std_module_rpi),
            lambda: cls._check_module_has_valid_network_address(controller, module),
            lambda: cls._check_module_tag_exists(controller, module),
            lambda: cls._check_module_location_in_program(controller, module)
        ])

    @classmethod
    def _validate_safety_io_block(
        cls,
        controller,
        module
    ) -> bool:
        log(cls).info(f'Validating Ford Safety Block: {module.name}')
        return function_list_or_chain([
            lambda: cls.check_module_has_logic_gsv(controller, module),
            lambda: cls.check_module_has_cop_in_instruction(controller, module),
            lambda: cls.check_module_has_cop_out_instruction(controller, module),
            lambda: cls.check_module_has_valid_network_rpi(controller, module, cls.sfty_module_input_rpi),
            lambda: cls._check_module_has_valid_network_address(controller, module),
        ])

    @classmethod
    def validate_module(
        cls,
        controller,
        module
    ) -> bool:
        type_ = module.introspective_module.controls_type

        if type_ is RaModuleControlsType.PLC:
            return cls._validate_module_plc(controller, module)
        elif type_ is RaModuleControlsType.RACK_COMM_CARD:
            return cls._validate_rack_comm_card(controller, module)
        elif type_ is RaModuleControlsType.ETHERNET_SWITCH:
            return True  # No specific validation needed for Ethernet Switch
        elif type_ in RaModuleControlsType.all_block_types():
            return cls._validate_module_io_block(controller, module)
        elif type_ is RaModuleControlsType.ENCODER:
            return cls._validate_module_encoder(controller, module)
        elif type_ is RaModuleControlsType.DRIVE:
            return cls._validate_module_drive(controller, module)
        else:
            return warning(f'No validation implemented for module type: {module.introspective_module.controls_type}')
