import re
import pytest
import logging
from structifytext import parser
from cStringIO import StringIO
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@pytest.fixture(scope='module')
def mock_chunky_data(request):
    output = "Some Identifiable Chunk Start:\r\n"
    output += "Some chunk content 1\r\n"
    output += "Some more chunk content 1\r\n"
    output += "Some Other Identifiable Chunk Start:\r\n"
    output += "Some chunk content 2\r\n"
    output += "Some more chunk content 2\r\n"
    return output

def test_can_compile_regex():
    regex = parser._compile_regex('message', '(\S+)')
    re.purge()
    expected_regex = re.compile('(\S+)')
    assert isinstance(regex, expected_regex.__class__)
    assert regex.pattern == expected_regex.pattern


def test_value_not_regex_string_raises_exception():
    with pytest.raises(TypeError):
        parser._compile_regex('message', 123)
    with pytest.raises(TypeError):
        parser._compile_regex('message', ['(\S+)'])
    with pytest.raises(TypeError):
        parser._compile_regex('message', re.compile('(\S+)'))


def test_index_of_matches():
    lines = ['a', 'b', 'c', 'c', 'c']
    regex = re.compile('a|c')
    matches = filter(regex.search, lines)
    expected_indexes = [0,2]
    result_indexes = parser._index_of_matches(matches, lines)
    assert expected_indexes == result_indexes


def test_parse_regex_expect_string():
    lines = ["Hello","World"]
    result = parser._parse_regex(lines, 'somekey', '(World)')
    expected_result = 'World'
    assert result == expected_result


def test_parse_regex_force_list():
    lines = ["Hello","World"]
    result = parser._parse_regex(lines, 'somekey', '(World)', return_list=True)
    expected_result = ['World']
    assert result == expected_result


def test_parse_regex_expect_list():
    lines = ["Hello","World", "world"]
    result = parser._parse_regex(lines, 'somekey', '(?i)(World)', return_list=True)
    expected_result = ['World', "world"]
    assert result == expected_result


def test_parse_regex_expect_none():
    lines = ["Hello","World", "world"]
    result = parser._parse_regex(lines, 'somekey', '(?i)(Cheese)', return_list=True)
    assert result is None



def test_value_without_group_raises_exception():
    lines = ["Hello", "World"]
    with pytest.raises(ValueError):
        parser._parse_regex(lines, 'somekey', 'World')


def test_value_with_two_groups_raises_warning():
    lines = ["Hello", "World"]
    with pytest.warns(UserWarning):
        parser._parse_regex(lines, 'somekey', '(.*)\S+(.*)')


def test_do_chunk_lines(mock_chunky_data):
    lines = StringIO(mock_chunky_data).readlines()
    match_indexes = [0, 3]
    expected_chunks = [lines[0:3], lines[3::]]
    chunks = parser._do_chunk_lines(lines, match_indexes)
    assert chunks == expected_chunks


def test_do_chunk_lines_force_block_end(mock_chunky_data):
    lines = StringIO(mock_chunky_data).readlines()
    match_indexes = [0,3]
    force_block_end_index = 4
    expected_chunks = [lines[0:4]]
    chunks = parser._do_chunk_lines(lines, match_indexes, force_block_end_index)
    assert chunks == expected_chunks


def test_chunk_lines_by_id(mock_chunky_data):
    lines = StringIO(mock_chunky_data).readlines()
    struct = {'id': '(Chunk\sStart)'}
    expected_chunks = [lines[0:3], lines[3::]]
    chunks = parser._chunk_lines(lines, struct)
    assert chunks == expected_chunks


def test_chunk_lines_by_block_start(mock_chunky_data):
    lines = StringIO(mock_chunky_data).readlines()
    struct = {'block_start': '(Chunk\sStart)'}
    expected_chunks = [lines[0:3], lines[3::]]
    chunks = parser._chunk_lines(lines, struct)
    assert chunks == expected_chunks


