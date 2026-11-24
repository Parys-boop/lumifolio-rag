import re

# Códigos e quantidades curtas em português admitem conferência literal.
# "Um" e "uma" também são artigos e ficam fora da checagem.
NUMERAL = {
    "zero": "0", "dois": "2", "duas": "2", "três": "3", "quatro": "4",
    "cinco": "5", "seis": "6", "sete": "7", "oito": "8", "nove": "9", "dez": "10",
}
NUMBER = re.compile(r"\b(?:\d+(?:[.,]\d+)*|" + "|".join(NUMERAL) + r")\b")


def quantities(text: str) -> set[str]:
    return {NUMERAL.get(token, token) for token in NUMBER.findall(text.casefold())}
