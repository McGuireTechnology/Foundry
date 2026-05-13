from ulid import new as new_ulid


def generate_ulid() -> str:
    return str(new_ulid())
