"""Rung model for PLC.
"""
from typing import (
    DefaultDict,
    Optional,
    Union
)
from pyrox.models.abc.factory import FactoryTypeMeta
from controlrox.interfaces import IRoutine
from controlrox.models.plc.rockwell.meta import PLC_RUNG_FILE
from controlrox.models.plc import Rung
from controlrox.services.plc.rung import RungFactory
from .meta import RaPlcObject


class RaRung(
    RaPlcObject[dict],
    Rung,
    metaclass=FactoryTypeMeta['RaRung', RungFactory]
):

    default_l5x_file_path = PLC_RUNG_FILE
    default_l5x_asset_key = 'Rung'

    def __init__(
        self,
        meta_data: dict = DefaultDict(None),
        routine: Optional[IRoutine] = None,
        rung_number: Union[int, str] = 0,
        rung_text: str = '',
        comment: str = ''
    ):
        """type class for plc Rung"""
        super().__init__(
            meta_data=meta_data,
            name='',
            comment=comment or meta_data.get('Comment', ''),
            routine=routine,
            rung_text=rung_text or meta_data.get('Text', ''),
            rung_number=int(rung_number) or meta_data.get('@Number', 0)
        )

    @property
    def dict_key_order(self) -> list[str]:
        return [
            '@Number',
            '@Type',
            'Comment',
            'Text'
        ]

    @property
    def type(self) -> str:
        return self['@Type']

    @classmethod
    def get_factory(cls):
        return RungFactory
