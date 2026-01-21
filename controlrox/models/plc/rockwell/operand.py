"""Logix operand module."""
from typing import Optional
from controlrox.interfaces import (
    ILogicInstructionType,
    ILogicInstruction
)
from controlrox.models.plc.operand import LogicOperand
from .meta import RaPlcObject


class LogixOperand(
    RaPlcObject[str],
    LogicOperand,
):
    """Logix Operand
    """

    def __init__(
        self,
        meta_data: str,
        arg_position: int,
        instruction: Optional[ILogicInstruction] = None,
    ) -> None:
        super().__init__(
            meta_data=meta_data,
            arg_position=arg_position,
            instruction=instruction
        )
        if not isinstance(meta_data, str):
            raise TypeError("Meta data must be a string!")

        self._as_aliased: str = ''
        self._as_qualified: str = ''
        self._instruction_type: ILogicInstructionType = ILogicInstructionType.UNKNOWN

    @property
    def alias(self) -> str:
        """Return alias of the operand.

        Returns:
            str: Alias of the operand
        """
        if self._as_aliased:
            return self._as_aliased
        return self.get_alias_name()

    def get_alias_name(self) -> str:
        print('not yet implemented')
        self._as_aliased = 'not yet implemented'
        return self._as_aliased

    def get_base_name(self) -> str:
        if self._base_name:
            return self._base_name
        self._base_name = str(self.meta_data).split('.')[0]
        return self._base_name

    def invalidate(self) -> None:
        raise NotImplementedError("invalidate method is not implemented yet.")
