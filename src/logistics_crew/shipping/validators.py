import re

CEP_PATTERN = re.compile(r"^\d{5}-?\d{3}$")
TRACKING_PATTERN = re.compile(r"^BR\d{9}BR$")


def normalize_cep(value: str) -> str:
    digits = value.replace("-", "")
    if len(digits) != 8 or not digits.isdigit():
        raise ValueError("CEP must be 8 digits, optional hyphen (e.g. 01310-000)")
    return f"{digits[:5]}-{digits[5:]}"


def validate_weight_kg(weight_kg: float) -> None:
    if weight_kg <= 0:
        raise ValueError("weight_kg must be greater than zero")


def validate_tracking_id(tracking_id: str) -> None:
    if not TRACKING_PATTERN.match(tracking_id):
        raise ValueError("tracking_id must match pattern BR#########BR")
