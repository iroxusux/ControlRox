import copy
import importlib
import threading
from typing import List, Optional, Self, Tuple, Type, Union
from pathlib import Path

from pyrox.services.dict import remove_none_values_inplace
from pyrox.services.logging import log
from pyrox.services.search import check_wildcard_patterns
from pyrox.models.abc.factory import MetaFactory, FactoryTypeMeta

from controlrox.interfaces import IController, IDatatype
from controlrox.services.l5x import dict_to_l5x_file, l5x_dict_from_file

from xml.parsers import expat


class ControllerMatcherFactory(MetaFactory):
    """Controller matcher factory."""

    @classmethod
    def get_registered_types(cls) -> dict[str, Type['ControllerMatcher']]:
        """Get the registered controller matcher types for this factory.

        Returns:
            dict[str, Type[ControllerMatcher]]: The registered controller matcher types.
        """
        return super().get_registered_types()


class ControllerMatcher(metaclass=FactoryTypeMeta['ControllerMatcher', ControllerMatcherFactory]):
    """Abstract base class for controller matching strategies."""

    supports_registering = False  # This class can't be used to match anything

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.supports_registering = True  # Subclasses can be used to match

    @staticmethod
    def get_datatype_patterns() -> List[str]:
        """List of patterns to identify the controller by datatype."""
        raise NotImplementedError("Subclasses must implement this method")

    @staticmethod
    def get_module_patterns() -> List[str]:
        """List of patterns to identify the controller by module."""
        raise NotImplementedError("Subclasses must implement this method")

    @staticmethod
    def get_program_patterns() -> List[str]:
        """List of patterns to identify the controller by program."""
        raise NotImplementedError("Subclasses must implement this method")

    @staticmethod
    def get_safety_program_patterns() -> List[str]:
        """List of patterns to identify the controller by safety program."""
        raise NotImplementedError("Subclasses must implement this method")

    @staticmethod
    def get_tag_patterns() -> List[str]:
        """List of patterns to identify the controller by tag."""
        raise NotImplementedError("Subclasses must implement this method")

    @classmethod
    def calculate_score(
        cls,
        controller_data: dict
    ) -> float:
        """Calculate a matching score (0.0 to 1.0, higher is better).

        Args:
            controller_data (dict): The controller data to evaluate.
        """
        score = 0.0
        if cls.check_controller_datatypes(controller_data):
            score += 0.2
        if cls.check_controller_modules(controller_data):
            score += 0.2
        if cls.check_controller_programs(controller_data):
            score += 0.2
        if cls.check_controller_safety_programs(controller_data):
            score += 0.2
        if cls.check_controller_tags(controller_data):
            score += 0.2
        return score

    @classmethod
    def can_match(
        cls,
    ) -> bool:
        """
        """
        return False

    @classmethod
    def get_class(cls) -> type[Self]:
        return cls

    @classmethod
    def get_factory(cls):
        return ControllerMatcherFactory

    @classmethod
    def get_controller_constructor(
        cls,
    ) -> Type[IController]:
        """Get the appropriate controller constructor for this matcher.

        Returns:
            Type[Controller]: The constructor for the appropriate controller type.
        """
        raise NotImplementedError("Subclasses must implement this method")

    @classmethod
    def check_controller_datatypes(
        cls,
        controller_data: dict,
    ) -> bool:
        """Check if controller datatypes match controller pattern.

        Args:
            controller_data (dict): The controller data to evaluate.
        """
        return cls.check_dict_list_for_patterns(
            cls.get_controller_data_list(controller_data, 'DataType'),
            '@Name',
            cls.get_datatype_patterns()
        )

    @classmethod
    def check_controller_modules(
        cls,
        controller_data: dict,
    ) -> bool:
        """Check if controller modules match controller pattern."""
        return cls.check_dict_list_for_patterns(
            cls.get_controller_data_list(controller_data, 'Module'),
            '@Name',
            cls.get_module_patterns()
        )

    @classmethod
    def check_controller_programs(
        cls,
        controller_data: dict,
    ) -> bool:
        """Check if controller programs match controller pattern."""
        return cls.check_dict_list_for_patterns(
            cls.get_controller_data_list(controller_data, 'Program'),
            '@Name',
            cls.get_program_patterns()
        )

    @classmethod
    def check_controller_safety_programs(
        cls,
        controller_data: dict,
    ) -> bool:
        """Check if controller safety programs match controller pattern."""
        programs = cls.get_controller_data_list(controller_data, 'Program')
        safety_programs = [p for p in programs if p.get('@Class') == 'Safety']
        return cls.check_dict_list_for_patterns(
            safety_programs,
            '@Name',
            cls.get_safety_program_patterns()
        )

    @classmethod
    def check_controller_tags(
        cls,
        controller_data: dict,
    ) -> bool:
        """Check if controller tags match controller pattern."""
        return cls.check_dict_list_for_patterns(
            cls.get_controller_data_list(controller_data, 'Tag'),
            '@Name',
            cls.get_tag_patterns()
        )

    @classmethod
    def check_dict_list_for_patterns(
        cls,
        dict_list: List[dict],
        key: str,
        patterns: List[str]
    ) -> bool:
        """Check if any dictionary in the list has a value for the given key that matches any of the patterns.

        Args:
            dict_list (List[dict]): List of dictionaries to check.
            key (str): The key in the dictionary to check the value of.
            patterns (List[str]): List of patterns to match against the value.

        Returns:
            bool: True if any value matches any pattern, False otherwise.
        """
        if not patterns:
            return False
        log(cls).debug(f"Checking patterns {patterns} in key '{key}' of dict list")
        result = check_wildcard_patterns(
            [item.get(key, '') for item in dict_list],
            patterns
        )
        log(cls).debug(f"Pattern match result: {result}")
        return result

    @classmethod
    def get_controller_meta(
        cls,
        controller_data: dict
    ) -> dict:
        """Extract relevant metadata for the controller.

        Args:
            controller_data (dict): The controller data to extract from.

        Returns:
            dict: The controller metadata.

        Raises:
            ValueError: If no controller data is provided.
        """
        if not controller_data:
            raise ValueError("No controller data provided")
        logix_content = controller_data.get('RSLogix5000Content', {})
        if logix_content is None:
            return {}

        controller_dict = logix_content.get('Controller', {})
        if controller_dict is None:
            return {}

        return controller_dict

    @classmethod
    def get_controller_data_list(
        cls,
        controller_data: dict,
        data_string: str,
    ) -> List[dict]:
        """Extract the list of data from the controller data.

        Args:
            controller_data (dict): The controller data to extract from.
            data_string (str): The key string to extract (e.g., 'Program', 'Tag').

        Returns:
            List[dict]: The list of data dictionaries.
        """
        controller_meta = cls.get_controller_meta(controller_data)

        data_list_container = controller_meta.get(f'{data_string}s', {})
        if data_list_container is None:
            return []

        data_list = data_list_container.get(data_string, [])
        if data_list is None:
            return []

        if isinstance(data_list, dict):
            data_list = [data_list]

        return data_list


