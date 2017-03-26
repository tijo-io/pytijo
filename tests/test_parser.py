import os
import re
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
                'id': re.compile(r'\[TABLE (\d{1,2})\]'),
                'flows': [
                    {
                        'id': re.compile(r'\s{4}\[FLOW_ID(\d+)\]'),
                        'timestamp': re.compile(r'\s+Timestamp\s+=\s+(.+)')
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
                'id': re.compile(r'.*Group id:\s+(\d+)'),
                'ref_count': re.compile(r'.*Reference count:\s+(\d+)'),
                'packet_count': re.compile(r'.*Packet count:\s+(\d+)'),
                'byte_count': re.compile(r'.*Byte count:\s+(\d+)'),
                'bucket': [
                    {
                        'id': re.compile(r'.*Bucket\s+(\d+)'),
                        'packet_count': re.compile(r'.*Packet count:\s+(\d+)'),
                        'byte_count': re.compile(r'.*Byte count:\s+(\d+)'),
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
    struct = { 'message': re.compile(r'(.*)') }
    lines = ["Hello World"]
    expected_output = { 'message': "Hello World" }
    parsed = parser.parse_struct(lines, struct)
    assert parsed == expected_output


def test_simple_list():
    struct = { 'count': [re.compile(r'(\d)')] }
    lines = ["The count says: 1", "The count says: 2", "The count says: 3",
             "The count says: 4", "The count says: 5"]
    expected_output = { 'count': [1,2,3,4,5] }
    parsed = parser.parse_struct(lines, struct)
    # For now we need to convert to type after parsing
    parsed = {'count': map(int, parsed['count'])}
    assert parsed == expected_output


def test_parser(mock_struct):
    lines = StringIO(read('./flow_output.txt')).readlines()
    expected_output = ast.literal_eval(read('./flow_output_parsed.txt'))
    parsed = parser.parse_struct(lines, mock_struct)
    assert parsed == expected_output


def test_groups(mock_group_struct):
    lines = StringIO(read('./group_output.txt')).readlines()
    expected_output = ast.literal_eval(read('./group_output_parsed.txt'))
    parsed = parser.parse_struct(lines, mock_group_struct)
    assert parsed == expected_output
