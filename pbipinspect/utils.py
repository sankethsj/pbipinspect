
from collections import defaultdict
import re
from typing import Any


def get_regex_group(
    x: str, 
    pattern: str | re.Pattern[str],
    group: int = 1,
    if_none: Any = None
) -> Any:
    """
    Extracts a specified group from a regex match within a given string.

    Parameters
    ----------
    x : str
        The input string to search for the regex pattern.
    pattern : str or re.Pattern
        The regex pattern used to search within the input string.
    group : int, optional
        The group number to extract from the match, defaults to 1.
    if_none : Any, optional
        The value to return if no match is found, defaults to None.

    Returns
    -------
    Any
        The specified regex group if a match is found, otherwise returns `if_none`.
    """

    match = re.search(pattern, x)
    if match is None:
        return if_none
    return match.group(group)

def check_lines_max_length(x: str, max_length: int) -> list[tuple[str, str]]:
    """
    Checks if any line in a given string exceeds the maximum length.

    Parameters
    ----------
    x : str
        The input string to check.
    max_length : int
        The maximum length of a line.

    Returns
    -------
    list[tuple[str, str]]
        A list of tuples, where the first element of the tuple is the line
        number (1-indexed) and the second element is the line itself, if the
        line exceeds the maximum length. If no lines exceed the maximum length,
        an empty list is returned.
    """
    lines = x.split('\n')
    len_check = [
        (str(i + 1), x) 
        for i, x in enumerate(lines) 
        if len(x) > max_length
    ]
    return len_check

def quote_and_join(strings: list[str], sep=', '):
    """
    Joins a list of strings with a separator, single-quoting each string.

    Parameters
    ----------
    strings : list[str]
        The list of strings to join.
    sep : str, optional
        The separator to use when joining the strings, defaults to ', '.

    Returns
    -------
    str
        The joined string.
    """
    return sep.join(f"'{s}'" for s in strings)

def smart_join(strings: list[str]):
    """
    Joins a list of strings into a single string formatted in a human-readable way.

    Parameters
    ----------
    strings : list[str]
        The list of strings to join.

    Returns
    -------
    str
        A single string with the elements joined. If the list is empty, returns an 
        empty string. If there is one element, returns the element quoted. If there 
        are two elements, joins them with 'and'. For more than two elements, joins 
        all but the last with commas, and the last with 'and'.
    """
    if not strings:
        return ''
    elif len(strings) == 1:
        return f"'{strings[0]}'"
    elif len(strings) == 2:
        return quote_and_join(strings, ' and ')
    else:
        return quote_and_join(strings[:-1], ', ') + ' and ' + f"'{strings[-1]}'"

def sanitize_id(text: str) -> str:
    """
    Transforms a given string into a valid Markdown-friendly ID.
    
    - Converts to lowercase
    - Replaces spaces with hyphens
    - Removes special characters except hyphens and alphanumerics
    
    Parameters
    ----------
    text : str
        The string to sanitize
    
    Returns
    -------
    str
        The sanitized string
    """
    text = text.lower() 
    text = re.sub(r'\s+', '-', text)
    text = re.sub(r'[^a-z0-9\-]', '', text)
    return text

def fix_duplicate_ids(text: str) -> str:
    """
    Finds duplicate HTML id attributes and markdown links (e.g. [text](#id))
    and fixes them so that each occurrence is unique.

    For HTML tag attributes (like id="Duplicate"), the first occurrence remains
    unchanged, the second becomes "Duplicate1", the third "Duplicate2", etc.

    For markdown links, we assume that the intended target should follow the
    same order. For example, the first markdown link referencing "#Duplicate" will
    be changed to point to the first occurrence (i.e. "#Duplicate"), the second will
    be changed to "#Duplicate1", etc.

    Code blocks (demarcated by "```") are left unmodified.

    Parameters
    ----------
    text : str
        The rendered text to fix duplicate ids and markdown links in.

    Returns
    -------
    str
        The rendered text with duplicate ids and markdown links fixed.
    """
    id_mapping = defaultdict(list)
    counts: dict = defaultdict(int)
    link_counts: dict = defaultdict(int)

    id_attr_pattern = re.compile(r'(\bid=")([^"]+)(")')
    md_link_pattern = re.compile(r'(\]\(#)([^)]+)(\))')

    def replace_html_id(match):
        prefix, orig_id, suffix = match.groups()
        cnt = counts[orig_id]
        new_id = orig_id if cnt == 0 else f"{orig_id}{cnt}"
        counts[orig_id] += 1
        id_mapping[orig_id].append(new_id)
        return f'{prefix}{new_id}{suffix}'

    def replace_md_link(match):
        prefix, orig_id, suffix = match.groups()
        if orig_id not in id_mapping or not id_mapping[orig_id]:
            return match.group(0)
        cnt = link_counts[orig_id]
        if cnt < len(id_mapping[orig_id]):
            new_target = id_mapping[orig_id][cnt]
        else:
            new_target = id_mapping[orig_id][0]
        link_counts[orig_id] += 1
        return f'{prefix}{new_target}{suffix}'

    code_block_pattern = re.compile(r'(```[\s\S]*?```)', re.MULTILINE)
    segments = code_block_pattern.split(text)

    for i, segment in enumerate(segments):
        if i % 2 == 0:
            segment = id_attr_pattern.sub(replace_html_id, segment)
            segment = md_link_pattern.sub(replace_md_link, segment)
            segments[i] = segment

    fixed_text = "".join(segments)
    return fixed_text