class ControllerFactory(MetaFactory):
    """Controller factory with scoring-based matching."""

    @classmethod
    def get_best_match(
        cls,
        controller_data: dict,
        min_score: float = 0.3
    ) -> Optional[Type]:
        """Get the best matching controller type based on scoring."""
        if not controller_data:
            log(cls).warning("No controller data provided")
            return None

        scored_matches: List[Tuple[float, Type]] = []
        matchers = ControllerMatcherFactory.get_registered_types()
        if not matchers:
            log(cls).warning("No controller matchers registered")
            return None

        for _, matcher in matchers.items():
            score = matcher.calculate_score(controller_data)
            ctrl_class = matcher.get_controller_constructor()
            if score >= min_score:
                scored_matches.append((score, matcher.get_controller_constructor()))
                log(cls).info(
                    f"Matched {ctrl_class.__name__} with score {score:.2f}"
                )
            else:
                log(cls).info(f"{ctrl_class.__name__} score {score:.2f} below min score {min_score}")

        if not scored_matches:
            log(cls).info(f"No matches found above min score {min_score}")
            return None

        # Sort by score (highest first) and return the best match
        scored_matches.sort(key=lambda x: x[0], reverse=True)
        best_score, best_class = scored_matches[0]

        log(cls).info(f"Best match: {best_class.__name__} with score {best_score:.2f}")
        return best_class

    @classmethod
    def create_controller(
        cls,
        meta_data: dict,
        **kwargs
    ) -> Optional[IController]:
        """Create the best matching controller instance."""
        controller_class = cls.get_best_match(meta_data)
        if not controller_class:
            return None
        return controller_class(meta_data=meta_data, **kwargs)


