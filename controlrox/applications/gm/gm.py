"""General motors implimentation specific plc types
    """
from enum import Enum
import fnmatch
import re
from typing import Generic, Optional, TypeVar, Union

from controlrox.interfaces import META
from controlrox.interfaces import (
    IRoutine,
    IProgram,
)
from controlrox.models.plc.rockwell import (
    RaPlcObject,
    RaAddOnInstruction,
    RaController,
    RaDatatype,
    RaModule,
    RaProgram,
    RaRung,
    RaRoutine,
    RaTag,
)


GM_CTRL = TypeVar('GM_CTRL', bound='GmController')

GM_CHAR = 'z'
GM_SAFE_CHAR = 's_z'
USER_CHAR = 'u'
USER_SAFE_CHAR = 's_u'
ALARM_PATTERN:   str = '*<Alarm[[]*[]]:*>'
PROMPT_PATTERN:  str = '*<Prompt[[]*[]]:*>'

DIAG_RE_PATTERN:    str = r"(<.+\[\d*\].*>)"
TL_RE_PATTERN:      str = r"(?:.*)(<.*\[\d*\]:.*>)(?:.*)"
TL_ID_PATTERN:      str = r"(?:.*<)(.*)(?:\[\d*\]:.*>.*)"
DIAG_NUM_RE_PATTERN: str = r"(?:<.*\[)(\d*)(?:\].*>)"
COLUMN_RE_PATTERN:   str = r"(?:<.*\[\d+\]:)(@[a-zA-Z]+\d+)(?:.*)"
DIAG_NAME_RE_PATTER: str = r"(?!MOV\(\d*,HMI\.Diag\.Pgm\.Name\.LEN\))(MOV\(.*?,HMI\.Diag\.Pgm\.Name\.DATA\[\d*?\])"


class TextListElement:
    """General Motors Text List Generic Element
    """

    def __init__(
        self,
        text: str,
        rung: 'GmRung'
    ):
        self._text:      str = self._get_diag_text(text)
        self._text_list_id: str = self._get_tl_id()
        self._number:    int = self._get_diag_number()
        self._rung: 'GmRung' = rung

    def __eq__(self, other):
        if isinstance(other, TextListElement):
            return self.number == other.number
        return False

    def __hash__(self):
        return hash((self.text, self.number))

    def __repr__(self) -> str:
        return (
            f'text={self.text}, '
            f'text_list_id={self.text_list_id}'
            f'number={self.number}, '
            f'rung={self.rung}'
        )

    def __str__(self):
        return self.text

    @property
    def number(self) -> int:
        return self._number

    @property
    def rung(self) -> 'GmRung':
        return self._rung

    @property
    def text(self) -> str:
        return self._text

    @property
    def text_list_id(self) -> str:
        return self._text_list_id

    def _get_diag_number(self):
        match = re.search(DIAG_NUM_RE_PATTERN, self._text)
        if match:
            return int(match.groups()[0])

        raise ValueError('Could not find diag number in diag string! -> %s' % self._text)

    def _get_diag_text(self, text: str):
        match = re.search(DIAG_RE_PATTERN, text)
        if match:
            return match.groups()[0]

        raise ValueError('Could not find diag text in diag string! -> %s' % text)

    def _get_tl_id(self) -> str:
        if not self.text:
            return ''

        match = re.search(TL_ID_PATTERN, self.text)
        if match:
            return match.groups()[0].strip()
        else:
            return ''


class KDiagType(Enum):
    NA = 0
    ALARM = 1
    PROMPT = 2
    VALUE = 3


class KDiagProgramType(Enum):
    NA = 0
    MCP = 1
    STATION = 2
    DEVICE = 3
    ROBOT = 4
    HMI = 5
    PFE = 6


