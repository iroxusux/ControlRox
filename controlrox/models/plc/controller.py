"""PLC type module for Pyrox framework."""
from typing import (
    List,
    Optional,
)

from pyrox.models import HashList
from pyrox.services.logging import log

from controlrox.interfaces import (
    IAddOnInstruction,
    IController,
    IControllerSafetyInfo,
    IDatatype,
    IHasRoutines,
    IHasTags,
    IModule,
    ITag,
    IProgram,
    IRoutine,
    IRung,
)

from controlrox.services import (
    AOIFactory,
    DatatypeFactory,
    ModuleFactory,
    ProgramFactory,
    RoutineFactory,
    RungFactory,
    TagFactory
)

from .protocols import (
    HasAOIs,
    HasDatatypes,
    HasModules,
    HasPrograms,
    HasTags
)

from .meta import PlcObject

__all__ = (
    'Controller',
)


class Controller(
    IController,
    HasAOIs,
    HasDatatypes,
    HasModules,
    HasPrograms,
    HasTags,
    PlcObject[dict]
):
    """Controller for a PLC project.

    Args:
        meta_data (str, optional): The meta data for the controller. Defaults to None.
        file_location (str): The file location of the controller project. Defaults to None.
        comms_path (str): The communication path for the controller. Defaults to ''.
        slot (int): The slot number of the controller. Defaults to 0.
    """

    def __init__(
        self,
        meta_data: Optional[dict] = None,
        file_location: str = '',
        comms_path: str = '',
        slot: int = 0,
        **kwargs,
    ) -> None:
        super().__init__(
            meta_data=meta_data,
            **kwargs,
        )

        self._file_location, self._comms_path, self._slot = file_location, comms_path, slot
        self._processor_type: str = ''

    @property
    def comms_path(self) -> str:
        return self.get_comms_path()

    @property
    def file_location(self) -> str:
        return self.get_file_location()

    @property
    def slot(self) -> Optional[int]:
        return self.get_slot()

    @classmethod
    def from_file(
            cls,
            file_location: str,
            meta_data: Optional[dict] = None
    ) -> IController:
        raise NotImplementedError("from_file should be overridden by subclasses.")

    @classmethod
    def from_meta_data(
        cls,
        meta_data: dict,
        file_location: str = '',
        comms_path: str = '',
        slot: int = 0
    ) -> IController:
        raise NotImplementedError("from_meta_data should be overridden by subclasses.")

    def _compile_common_hashlist_from_meta_data(
        self,
        target_list: HashList,
        target_meta_list: list,
        item_class: type,
        **kwargs
    ) -> None:
        """Compile a common HashList from meta data.

        Args:
            target_list (HashList): The target HashList to populate.
            target_meta_list (list): The list of meta data dictionaries.
            item_class (type): The class type of the items to create.
        """
        target_list.clear()
        for item in target_meta_list:
            if isinstance(item, dict):
                target_list.append(
                    item_class(
                        meta_data=item,
                        **kwargs
                    ))
            else:
                log(self).warning(f'Invalid item data: {item}. Skipping...')

    def compile(self) -> 'Controller':
        self.compile_aois()
        self.compile_datatypes()
        self.compile_modules()
        self.compile_programs()
        self.compile_tags()
        return self

    def compile_aois(self) -> None:
        constructor = AOIFactory.get_registered_type_by_supporting_class(self.__class__)
        if not constructor:
            raise RuntimeError('No AOI constructor found for this controller type!')

        self._compile_common_hashlist_from_meta_data(
            target_list=self._aois,
            target_meta_list=self.raw_aois,
            item_class=constructor,
        )

    def compile_datatypes(self) -> None:
        constructor = DatatypeFactory.get_registered_type_by_supporting_class(self.__class__)
        if not constructor:
            raise RuntimeError('No Datatype constructor found for this controller type!')

        self._compile_common_hashlist_from_meta_data(
            target_list=self._datatypes,
            target_meta_list=self.raw_datatypes,
            item_class=constructor,
        )

    def compile_modules(self) -> None:
        constructor = ModuleFactory.get_registered_type_by_supporting_class(self.__class__)
        if not constructor:
            raise RuntimeError('No Module constructor found for this controller type!')

        self._compile_common_hashlist_from_meta_data(
            target_list=self._modules,
            target_meta_list=self.raw_modules,
            item_class=constructor,
        )

    def compile_programs(self) -> None:
        constructor = ProgramFactory.get_registered_type_by_supporting_class(self.__class__)
        if not constructor:
            raise RuntimeError('No Program constructor found for this controller type!')

        self._compile_common_hashlist_from_meta_data(
            target_list=self._programs,
            target_meta_list=self.raw_programs,
            item_class=constructor,
        )

    def compile_tags(self) -> None:
        constructor = TagFactory.get_registered_type_by_supporting_class(self.__class__)
        if not constructor:
            raise RuntimeError('No Tag constructor found for this controller type!')

        self._compile_common_hashlist_from_meta_data(
            target_list=self._tags,
            target_meta_list=self.raw_tags,
            item_class=constructor,
            container=self
        )

    def create_aoi(
        self,
        name: str = '',
        description: str = '',
        meta_data: Optional[dict] = None
    ) -> IAddOnInstruction:

        constructor = AOIFactory.get_registered_type_by_supporting_class(self.__class__)
        if not constructor:
            raise RuntimeError('No AOI constructor found for this controller type!')

        return constructor(
            name=name,
            description=description,
            meta_data=meta_data
        )

    def create_datatype(
        self,
        name: str = '',
        description: str = '',
        meta_data: Optional[dict] = None
    ) -> IDatatype:
        constructor = DatatypeFactory.get_registered_type_by_supporting_class(self.__class__)
        if not constructor:
            raise RuntimeError('No Datatype constructor found for this controller type!')

        return constructor(
            name=name,
            description=description,
            meta_data=meta_data
        )

    def create_module(
        self,
        name: str = '',
        description: str = '',
        meta_data: Optional[dict] = None
    ) -> IModule:
        constructor = ModuleFactory.get_registered_type_by_supporting_class(self.__class__)
        if not constructor:
            raise RuntimeError('No Module constructor found for this controller type!')

        return constructor(
            name=name,
            description=description,
            meta_data=meta_data
        )

    def create_program(
        self,
        name: str = '',
        description: str = '',
        meta_data: Optional[dict] = None
    ) -> IProgram:
        constructor = ProgramFactory.get_registered_type_by_supporting_class(self.__class__)
        if not constructor:
            raise RuntimeError('No Program constructor found for this controller type!')

        return constructor(
            name=name,
            description=description,
            meta_data=meta_data
        )

    def create_routine(
        self,
        name: str = '',
        description: str = '',
        meta_data: Optional[dict] = None,
        container: Optional[IHasRoutines] = None
    ) -> IRoutine:
        constructor = RoutineFactory.get_registered_type_by_supporting_class(self.__class__)
        if not constructor:
            raise RuntimeError('No Routine constructor found for this controller type!')

        return constructor(
            name=name,
            description=description,
            meta_data=meta_data,
            container=container
        )

    def create_rung(
        self,
        meta_data: Optional[dict] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        routine: Optional[IRoutine] = None,
        comment: str = '',
        rung_text: str = '',
        rung_number: int = -1
    ) -> IRung:
        constructor = RungFactory.get_registered_type_by_supporting_class(self.__class__)
        if not constructor:
            raise RuntimeError('No Rung constructor found for this controller type!')

        return constructor(
            meta_data=meta_data,
            routine=routine,
            comment=comment,
            rung_text=rung_text,
            rung_number=rung_number,
        )

    def create_tag(
        self,
        name: str = '',
        datatype: str = '',
        description: str = '',
        container: Optional[IHasTags] = None,
        meta_data: Optional[dict] = None,
        tag_class: str = '',
        tag_type: str = 'Base',
        dimensions: str = '',
        constant: bool = False,
        external_access: str = 'Read/Write',
        **_
    ) -> ITag:
        constructor = TagFactory.get_registered_type_by_supporting_class(self.__class__)
        if not constructor:
            raise RuntimeError('No Tag constructor found for this controller type!')

        return constructor(
            meta_data=meta_data,
            name=name,
            description=description,
            tag_class=tag_class,
            tag_type=tag_type,
            datatype=datatype,
            dimensions=dimensions,
            constant=constant,
            external_access=external_access,
            container=container,
        )

    def get_comms_path(self) -> str:
        return self._comms_path

    def get_controller_safety_info(self) -> IControllerSafetyInfo:
        raise NotImplementedError("This method should be overridden by subclasses to get controller safety info.")

    def get_file_location(self) -> str:
        return self._file_location  # type: ignore

    def get_processor_type(self) -> str:
        return self._processor_type

    def get_slot(self) -> int:
        return self._slot

    def set_comms_path(self, comms_path: str) -> None:
        if comms_path is not None and not isinstance(comms_path, str):
            raise ValueError('comms_path must be a string or None')
        self._comms_path = comms_path

    def set_file_location(
        self,
        file_location: Optional[str]
    ) -> None:
        if file_location is not None and not isinstance(file_location, str):
            raise ValueError('file_location must be a string or None')
        self._file_location = file_location

    def set_processor_type(
        self,
        processor_type: str
    ) -> None:
        self._processor_type = processor_type

    def set_slot(
        self,
        slot: int
    ) -> None:
        self._slot = slot

    def import_assets_from_file(
        self,
        file_location: str,
        asset_types: Optional[List[str]] = None
    ) -> None:
        raise NotImplementedError("import_assets_from_file should be overridden by subclasses.")

    def invalidate(self) -> None:
        self.invalidate_aois()
        self.invalidate_datatypes()
        self.invalidate_modules()
        self.invalidate_programs()
        self.invalidate_tags()

    def get_revision(self) -> str:
        raise NotImplementedError("get_revision should be overridden by subclasses.")

    def set_revision(self, revision: str) -> None:
        raise NotImplementedError("set_revision should be overridden by subclasses.")

    def get_created_date(self) -> str:
        raise NotImplementedError("get_created_date should be overridden by subclasses.")

    def get_modified_date(self) -> str:
        raise NotImplementedError("get_modified_date should be overridden by subclasses.")

    def set_modified_date(self, modified_date: str) -> None:
        raise NotImplementedError("set_modified_date should be overridden by subclasses.")
