import os
import json
import pytest
from pytijo import parser


@pytest.fixture(scope="module")
def mock_struct(request):
    return {
        "tables": [
            {
                "#id": r"\[TABLE (\d{1,2})\]",
                "flows": [
                    {
                        "#id": r"\[FLOW_ID(\d+)\]",
                        "timestamp": r"Timestamp\s+=\s+(.+)",
                        "ofp_version": r"ofp_version\s+=\s+(\d+)",
                        "controller_group": r"ControllerGroup\s+=\s+(\d+)",
                        "controller_id": r"ControllerId\s+=\s+(\d+)",
                        "priority": r"Priority\s+=\s+(\d+)",
                        "idle_timeout": r"Idle_timeout\s+=\s+(\d+)",
                        "hard_timeout": r"Hard_timeout\s+=\s+(\d+)",
                        "packet_count": r"Packet_count\s+=\s+(\d+)",
                        "byte_count": r"Byte_count\s+=\s+(\d+)",
                        "cookie": r"Cookie\s+=\s+([0-9a-fA-F]+)",
                        "send_flow_rem": r"Send_flow_rem\s+=\s+(true|false)",
                        "match_fields": {
                            "#start": r"(\[MATCHFIELDS\])",
                            "#end": r"(\[INSTRUCTIONS\])",
                            "ether_type": r"OFPXMT_OFB_ETH_TYPE\s+=\s+(.+)",
                            "in_port": r"OFPXMT_OFB_IN_PORT\s+=\s+(.+)",
                            "mpls_label": r"OFPXMT_OFB_MPLS_LABEL\s+=\s+(.+)",
                        },
                        "instructions": {
                            "#start": r"(\[INSTRUCTIONS\])",
                            "go_to_table": {
                                "#start": r"(\[OFPIT_GOTO_TABLE\])",
                                "table": r"table\s+=\s+(\d+)",
                            },
                            "apply_actions": {
                                "#start": r"(\[OFPIT_APPLY_ACTIONS\])",
                                "output": {
                                    "port": r"port\s+=\s+(.+)",
                                    "mlen": r"mlen\s+=\s+(.+)",
                                },
                                "pop_mpls": {
                                    "#start": r"(\[OFPAT_POP_MPLS\])",
                                    "eth": r"eth\s+=\s+(.+)",
                                },
                                "group": {
                                    "#start": r"(\[OFPAT_GROUP\])",
                                    "#id": r"id\s+=\s+(\d+)",
                                },
                            },
                        },
                    }
                ],
            }
        ]
    }


@pytest.fixture(scope="module")
def mock_group_struct(request):
    return {
        "groups": [
            {
                "#id": r"Group id:\s+(\d+)",
                "ref_count": r"Reference count:\s+(\d+)",
                "packet_count": r"Packet count:\s+(\d+)",
                "byte_count": r"Byte count:\s+(\d+)",
                "bucket": [
                    {
                        "#id": r"Bucket\s+(\d+)",
                        "packet_count": r"Packet count:\s+(\d+)",
                        "byte_count": r"Byte count:\s+(\d+)",
                    }
                ],
            }
        ]
    }


def read(filename):
    output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    with open(output_file, "r") as fin:
        return fin.read()


def test_simple_struct():
    struct = {"message": r"(.*)"}
    lines = ["Hello World"]
    expected_output = {"message": "Hello World"}
    parsed = parser.parse_struct(lines, struct)
    assert parsed == expected_output


def test_simple_list():
    struct = {"count": [r"(\d)"]}
    lines = [
        "The count says: 1",
        "The count says: 2",
        "The count says: 3",
        "The count says: 4",
        "The count says: 5",
    ]
    expected_output = {"count": [1, 2, 3, 4, 5]}
    parsed = parser.parse_struct(lines, struct)
    # We need to convert to type after parsing
    parsed = {"count": list(map(int, parsed["count"]))}
    assert parsed == expected_output


def test_re_custom_groups_list():
    struct = {"count@tijo_re": [{"regex": r"(\d)\s+(\d)\s+(\d)\s+(\d)", "group": 2}]}
    lines = [
        "The count says: 1 2 3 4",
        "The count says: 2 3 4 1",
        "The count says: 3 4 1 2",
        "The count says: 4 1 2 3",
    ]
    expected_output = {"count": ["2", "3", "4", "1"]}
    parsed = parser.parse_struct(lines, struct)
    assert parsed == expected_output


def test_re_custom_groups_single():

    struct = {"count@tijo_re": {"regex": r"(\d)\s+(\d)\s+(\d)\s+(\d)", "group": 2}}
    lines = [
        "The count says: 1 2 3 4",
        "The count says: 2 3 4 1",
        "The count says: 3 4 1 2",
        "The count says: 4 1 2 3",
    ]
    expected_output = {"count": "2"}
    parsed = parser.parse_struct(lines, struct)
    assert parsed == expected_output


def test_flows(mock_struct):
    lines = read("./flow_output.txt").splitlines()
    expected_output = json.loads(read("./flow_output_parsed.txt"))
    parsed = parser.parse_struct(lines, mock_struct)
    assert parsed == expected_output


def test_groups(mock_group_struct):
    lines = read("./group_output.txt").splitlines()
    expected_output = json.loads(read("./group_output_parsed.txt"))
    parsed = parser.parse_struct(lines, mock_group_struct)
    assert parsed == expected_output


def test_parse(mock_struct):
    expected_output = json.loads(read("./flow_output_parsed.txt"))
    parsed = parser.parse(read("./flow_output.txt"), mock_struct)
    assert parsed == expected_output
