
def required(value: str, label: str) -> None:
    if not value or not value.strip():
        raise ValueError(f'{label} is required')


def min_length(value: str, length: int, label: str) -> None:
    if len(value) < length:
        raise ValueError(f'{label} must be at least {length} characters')
