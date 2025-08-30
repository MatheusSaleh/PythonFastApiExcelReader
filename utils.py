from enum import Enum

def parse_enum(value: str, enum_class: Enum):
    """
    Converte uma string para o valor do Enum correspondente.
    Retorna None se não existir correspondência.
    """
    if value is None:
        return None
    try:
        return enum_class[value.strip().upper()]
    except KeyError:
        # tenta comparar pelo valor do Enum (não pelo nome)
        for item in enum_class:
            if str(item.value).strip().upper() == value.strip().upper():
                return item
    return None
