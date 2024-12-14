
import re
from typing import Any

def get_regex_group(
    x: str, 
    pattern: str | re.Pattern[str],
    group: int = 1,
    if_none: Any = None
) -> Any:
    match = re.search(pattern, x)
    if match is None:
        return if_none
    return match.group(group)

def check_lines_max_length(x: str, max_length: int) -> list[tuple[str, str]]:
    lines = x.split('\n')
    len_check = [
        (str(i + 1), x) 
        for i, x in enumerate(lines) 
        if len(x) > max_length
    ]
    return len_check

def quote_and_join(strings: list[str], sep=', '):
    return sep.join(f"'{s}'" for s in strings)

def smart_join(strings: list[str]):
    if not strings:
        return ''
    elif len(strings) == 1:
        return f"'{strings[0]}'"
    elif len(strings) == 2:
        return quote_and_join(strings, ' and ')
    else:
        return quote_and_join(strings[:-1], ', ') + ' and ' + f"'{strings[-1]}'"
