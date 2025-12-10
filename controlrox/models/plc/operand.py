"""Logic operand module."""
from typing import Optional
from controlrox.interfaces import (
    ILogicInstruction,
    ILogicOperand,
)
from .meta import PlcObject


class LogicOperand(
    ILogicOperand,
    PlcObject[str],
):
    """Logic Operand
    """

    def __init__(
        self,
        meta_data: str,
        arg_position: int,
        instruction: Optional[ILogicInstruction] = None,
        **kwargs
    ) -> None:
        super().__init__(
            meta_data=meta_data,
            **kwargs
        )
        # positional argument
        self._arg_position = arg_position
        self._instruction = instruction

        # cached values
        self._base_name: str = ''
        self._parents: list[str] = []
        self._trailing_name: str = ''

    def get_all_parent_operands(self) -> list[str]:
        if self._parents:
            return self._parents

        parts = str(self.meta_data).split('.')
        if len(parts) == 1:
            self._parents = [self.meta_data]
            return self._parents

        self._parents = []
        for x in range(len(parts)):
            self._parents.append(str(self._meta_data).rsplit('.', x)[0])

        return self._parents

    def get_argument_position(self) -> int:
        return self._arg_position

    def get_base_name(self) -> str:
        if self._base_name:
            return self._base_name
        self._base_name = str(self.meta_data).split('.')[0]
        return self._base_name

    def get_instruction(self) -> ILogicInstruction:
        if not self._instruction:
            raise ValueError("Instruction is not set for this operand!")
        return self._instruction

    def get_trailing_name(self) -> str:
        parts = str(self.meta_data).split('.')
        if len(parts) == 1:
            return ''

        return '.' + '.'.join(parts[1:])
