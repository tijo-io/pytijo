import re
import pytest
from pytijo import parser


@pytest.fixture(scope="module")
def mock_chunky_data(request):
    output = "Some Identifiable Chunk Start:\r\n"
    output += "Some chunk content 1\r\n"
    output += "Some more chunk content 1\r\n"
    output += "Some Other Identifiable Chunk Start:\r\n"
    output += "Some chunk content 2\r\n"
    output += "Some more chunk content 2\r\n"
    return output


@pytest.fixture(scope="module")
def mock_chunky_single_line_data(request):
    output = "Some Identifiable Chunk Start: "
    output += "Some chunk content 1 "
    output += "Some more chunk content 1 "
    output += "Some Other Identifiable Chunk Start: "
    output += "Some chunk content 2 "
    output += "Some more chunk content 2 "
    return output


def test_can_compile_regex():
    regex = parser._compile_regex("message", r"(\S+)")
    re.purge()
    expected_regex = re.compile(r"(\S+)")
    assert isinstance(regex, expected_regex.__class__)
    assert regex.pattern == expected_regex.pattern


def test_value_not_regex_string_raises_exception():
    with pytest.raises(TypeError):
        parser._compile_regex("message", 123)
    with pytest.raises(TypeError):
        parser._compile_regex("message", [r"(\S+)"])
    with pytest.raises(TypeError):
        parser._compile_regex("message", re.compile(r"(\S+)"))


def test_chunk_lines_by_id(mock_chunky_data):
    struct = {"#id": r"(Chunk\sStart)"}
    expected_chunks = [
        "Chunk Start:\r\nSome chunk content 1\r\nSome more chunk content 1\r\nSome Other Identifiable ",
        "Chunk Start:\r\nSome chunk content 2\r\nSome more chunk content 2\r\n",
    ]
    chunks = parser._chunk_lines(mock_chunky_data, struct)
    assert chunks == expected_chunks


def test_chunk_single_line_by_id(mock_chunky_single_line_data):
    struct = {"#id": r"(Chunk\sStart)"}
    expected_chunks = [
        "Chunk Start: Some chunk content 1 Some more chunk content 1 Some Other Identifiable ",
        "Chunk Start: Some chunk content 2 Some more chunk content 2 ",
    ]
    chunks = parser._chunk_lines(mock_chunky_single_line_data, struct)
    assert chunks == expected_chunks


def test_chunk_lines_by_block_start(mock_chunky_data):
    struct = {"#start": r"(Chunk\sStart)"}
    expected_chunks = [
        "Chunk Start:\r\nSome chunk content 1\r\nSome more chunk content 1\r\nSome Other Identifiable ",
        "Chunk Start:\r\nSome chunk content 2\r\nSome more chunk content 2\r\n",
    ]
    chunks = parser._chunk_lines(mock_chunky_data, struct)
    assert chunks == expected_chunks


def test_chunk_lines_single_line_by_block_start(mock_chunky_single_line_data):
    struct = {"#start": r"(Chunk\sStart)"}
    expected_chunks = [
        "Chunk Start: Some chunk content 1 Some more chunk content 1 Some Other Identifiable ",
        "Chunk Start: Some chunk content 2 Some more chunk content 2 ",
    ]
    chunks = parser._chunk_lines(mock_chunky_single_line_data, struct)
    assert chunks == expected_chunks


def test_chunk_lines_force_break_end(mock_chunky_data):
    struct = {"#start": r"(Chunk\sStart)", "#end": r"(chunk content 2)"}
    expected_chunks = [
        "Chunk Start:\r\nSome chunk content 1\r\nSome more chunk content 1\r\nSome Other Identifiable Chunk Start:\r\nSome chunk content 2"
    ]
    chunks = parser._chunk_lines(mock_chunky_data, struct)
    assert chunks == expected_chunks


def test_chunk_lines_no_match_returns_none(mock_chunky_data):
    struct = {"#start": r"(Elephant)"}
    chunks = parser._chunk_lines(mock_chunky_data, struct)
    assert chunks is None


def test_chunk_lines_no_id_or_block_start_raises_exception(mock_chunky_data):
    struct = {"yo": r"(Chunk\sStart)"}
    with pytest.raises(KeyError):
        parser._chunk_lines(mock_chunky_data, struct)


# TODO decide if #end does not but #start does
def test_chunk_lines_no_block_end_match_raises_warning(mock_chunky_data):
    struct = {"#start": r"(Chunk\sStart)", "#end": r"(Elephant)"}
    expected_chunks = None
    # with pytest.warns(UserWarning):
    chunks = parser._chunk_lines(mock_chunky_data, struct)
    assert chunks == expected_chunks


def test_parse_dict_simple():
    text = "The\nvalue is: 10"
    struct = {"somekey": r"value\sis:\s(\d+)"}
    parsed = parser._parse_dict(struct, text)
    expected_output = {"somekey": "10"}
    assert parsed == expected_output


def test_parse_dict_with_id(mock_chunky_data):
    struct = {"#id": r"(Chunk\sStart)", "content_no": r"Some\schunk\scontent\s(\d)"}
    parsed = parser._parse_dict(struct, mock_chunky_data)
    expected_output = {"id": "Chunk Start", "content_no": "1"}
    assert parsed == expected_output


def test_parse_dict_with_block_start(mock_chunky_data):
    struct = {"#start": r"(Chunk\sStart)", "content_no": r"Some\schunk\scontent\s(\d)"}
    parsed = parser._parse_dict(struct, mock_chunky_data)
    expected_output = {"content_no": "1"}
    assert parsed == expected_output


def test_parse_dict_return_list(mock_chunky_data):
    struct = {"#start": r"(Chunk\sStart)", "content_no": r"Some\schunk\scontent\s(\d)"}
    parsed = parser._parse_dict(struct, mock_chunky_data, return_list=True)
    expected_output = [{"content_no": "1"}, {"content_no": "2"}]
    assert parsed == expected_output


def test_parse_dict_return_none(mock_chunky_data):
    struct = {"#start": r"(Chunk\sEnd)", "content_no": r"Some\schunk\scontent\s(\d)"}
    parsed = parser._parse_dict(struct, mock_chunky_data)
    assert parsed is None


def test_parse_list_simple():
    lines = [
        "The count says: 1",
        "The count says: 2",
        "The count says: 3",
        "The count says: 4",
        "The count says: 5",
    ]
    parsed = parser._parse_dict({"count": [r"(\d)"]}, lines)
    expected_output = {"count": ["1", "2", "3", "4", "5"]}
    assert parsed == expected_output


def test_parse_list_with_dictionary():
    lines = [
        "The count says: 1",
        "The count says: 2",
        "The count says: 3",
        "The count says: 4",
        "The count says: 5",
    ]
    struct = {"id": [{"#id": r"(\d)"}]}
    parsed = parser._parse_dict(struct, lines)
    expected_output = {
        "id": [{"id": "1"}, {"id": "2"}, {"id": "3"}, {"id": "4"}, {"id": "5"}]
    }
    assert parsed == expected_output


def test_parse_returns_none():
    lines = [
        "The count says: 1",
        "The count says: 2",
        "The count says: 3",
        "The count says: 4",
        "The count says: 5",
    ]
    parsed_list = parser._parse_dict({"count": [r"(elephant)"]}, lines)
    assert parsed_list == {"count": None}
    parsed_dict = parser._parse_dict({"id": [{"#id": r"(elephant)"}]}, lines)
    assert parsed_dict == {"id": None}