class ControllerInstanceManager:
    """
    Manages controller instances.
    """
    _controller: Optional[IController] = None
    _lock = threading.Lock()

    def __init__(self):
        raise RuntimeError('ControllerInstanceManager is a static class and should not be instantiated!')

    @classmethod
    def get_controller(cls) -> Optional[IController]:
        """Get the current controller instance.

        Returns:
            IController: The current controller instance or None if not set.
        """
        return cls._controller

    @classmethod
    def set_controller(cls, controller: Optional[IController]) -> None:
        """Set the current controller instance.

        Args:
            controller (IController): The controller instance to set.
        """
        with cls._lock:
            if controller and not isinstance(controller, IController):
                raise ValueError('controller must be a valid IController object!')
            cls._controller = controller

    @classmethod
    def load_controller_from_file_location(
        cls,
        file_location: Union[Path, str],
    ) -> Optional[IController]:
        """load a controller from a provided .l5x file location

        Args:
            file_location (str): file location (must end in .l5x)
        Returns:
            Controller: controller object
        """
        ctrl = None

        try:
            if not file_location:
                raise ValueError('file_location must be a valid string or Path!')

            controller_meta_data = l5x_dict_from_file(file_location)

            if not controller_meta_data:
                raise ValueError(f'Unable to load controller meta data from file: {file_location}')

            ctrl = ControllerFactory.create_controller(
                controller_meta_data,
                file_location=file_location
            )

            if ctrl is None:
                raise ValueError(f'No suitable controller type found for file: {file_location}')

        except FileNotFoundError:
            log(__name__).error(f'Controller file not found: {file_location}')
            raise
        except ValueError as e:
            log(__name__).error(f'Invalid controller data in {file_location}: {e}')
            raise
        except expat.ExpatError as e:
            log(__name__).error(f'Malformed L5X file {file_location}: {e}')
            raise
        except Exception as e:
            log(__name__).error(f'Error loading controller from file {file_location}: {e}')
            raise

        finally:
            cls.set_controller(ctrl)
            return cls._controller

    @classmethod
    def new_controller(
        cls,
    ) -> IController:
        """Create a new empty controller instance.

        Returns:
            IController: The new controller instance.
        """
        ctrl = ControllerFactory.create_controller(
            meta_data={},
        )
        if ctrl is None:
            raise RuntimeError('Unable to create new controller instance!')

        cls.set_controller(ctrl)
        if not cls._controller:
            raise RuntimeError('Controller instance was not set properly!')

        return cls._controller

    @classmethod
    def save_controller_to_file_location(
        cls,
        controller: IController,
        file_location: Union[Path, str]
    ) -> None:
        """save a controller to a provided .l5x file location

        Args:
            controller (Controller): controller object
            file_location (str): file location (must end in .l5x)
        """
        if isinstance(file_location, Path):
            file_location = str(file_location)

        if not file_location.endswith('.L5X'):
            file_location += '.L5X'

        if not controller or not isinstance(controller, IController):
            raise ValueError('controller must be a valid Controller object!')

        meta_data = {}
        meta_data['RSLogix5000Content'] = controller.get_meta_data().get('RSLogix5000Content', None)

        if not meta_data or not isinstance(meta_data, dict):
            raise ValueError('controller.meta_data must be a valid dictionary!')

        if 'RSLogix5000Content' not in meta_data or not isinstance(meta_data['RSLogix5000Content'], dict):
            raise ValueError('controller.meta_data must contain a valid "RSLogix5000Content" dictionary!')

        if len(meta_data.keys()) != 1:
            raise ValueError('controller.meta_data contains unexpected keys!')

        write_dict = copy.deepcopy(meta_data)
        remove_none_values_inplace(write_dict)
        dict_to_l5x_file(
            write_dict,
            file_location
        )


