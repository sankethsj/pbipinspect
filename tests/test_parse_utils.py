
from pbipinspect.parse.utils import remove_doc_comments

def test_remove_doc_comment():
    input_str = "/* @doc This is a doc comment */ Hello World"
    expected_output = "Hello World"
    assert remove_doc_comments(input_str) == expected_output

def test_no_removal_of_string_without_comments():
    input_str = "Hello World"
    expected_output = "Hello World"
    assert remove_doc_comments(input_str) == expected_output

def test_removal_of_doc_comment_with_newline_characters():
    input_str = "/* @doc This is a doc comment\nwith multiple lines */ Hello World"
    expected_output = "Hello World"
    assert remove_doc_comments(input_str) == expected_output
