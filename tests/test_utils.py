
import pytest
from pbipinspect.utils import (
    check_lines_max_length,
    fix_duplicate_ids,
    get_regex_group,
    quote_and_join,
    sanitize_id,
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

def test_sanitize_id_empty_string():
    assert sanitize_id("") == ""

def test_sanitize_id_spaces_only():
    assert sanitize_id("   ") == "-"

def test_sanitize_id_special_chars_only():
    assert sanitize_id("!@#$%^&*()") == ""

def test_sanitize_id_alphanumeric_and_spaces():
    assert sanitize_id("Hello World") == "hello-world"

def test_sanitize_id_alphanumeric_and_special_chars():
    assert sanitize_id("Hello!@# World$%^") == "hello-world"

def test_sanitize_id_hyphens():
    assert sanitize_id("hello-world") == "hello-world"

def test_fix_duplicate_ids_no_duplicates():
    input_text = """
    - [Unique](#Unique)
    
    <span id="Unique">Content</span>
    """
    expected = input_text
    output = fix_duplicate_ids(input_text)
    assert output == expected

def test_fix_duplicate_ids_html_duplicate_ids():
    input_text = """
    <span id="Test">First</span>
    <span id="Test">Second</span>
    <span id="Test">Third</span>
    """
    expected = """
    <span id="Test">First</span>
    <span id="Test1">Second</span>
    <span id="Test2">Third</span>
    """
    output = fix_duplicate_ids(input_text)
    assert " ".join(output.split()) == " ".join(expected.split())

def test_fix_duplicate_ids_markdown_links_only():
    input_text = """
    - [Link One](#LinkTest)
    - [Link Two](#LinkTest)

    <span id="LinkTest">Content One</span>
    <span id="LinkTest">Content Two</span>
    """
    expected = """
    - [Link One](#LinkTest)
    - [Link Two](#LinkTest1)

    <span id="LinkTest">Content One</span>
    <span id="LinkTest1">Content Two</span>
    """
    output = fix_duplicate_ids(input_text)
    assert " ".join(output.split()) == " ".join(expected.split())

def test_fix_duplicate_ids_mixed_duplicates():
    input_text = """
    - [Overview](#Overview)
    - [Duplicate](#Duplicate)
    - [Duplicate](#Duplicate)
    
    <span id="Overview">Overview Content</span>
    <span id="Duplicate">First Duplicate Content</span>
    <span id="Duplicate">Second Duplicate Content</span>
    
    In the text, here's another [Duplicate](#Duplicate) link.
    """
    expected = """
    - [Overview](#Overview)
    - [Duplicate](#Duplicate)
    - [Duplicate](#Duplicate1)
    
    <span id="Overview">Overview Content</span>
    <span id="Duplicate">First Duplicate Content</span>
    <span id="Duplicate1">Second Duplicate Content</span>
    
    In the text, here's another [Duplicate](#Duplicate) link.
    """
    output = fix_duplicate_ids(input_text)
    assert " ".join(output.split()) == " ".join(expected.split())

def test_fix_duplicate_ids_markdown_link_with_no_matching_html():
    input_text = """
    - [NoMatch](#NoMatch)
    
    <span id="SomeOtherId">Content</span>
    """
    expected = input_text
    output = fix_duplicate_ids(input_text)
    assert " ".join(output.split()) == " ".join(expected.split())

def test_fix_duplicate_ids_code_blocks_not_modified():
    input_text = (
        "Some text with duplicate id: <div id=\"Duplicate\"></div> and <div id=\"Duplicate\"></div>.\n\n"
        "```html\n"
        "<div id=\"Duplicate\"></div>\n"
        "<div id=\"Duplicate\"></div>\n"
        "```\n"
    )
    expected_output = (
        "Some text with duplicate id: <div id=\"Duplicate\"></div> and <div id=\"Duplicate1\"></div>.\n\n"
        "```html\n"
        "<div id=\"Duplicate\"></div>\n"
        "<div id=\"Duplicate\"></div>\n"
        "```\n"
    )

    output_text = fix_duplicate_ids(input_text)
    assert output_text == expected_output
