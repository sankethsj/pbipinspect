
import pytest
from pbipinspect.utils import (
    check_lines_max_length,
    get_regex_group,
    quote_and_join,
    smart_join,
)
import re

def test_get_regex_group_valid_pattern():
    x = "Hello, world!"
    pattern = "(world)"
    result = get_regex_group(x, pattern)
    assert result == "world"

def test_get_regex_group_invalid_pattern():
    x = "Hello, world!"
    pattern = "["
    with pytest.raises(re.error):
        get_regex_group(x, pattern)

def test_get_regex_group_non_existent_group():
    x = "Hello, world!"
    pattern = "world"
    with pytest.raises(IndexError):
        get_regex_group(x, pattern) is None

def test_get_regex_group_if_none():
    x = "Hello, world!"
    pattern = "foo"
    if_none = "default"
    result = get_regex_group(x, pattern, if_none=if_none)
    assert result == "default"

def test_check_lines_max_length_empty_string():
    assert check_lines_max_length("", 10) == []

def test_check_lines_max_length_not_exceeding_max_length():
    assert check_lines_max_length("a\nb\nc", 2) == []

def test_check_lines_max_length_exceeding_max_length():
    assert check_lines_max_length("123456789\nabcdefg\n1234567890", 8) == [
        ("1", "123456789"),
        ("3", "1234567890")
    ]

def test_quote_and_join_empty_list():
    assert quote_and_join([], ', ') == ''

def test_quote_and_join_single_string():
    assert quote_and_join(['hello'], ', ') == "'hello'"

def test_quote_and_join_multiple_strings():
    assert quote_and_join(['hello', 'world'], ', ') == "'hello', 'world'"

def test_quote_and_join_custom_separator():
    assert quote_and_join(['hello', 'world'], ' | ') == "'hello' | 'world'"

def test_smart_join_empty_list():
    assert smart_join([]) == ''

def test_smart_join_single_element():
    assert smart_join(['hello']) == "'hello'"

def test_smart_join_two_elements():
    assert smart_join(['hello', 'world']) == "'hello' and 'world'"

def test_smart_join_multiple_elements():
    assert smart_join(['hello', 'world', 'foo', 'bar']) == "'hello', 'world', 'foo' and 'bar'"
