import builtins
import importlib
import re
from datetime import timedelta


def parse_timedelta(time_str):
    # Regex to capture days, hours, minutes, and seconds
    regex = re.compile(r'((?P<days>\d+)d)?\s?((?P<hours>\d+)h)?\s?((?P<minutes>\d+)m)?\s?((?P<seconds>\d+)s)?')
    parts = regex.match(time_str)
    if not parts:
        return None

    # Filter out None values and convert to integers
    time_params = {name: int(param) for name, param in parts.groupdict().items() if param}
    return timedelta(**time_params)


def resolve_type(type_name: str) -> type:
    if type_name is None:
        raise ValueError("type_name cannot be None")

    name = type_name.strip()
    if name == "":
        raise ValueError("type_name cannot be empty")

    # Fast-path for common builtins.
    builtin_type = getattr(builtins, name, None)
    if isinstance(builtin_type, type):
        return builtin_type

    # Support fully qualified paths, e.g. datetime.datetime.
    if "." in name:
        module_name, attr_name = name.rsplit(".", 1)
        module = importlib.import_module(module_name)
        resolved = getattr(module, attr_name)
        if isinstance(resolved, type):
            return resolved
        raise TypeError(f"{name!r} resolves to a non-type value")

    raise ValueError(
        f"Unknown type name: {type_name!r}. "
        f"Use a builtin type name (e.g. 'int') or a fully qualified path (e.g. 'datetime.datetime')."
    )
