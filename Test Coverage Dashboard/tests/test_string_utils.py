from sample_codebase import string_utils


def test_reverse_string():
    assert string_utils.reverse_string("hello") == "olleh"


def test_capitalize_words():
    assert string_utils.capitalize_words("hello world") == "Hello World"