class KDiag(TextListElement):
    """General Motors "k" Diagnostic Object
    """

    def __init__(self,
                 diag_type: KDiagType,
                 text: str,
                 parent_offset: Optional[Union[str, int]],
                 rung: 'GmRung'):

        if diag_type is KDiagType.NA:
            raise ValueError('Cannot be NA!')

        if parent_offset is None:
            parent_offset = 0

        super().__init__(
            text=text,
            rung=rung
        )

        self.diag_type: KDiagType = diag_type
        self.parent_offset:   int = int(parent_offset)
        self._col_location = ''

    def __eq__(self, other):
        if isinstance(other, KDiag):
            return self.global_number == other.global_number
        return False

    def __hash__(self):
        return hash((
            self.text,
            self.diag_type.value,
            self.column_location,
            self.number,
            self.parent_offset
        ))

    def __repr__(self) -> str:
        return (
            f'KDiag(text={self.text}, '
            f'diag_type={self.diag_type}, '
            f'col_location={self.column_location}, '
            f'number={self.number}, '
            f'parent_offset={self.parent_offset}), '
            f'rung={self.rung}'
        )

    @property
    def column_location(self) -> str:
        if not self._col_location:
            self._get_col_location()
        return self._col_location

    @property
    def global_number(self) -> int:
        return self.number + self.parent_offset

    def _get_col_location(self) -> None:
        self._col_location = ''
        col_match = re.search(COLUMN_RE_PATTERN, self.text)
        if col_match:
            self._col_location = col_match.groups()[0]
            return


class GmPlcObject(
    RaPlcObject[META],
    Generic[META]
):
    """Gm Plc Object
    """

    @property
    def is_gm_owned(self) -> bool:
        return True if (
            self.name.lower().startswith(GM_CHAR)
            or self.name.lower().startswith(GM_SAFE_CHAR)
        ) else False

    @property
    def is_user_owned(self) -> bool:
        return True if (
            self.name.lower().startswith(USER_CHAR)
            or self.name.lower().startswith(USER_SAFE_CHAR)
        ) else False

    @property
    def process_name(self) -> str:
        if self.name.startswith(('CG_', 'zz_', 'sz_', 'zs_')):
            return self.name[3:]

        return self.name


class GmAddOnInstruction(
    GmPlcObject[dict],
    RaAddOnInstruction
):
    """General Motors AddOn Instruction Definition
    """


class GmDatatype(
    GmPlcObject[dict],
    RaDatatype
):
    """General Motors Datatype
    """


class GmModule(
    GmPlcObject[dict],
    RaModule
):
    """General Motors Module
    """


class GmRung(
    GmPlcObject[dict],
    RaRung
):
    """General Motors Rung
    """

    def __init__(
        self,
        meta_data: dict | None = None,
        routine: IRoutine | None = None,
        rung_number: int | str = 0,
        rung_text: str = '',
        comment: str = ''
    ) -> None:
        super().__init__(meta_data, routine, rung_number, rung_text, comment)
        self._kdiags: list[KDiag] = []

    @property
    def has_kdiag(self) -> bool:
        if not self.comment:
            return False

        return '<@DIAG>' in self.comment

    @property
    def kdiags(self) -> list[KDiag]:
        if not self._kdiags:
            self.get_kdiags()
        return self._kdiags

    @property
    def text_list_items(self) -> list[TextListElement]:
        if not self.comment:
            return []

        comment_lines = self.comment.splitlines()
        ret_list = []

        for line in comment_lines:
            match = re.match(TL_RE_PATTERN, line)
            if match:
                ret_list.append(TextListElement(match.groups()[0], self))

        return ret_list

    def get_kdiags(self) -> None:
        self._kdiags.clear()

        if not self.comment:
            return

        comment_lines = self.comment.splitlines()

        if not self.routine:
            raise ValueError("Routine is None")

        container = self.routine.get_container()
        if not container:
            raise ValueError("Routine container is None")

        if not isinstance(container, GmProgram):
            return

        for line in comment_lines:
            if fnmatch.fnmatch(line, ALARM_PATTERN):
                self._kdiags.append(
                    KDiag(
                        KDiagType.ALARM,
                        line,
                        container.parameter_offset,
                        self
                    )
                )

            elif fnmatch.fnmatch(line, PROMPT_PATTERN):
                self._kdiags.append(
                    KDiag(
                        KDiagType.PROMPT,
                        line,
                        container.parameter_offset,
                        self
                    )
                )


class GmRoutine(
    GmPlcObject[dict],
    RaRoutine
):
    """General Motors Routine
    """

    def __init__(
        self,
        meta_data: dict | str | None = None,
        name: str = '',
        description: str = '',
        **kwargs
    ) -> None:
        super().__init__(meta_data, name, description, **kwargs)
        self._kdiags: list[KDiag] = []

    @property
    def kdiags(self) -> list[KDiag]:
        if not self._kdiags:
            self.compile_kdiags()
        return self._kdiags

    @property
    def rungs(self) -> list[GmRung]:
        return super().rungs

    @property
    def text_list_items(self) -> list[TextListElement]:
        x = []
        for rung in self.rungs:
            x.extend(rung.text_list_items)
        return x

    def compile_kdiags(self) -> None:
        for rung in self.rungs:
            self._kdiags.extend(rung.kdiags)

    def invalidate(self) -> None:
        self._kdiags.clear()
        return super().invalidate()


