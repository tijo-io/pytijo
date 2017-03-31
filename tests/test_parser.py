import os
import ast
import pytest
import logging
from structifytext import parser
from cStringIO import StringIO

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@pytest.fixture(scope='module')
def mock_struct(request):
    return {
        'tables': [
            {
                'id': '\[TABLE (\d{1,2})\]',
                'flows': [
                    {
                        'id': '\[FLOW_ID(\d+)\]',
                        'timestamp': 'Timestamp\s+=\s+(.+)'
                    }
                ]
            }
        ]
    }


@pytest.fixture(scope='module')
def mock_group_struct(request):
    return {
        'groups': [
            {
                'id': 'Group id:\s+(\d+)',
                'ref_count': 'Reference count:\s+(\d+)',
                'packet_count': 'Packet count:\s+(\d+)',
                'byte_count': 'Byte count:\s+(\d+)',
                'bucket': [
                    {
                        'id': 'Bucket\s+(\d+)',
                        'packet_count': 'Packet count:\s+(\d+)',
                        'byte_count': 'Byte count:\s+(\d+)',
                    }
                ]
            }
        ]
    }


def read(filename):
    output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    with open(output_file, 'r') as fin:
        return fin.read()


def test_simple_struct():
    struct = { 'message': '(.*)' }
    lines = ["Hello World"]
    expected_output = { 'message': "Hello World" }
    parsed = parser.parse_struct(lines, struct)
    assert parsed == expected_output


def test_simple_list():
    struct = { 'count': ['(\d)'] }
    lines = ["The count says: 1", "The count says: 2", "The count says: 3",
             "The count says: 4", "The count says: 5"]
    expected_output = { 'count': [1,2,3,4,5] }
    parsed = parser.parse_struct(lines, struct)
    # For now we need to convert to type after parsing
    parsed = {'count': map(int, parsed['count'])}
    assert parsed == expected_output


def test_flows(mock_struct):
    lines = StringIO(read('./flow_output.txt')).readlines()
    expected_output = ast.literal_eval(read('./flow_output_parsed.txt'))
    parsed = parser.parse_struct(lines, mock_struct)
    assert parsed == expected_output


def test_groups(mock_group_struct):
    lines = StringIO(read('./group_output.txt')).readlines()
    expected_output = ast.literal_eval(read('./group_output_parsed.txt'))
    parsed = parser.parse_struct(lines, mock_group_struct)
    assert parsed == expected_output


def test_value_not_regex_string_raises_exception():
    struct = {'message': 123}
    lines = ["Hello World"]
    with pytest.raises(TypeError):
        parser.parse_struct(lines, struct)


def test_value_without_group_raises_exception():
    struct = {'message': 'ab'}
    lines = ["Hello World"]
    with pytest.raises(ValueError):
        parser.parse_struct(lines, struct)


def test_value_with_two_groups_raises_warning():
    struct = {'message': '(.*)\S+(.*)'}
    lines = ["Hello World"]
    with pytest.raises(UserWarning):
        parser.parse_struct(lines, struct)


def test_list_with_dict_no_id_raises_exception():
    struct = {'letter': [{'to': 'Dear\s+(\w+)', 'from': 'Regards,\s+(\w+)'}]}
    letter = "Dear Einstein,\r\n"
    letter += "I am become Death, the destroyer of worlds.\r\n"
    letter += "And it's all your fault!\r\n"
    letter += "Regards, Oppenheimer\r\n"
    lines = StringIO(letter).readlines()
    logger.debug(lines)
    with pytest.raises(KeyError):
        parser.parse_struct(lines, struct)
