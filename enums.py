from enum import Enum

class SexoEnum(str, Enum):
    FEMININO = "F"
    MASCULINO = "M"
    OUTROS = "O"
    PREFIRO_NAO_DIZER = "P"

class EstadoCivilEnum(str, Enum):
    SOLTEIRO = "1"
    CASADO = "2"
    VIUVO = "3"
    DIVORCIADO = "4"
    SEPARADO = "5"

class RespostaEnum(str, Enum):
    SIM = "S"
    NAO = "N"