class GmTag(
    GmPlcObject[dict],
    RaTag
):
    """General Motors Tag
    """


class GmProgram(
    GmPlcObject[dict],
    RaProgram
):
    """General Motors Program
    """
    PARAM_RTN_STR = 'B*_Parameters'

    PARAM_MATCH_STR = "MOV(*,HMI.Diag.Pgm.MsgOffset);"

    PGM_NAME_STR = "MOV(*,HMI.Diag.Pgm.Name.LEN)*"

    def __init__(
        self,
        meta_data: dict | str | None = None,
        name: str = '',
        description: str = '',
        **kwargs
    ) -> None:
        super().__init__(meta_data, name, description, **kwargs)
        self._kdiags: list[KDiag] = []

    @property
    def is_gm_owned(self) -> bool:
        return len(self.gm_routines) > 0

    @property
    def is_user_owned(self) -> bool:
        return len(self.user_routines) > 0

    @property
    def diag_name(self) -> str:
        if not self.parameter_routine:
            return ''

        diag_rung = None
        for rung in self.parameter_routine.rungs:
            match = re.search(DIAG_NAME_RE_PATTER, rung.text)
            if match:
                diag_rung = rung
                break
        if not diag_rung:
            return ''

        # Extract the length of the string
        length_match = re.search(r'MOV\((\d+),HMI\.Diag\.Pgm\.Name\.LEN\)', diag_rung.text)
        if length_match:
            string_length = int(length_match.group(1))
        else:
            raise ValueError("String length not found in the PLC code")

        # Extract the ASCII characters and their positions
        data_matches = re.findall(r'MOV\((kAscii\.\w+),HMI\.Diag\.Pgm\.Name\.DATA\[(\d+)\]\)', diag_rung.text)
        if not data_matches:
            raise ValueError("No ASCII characters found in the PLC code")

        # Create a dictionary to map ASCII positions to characters
        ascii_map = {
            'kAscii.A': 'A',
            'kAscii.B': 'B',
            'kAscii.C': 'C',
            'kAscii.D': 'D',
            'kAscii.E': 'E',
            'kAscii.F': 'F',
            'kAscii.G': 'G',
            'kAscii.H': 'H',
            'kAscii.I': 'I',
            'kAscii.J': 'J',
            'kAscii.K': 'K',
            'kAscii.L': 'L',
            'kAscii.M': 'M',
            'kAscii.N': 'N',
            'kAscii.O': 'O',
            'kAscii.P': 'P',
            'kAscii.Q': 'Q',
            'kAscii.R': 'R',
            'kAscii.S': 'S',
            'kAscii.T': 'T',
            'kAscii.U': 'U',
            'kAscii.V': 'V',
            'kAscii.W': 'W',
            'kAscii.X': 'X',
            'kAscii.Y': 'Y',
            'kAscii.Z': 'Z',
            'kAscii.a': 'a',
            'kAscii.b': 'b',
            'kAscii.c': 'c',
            'kAscii.d': 'd',
            'kAscii.e': 'e',
            'kAscii.f': 'f',
            'kAscii.g': 'g',
            'kAscii.h': 'h',
            'kAscii.i': 'i',
            'kAscii.j': 'j',
            'kAscii.k': 'k',
            'kAscii.l': 'l',
            'kAscii.m': 'm',
            'kAscii.n': 'n',
            'kAscii.o': 'o',
            'kAscii.p': 'p',
            'kAscii.q': 'q',
            'kAscii.r': 'r',
            'kAscii.s': 's',
            'kAscii.t': 't',
            'kAscii.u': 'u',
            'kAscii.v': 'v',
            'kAscii.w': 'w',
            'kAscii.x': 'x',
            'kAscii.y': 'y',
            'kAscii.z': 'z',
            'kAscii.n0': '0',
            'kAscii.n1': '1',
            'kAscii.n2': '2',
            'kAscii.n3': '3',
            'kAscii.n4': '4',
            'kAscii.n5': '5',
            'kAscii.n6': '6',
            'kAscii.n7': '7',
            'kAscii.n8': '8',
            'kAscii.n9': '9',
        }

        # Initialize the string with placeholders
        string_chars = [''] * string_length

        # Fill the string with the extracted characters
        for char, pos in data_matches:
            string_chars[int(pos)] = ascii_map.get(char, '?')

        # Join the characters to form the final string
        final_string = ''.join(string_chars)

        return final_string

    @property
    def diag_setup(self) -> dict:
        return {
            'program_name': self.name,
            'diag_name': self.diag_name,
            'msg_offset': self.parameter_offset,
            'hmi_tag': 'TBD',
            'program_type': self.program_type,
            'tag_alias_refs': 'TBD'
        }

    @property
    def kdiags(self) -> list[KDiag]:
        if not self._kdiags:
            self.compile_kdiags()
        return self._kdiags

    @property
    def parameter_offset(self) -> int:
        if not self.parameter_routine:
            return 0

        for rung in self.parameter_routine.rungs:
            if fnmatch.fnmatch(rung.text, self.PARAM_MATCH_STR):
                return int(rung.text.replace("MOV(", '').replace(',HMI.Diag.Pgm.MsgOffset);', ''))
        return 0

    @property
    def parameter_routine(self) -> Optional[GmRoutine]:
        for routine in self.routines:
            if fnmatch.fnmatch(routine.name, self.PARAM_RTN_STR):
                return routine
        return None

    @property
    def program_type(self) -> KDiagProgramType:
        return KDiagProgramType.NA

    @property
    def routines(self) -> list[GmRoutine]:
        return super().routines

    @property
    def text_list_items(self) -> list[TextListElement]:
        x = []
        for routine in self.routines:
            x.extend(routine.text_list_items)
        return x

    @property
    def gm_routines(self) -> list[GmRoutine]:
        return [x for x in self.routines if x.is_gm_owned]

    @property
    def user_routines(self) -> list[GmRoutine]:
        return [x for x in self.routines if x.is_user_owned]

    def compile_kdiags(self):
        """get all kdiags within program
        """
        for routine in self.routines:
            if not isinstance(routine, GmRoutine):
                raise ValueError('Routine is not a GmRoutine')

            self._kdiags.extend(routine.kdiags)

    def invalidate(self) -> None:
        self._kdiags.clear()
        return super().invalidate()