def get_controller_datatype(
    controller: IController,
    datatype_name: str
) -> Optional[IDatatype]:
    """get a datatype from a controller by name

    Args:
        controller (IController): controller object
        datatype_name (str): name of the datatype
    Returns:
        Datatype: datatype object
    """
    if not controller or not isinstance(controller, IController):
        raise ValueError('controller must be a valid IController object!')

    if not datatype_name or not isinstance(datatype_name, str):
        raise ValueError('datatype_name must be a valid string!')

    datatype = controller.get_datatypes().get(datatype_name, None)
    return datatype


def load_controller_from_file_location(
    file_location: Union[Path, str],
) -> Optional[IController]:
    """load a controller from a provided .l5x file location

    Args:
        file_location (str): file location (must end in .l5x)
    Returns:
        Controller: controller object
    """

    controller_meta_data = l5x_dict_from_file(file_location)
    if not controller_meta_data:
        log(__name__).warning(f'Unable to load controller meta data from file: {file_location}')
        return None

    ctrl = ControllerFactory.create_controller(
        controller_meta_data,
        file_location=file_location
    )

    if not ctrl:
        log(__name__).warning(f'No suitable controller type found for file: {file_location}')
        return None

    return ctrl


def save_controller_to_file_location(
    controller: IController,
    file_location: Union[Path, str]
) -> None:
    """save a controller to a provided .l5x file location

    Args:
        controller (Controller): controller object
        file_location (str): file location (must end in .l5x)
    """
    if isinstance(file_location, Path):
        file_location = str(file_location)

    if not file_location.endswith('.L5X'):
        file_location += '.L5X'

    import controlrox.models.plc.rockwell
    importlib.reload(controlrox.models.plc)

    if not controller or not isinstance(controller, IController):
        raise ValueError('controller must be a valid Controller object!')

    meta_data = {}
    meta_data['RSLogix5000Content'] = controller.get_meta_data().get('RSLogix5000Content', None)

    if not meta_data or not isinstance(meta_data, dict):
        raise ValueError('controller.meta_data must be a valid dictionary!')

    if 'RSLogix5000Content' not in meta_data or not isinstance(meta_data['RSLogix5000Content'], dict):
        raise ValueError('controller.meta_data must contain a valid "RSLogix5000Content" dictionary!')

    if len(meta_data.keys()) != 1:
        raise ValueError('controller.meta_data contains unexpected keys!')

    write_dict = copy.deepcopy(meta_data)
    remove_none_values_inplace(write_dict)
    dict_to_l5x_file(
        write_dict,
        file_location
    )


def unsafe_load_controller_from_file_location(
    file_location: Union[Path, str]
) -> IController:
    """Unsafe load a controller from a provided .l5x file location

    Args:
        file_location (str): file location (must end in .l5x)
    Returns:
        Controller: controller object
    Raises:
        ValueError: if unable to load controller from file location
    """
    controller = load_controller_from_file_location(file_location)
    if not controller:
        raise ValueError(f'unable to load controller from {file_location}!')
    return controller


__all__ = (
    'ControllerMatcher',
    'ControllerMatcherFactory',
    'ControllerFactory',
    'get_controller_datatype',
    'load_controller_from_file_location',
    'unsafe_load_controller_from_file_location',
    'save_controller_to_file_location',
)
