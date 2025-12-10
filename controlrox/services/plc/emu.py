"""Pyrox emulation services module.
"""
from pyrox.services.file import get_save_file, save_file
from controlrox.interfaces import IController, IEmulationGenerator
from controlrox.services.tasks.generator import EmulationGeneratorFactory
from controlrox.services.checklist import compile_checklist_from_eplan_project, get_controls_template
from controlrox.services.eplan import get_project

__all__ = (
    'inject_emulation_routine',
    'remove_emulation_routine',
)


def _get_generator(
    controller: IController
) -> IEmulationGenerator:
    gen_class = EmulationGeneratorFactory.get_registered_type_by_supporting_class(controller)
    if not gen_class or not issubclass(gen_class, IEmulationGenerator):
        raise ValueError('No valid generator found for this controller type!')
    return gen_class(controller)  # type: ignore[call-arg]


def _work_precheck(
    controller: IController,
    generator: IEmulationGenerator,
) -> None:
    if not controller:
        raise ValueError('No controller provided for emulation routine operation.')
    if not generator:
        raise ValueError('No generator provided for emulation routine operation.')


def create_checklist_from_template(
    ctrl: IController
) -> None:
    project_checklist = compile_checklist_from_eplan_project(
        project=get_project(ctrl, ''),
        template=get_controls_template()
    )
    if not project_checklist:
        raise ValueError('Could not compile checklist from EPlan project and template!')
    if not ctrl.file_location:
        file_location = get_save_file([('.md', 'Markdown Files')])
    else:
        file_location = ctrl.file_location.replace('.L5X', '_Emulation_Checklist.md')
    if not file_location:
        raise ValueError('No valid location to save checklist file selected!')

    save_file(file_location, project_checklist['raw_content'])


def inject_emulation_routine(
    ctrl: IController
) -> None:
    """Injects emulation routine the current controller.

    Args:
        controller (plc.Controller): The controller to inject the emulation routine into.
    """
    generator = _get_generator(ctrl)
    _work_precheck(ctrl, generator)
    generator.generate_emulation_logic()


def remove_emulation_routine(
    controller: IController
) -> None:
    """Removes emulation routine from the current controller.

    Args:
        controller (plc.Controller): The controller to remove the emulation routine from.
    """
    generator = _get_generator(controller)
    _work_precheck(controller, generator)
    generator.remove_emulation_logic()