class GmController(
    GmPlcObject[dict],
    RaController
):
    """General Motors Plc Controller
    """

    generator_type = 'GmEmulationGenerator'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._kdiags = []

    @property
    def kdiags(self) -> list[KDiag]:
        if not self._kdiags:
            self.compile_kdiags()
        return self._kdiags

    @property
    def mcp_program(self) -> Optional[IProgram]:
        return self.programs.get('MCP', None)

    @property
    def safety_common_program(self) -> Optional[GmProgram]:
        """Get the safety common program if it exists
        """
        return self.programs.get('s_Common', None)

    @property
    def text_list_items(self) -> list[TextListElement]:
        x = []
        for program in self.programs:
            x.extend(program.text_list_items)
        return x

    @property
    def gm_programs(self) -> list[GmProgram]:
        return [x for x in self.programs if x.is_gm_owned]

    @property
    def user_program(self) -> list[GmProgram]:
        return [x for x in self.programs if x.is_user_owned]

    def compile_kdiags(self):
        """get all kdiags within controller
        """
        if self._kdiags:
            return

        for program in self.programs:
            if not isinstance(program, GmProgram):
                raise ValueError('Program is not a GmProgram')
            self._kdiags.extend(program.kdiags)

    def extract_messages(self):
        tl_items = self.text_list_items
        filtered = {}

        for item in tl_items:
            if item.text_list_id not in filtered:
                filtered[item.text_list_id] = []
            filtered[item.text_list_id].append(item)

        return {
            'text_lists': tl_items,
            'filtered': filtered,
            'duplicates': 'Fix This Method',
            'programs': [x.diag_setup for x in self.programs]
        }

    def invalidate(self) -> None:
        self._kdiags.clear()
        return super().invalidate()

    def validate_text_lists(self):
        """validate all text lists within controller
        """
        duplicate_diags = 'Fix This Method'

        return duplicate_diags


GmPlcObject.supporting_class = GmController