def test_chunk_lines_force_break_end(mock_chunky_data):
    lines = StringIO(mock_chunky_data).readlines()
    struct = {'block_start': '(Chunk\sStart)', 'block_end': '(chunk content 2)'}
    expected_chunks = [lines[0:4]]
    chunks = parser._chunk_lines(lines, struct)
    assert chunks == expected_chunks


def test_chunk_lines_no_match_returns_none(mock_chunky_data):
    lines = StringIO(mock_chunky_data).readlines()
    struct = {'block_start': '(Elephant)'}
    chunks = parser._chunk_lines(lines, struct)
    assert chunks is None


def test_chunk_lines_no_id_or_block_start_raises_exception(mock_chunky_data):
    lines = StringIO(mock_chunky_data).readlines()
    struct = {'yo': '(Chunk\sStart)'}
    with pytest.raises(KeyError):
        parser._chunk_lines(lines, struct)


def test_chunk_lines_no_block_end_match_raises_warning(mock_chunky_data):
    lines = StringIO(mock_chunky_data).readlines()
    struct = {'block_start': '(Chunk\sStart)', 'block_end': '(Elephant)'}
    expected_chunks = [lines[0:3], lines[3::]]
    with pytest.warns(UserWarning):
        chunks = parser._chunk_lines(lines, struct)
        assert chunks == expected_chunks


def test_parse_dict_simple():
    lines = ['The','value is: 10']
    struct = {'somekey': 'value\sis:\s(\d+)'}
    parsed = parser._parse_dict(struct, lines)
    expected_output = {'somekey': '10'}
    assert parsed == expected_output


def test_parse_dict_with_id(mock_chunky_data):
    lines = StringIO(mock_chunky_data).readlines()
    struct = {'id': '(Chunk\sStart)', 'content_no': 'Some\schunk\scontent\s(\d)'}
    parsed = parser._parse_dict(struct, lines)
    expected_output = {'id': 'Chunk Start', 'content_no': '1'}
    assert parsed == expected_output


def test_parse_dict_with_block_start(mock_chunky_data):
    lines = StringIO(mock_chunky_data).readlines()
    struct = {'block_start': '(Chunk\sStart)', 'content_no': 'Some\schunk\scontent\s(\d)'}
    parsed = parser._parse_dict(struct, lines)
    expected_output = {'content_no': '1'}
    assert parsed == expected_output


def test_parse_dict_return_list(mock_chunky_data):
    lines = StringIO(mock_chunky_data).readlines()
    struct = {'block_start': '(Chunk\sStart)', 'content_no': 'Some\schunk\scontent\s(\d)'}
    parsed = parser._parse_dict(struct, lines, return_list=True)
    expected_output = [{'content_no': '1'}, {'content_no': '2'}]
    assert parsed == expected_output


def test_parse_dict_return_none(mock_chunky_data):
    lines = StringIO(mock_chunky_data).readlines()
    struct = {'block_start': '(Chunk\sEnd)', 'content_no': 'Some\schunk\scontent\s(\d)'}
    parsed = parser._parse_dict(struct, lines)
    assert parsed is None


def test_parse_list_simple():
    lines = ["The count says: 1", "The count says: 2", "The count says: 3",
             "The count says: 4", "The count says: 5"]
    parsed = parser._parse_list('count', ['(\d)'], lines)
    expected_output = ['1', '2', '3', '4', '5']
    assert parsed == expected_output


def test_parse_list_with_dictionary():
    lines = ["The count says: 1", "The count says: 2", "The count says: 3",
             "The count says: 4", "The count says: 5"]
    struct = [{'id': '(\d)'}]
    parsed = parser._parse_list('id', struct, lines)
    expected_output = [{'id': '1'}, {'id': '2'}, {'id': '3'}, {'id': '4'}, {'id': '5'}]
    assert parsed == expected_output


def test_parse_returns_none():
    lines = ["The count says: 1", "The count says: 2", "The count says: 3",
             "The count says: 4", "The count says: 5"]
    parsed_list = parser._parse_list('count', ['(elephant)'], lines)
    assert parsed_list is None
    parsed_dict = parser._parse_list('id', [{'id': '(elephant)'}], lines)
    assert parsed_dict is None

