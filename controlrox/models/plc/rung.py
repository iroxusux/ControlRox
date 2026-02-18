"""Rung model for PLC.
"""
from typing import (
    DefaultDict,
    Optional,

)
from pyrox.models import FactoryTypeMeta
from controlrox.interfaces import (
    IRoutine,
    IRung,
)
from controlrox.services import RungFactory

from .protocols import HasSequencedInstructions
from .meta import PlcObject


class Rung(
    IRung,
    HasSequencedInstructions,
    PlcObject[dict],
    metaclass=FactoryTypeMeta['Rung', RungFactory]
):

    def __init__(
        self,
        meta_data: Optional[dict] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        routine: Optional[IRoutine] = None,
        comment: str = '',
        rung_text: str = '',
        rung_number: int = 0,
    ) -> None:
        """type class for plc Rung"""
        HasSequencedInstructions.__init__(self)
        PlcObject.__init__(
            self,
            meta_data=meta_data or DefaultDict(None),
            name=name,
            description=description,
        )

        self._routine: Optional[IRoutine] = routine
        self.meta_data['Comment'] = comment or self.meta_data.get('Comment', '')
        self.meta_data['Text'] = rung_text or self.meta_data.get('Text', '')
        self.meta_data['@Number'] = rung_number or self.meta_data.get('@Number', 0)

    def __eq__(self, other):
        if not isinstance(other, IRung):
            return False
        if self.text == other.text and self.number == other.number:
            return True
        return False

    def __repr__(self):
        return (
            f'Rung(number={self.number}, '
            f'comment={self.comment}, '
            f'text={self.text}, '
            f'instructions={len(self._instructions)}, '
        )

    def __str__(self):
        return self.text

    @property
    def routine(self) -> Optional[IRoutine]:
        return self.get_routine()

    @classmethod
    def get_factory(cls):
        return RungFactory

    def compile(self):
        """Compile the rung."""
        self.compile_instructions()
        self.compile_sequence()
        return self

    def compile_instructions(self, rung: IRung | None = None) -> None:
        return super().compile_instructions(self)  # override to pass rung to instruction compilation

    def get_comment(self) -> str:
        return self.meta_data.get('Comment', '')

    def get_comment_lines(self) -> int:
        """Get the number of comment lines in this rung.
        """
        if not self.comment:
            return 0

        return len(self.comment.splitlines())

    def get_routine(self) -> Optional[IRoutine]:
        return self._routine

    def get_number(self) -> int:
        number = self.meta_data.get('@Number')
        if number is None:
            raise RuntimeError("Rung number is not set.")
        return int(number)

    def get_text(self) -> str:
        return self.meta_data.get('Text', '')

    def invalidate(self) -> None:
        """Invalidate the rung, marking it for recompilation."""
        self.invalidate_instructions()
        self.invalidate_sequence()

    def set_comment(
        self,
        comment: str
    ) -> None:
        self.meta_data['Comment'] = comment

    def set_number(
        self,
        rung_number: int,
    ) -> None:
        self.meta_data['@Number'] = rung_number

    def set_text(
        self,
        text: str,
    ) -> None:
        self.meta_data['Text'] = text


__all__ = [
    'Rung',
]
