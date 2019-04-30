import six
import re


TIJO_METADATA = {
    "metadata_version": "0.1",
    "status": ["preview"],
    "supported_by": "community",
}

DOCUMENTATION = r"""
---
module: re
short_description: Parse values based on regular expressions
description:
  - This module allows parsing text using regular expressions
version_added: "0.1"
options:
  regex:
    description:
      - A regular expression to find the the value to extack from the given text.
      - If regex is a string then only the first value that match will be taken and it will be returned as string.
      - If regex is provided as string then all the matching values will be taken and a list will be returned.
    type: str|list
  group:
    description:
      - Group number to obtain the value from the regular expression.
      - By default is 1 if at least a group if defined in the regex.
      - If the regex does not contain any group then it will take the only one defined on group 0.
    type: int

"""

ATTR_REGEX = "regex"
ATTR_GROUP = "group"


def parse(text, key, value):

    group = 1
    is_list = False
    regex = value
    if isinstance(regex, (list, tuple)):
        regex = regex[0]
        is_list = True

    if isinstance(regex, dict):
        group = (
            group
            if ATTR_GROUP not in regex
            else int(_get_value(regex, ATTR_GROUP, default=1))
        )
        regex = _get_value(regex, ATTR_REGEX)

    if not isinstance(regex, six.string_types):
        raise TypeError(
            "The value at key '{}' must be a regular expression string".format(key)
        )

    regex = re.compile(regex)
    # first, try to use the group defined by the user
    # by default the first group is the one choosen
    # if not parenthesis are provided in the regex then use group 0
    group = group if regex.groups >= group else 1 if regex.groups > 0 else 0
    result = []

    # if the regexis provided as a list then we take as many values as possible
    # if not, we just take the first value
    for match in regex.finditer(text):
        result.append(match.group(group))
        if is_list is False:
            break

    # the result will be a list if the regex is provided as a list
    if is_list is True:
        return result if len(result) > 0 else None
    return result[0] if len(result) > 0 else None


def _get_value(map, key, mandatory=False, default=None, allow_empty=True):
    result = map.get(key)
    if result is None:
        if mandatory:
            raise AttributeError("{} not found".format(key))
        result = default

    if not allow_empty and (result is None or len(result) <= 0):
        raise AttributeError("{} has empty value".format(key))

    return result
