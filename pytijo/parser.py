import re
import six
import importlib
from .constants import *


def parse(text, struct):
    if isinstance(text, (list, tuple)):
        text = "\n".join(text)
    if isinstance(text, six.string_types):
        return parse_struct(text, struct)
    return None


def parse_struct(text, struct):
    if isinstance(text, (list, tuple)):
        text = "\n".join(text)

    parsed = {}

    for k, v in six.iteritems(struct):
        if not isinstance(k, six.string_types) or len(k) <= 0:
            continue

        k = k.strip().lower()
        module_index = k.find(MODULE_CHAR)

        # Get module name
        module_name = None
        if module_index > -1:
            module_name = k[module_index + 1 :]
            k = k[:module_index]

        # Load parser module
        parser_module = _load_module(module_name)

        # Get keyword
        keyword = None
        if k.startswith(KEYWORD_CHAR):
            keyword = k
            k = k[1:]

        if module_name is None:
            return_as_list = False
            if (
                isinstance(v, (list, tuple))
                and not isinstance(v, six.string_types)
                and len(v) > 0
                and isinstance(v[0], dict)
            ):
                v = v[0]
                return_as_list = True
            if isinstance(v, dict):
                parsed[k] = _parse_dict(v, text, return_list=return_as_list)
                continue

        if keyword != KEYWORD_START and keyword != KEYWORD_END:
            parsed[k] = parser_module.parse(text, k, v)

    return parsed


def _load_module(module_name=DEFAULT_MODULE_NAME):
    # TODO: Load module from other packages
    if module_name is None or len(module_name) == 0:
        module_name = DEFAULT_MODULE_NAME
    return importlib.import_module("{}.{}".format(CORE_MODULE_PACKAGE, module_name))


def _parse_dict(value, text, return_list=False):
    if return_list and (KEYWORD_START in value or KEYWORD_ID in value):
        chunks = _chunk_lines(text, value)
        if chunks is not None:
            return [parse_struct(chunk, value) for chunk in chunks]
        return None
    return parse_struct(text, value)


def _chunk_lines(text, struct):
    if KEYWORD_ID not in struct and KEYWORD_START not in struct:
        raise KeyError(
            "'{}' or '{}' key is required in a list containing a dictionary".format(
                KEYWORD_ID, KEYWORD_START
            )
        )

    # TODO make this more intelligent. For example, make start like
    # '@start': {'regex': '<the-regex>',skip: true, group:1} that will allow to customize
    # thinks like which group to use and if the text matched should be included or not
    start = struct[KEYWORD_START] if KEYWORD_START in struct else struct[KEYWORD_ID]
    start_regex = _compile_regex(KEYWORD_ID, start)

    end = struct[KEYWORD_END] if KEYWORD_END in struct else None
    end_regex = _compile_regex(KEYWORD_ID, end) if end is not None else None

    chunks = []
    start_position = -1
    chunk_to_text = text
    while len(chunk_to_text) > 0:
        start_match = start_regex.match(text)
        if not start_match:
            break
        end_match = end_regex.match(text) if end_regex else None

        if start_position < 0 and end_match is None:
            start_position = start_match.span()[0]
            continue

        end_position = end_match.span()[1] if end_match else start_match.span()[0] - 1
        chunk = chunk_to_text[start_position, end_position]
        chunk_to_text = chunk_to_text[end_position + 1 :]
        chunks.append(chunk)
        start_position = start_match.span()[0]

    if len(chunk_to_text) > 0:
        chunks.append(chunk_to_text)

    return chunks


def _compile_regex(key, regex):
    if not isinstance(regex, six.string_types):
        raise TypeError(
            "The value at key '{}' must be a regular expression string".format(key)
        )
    return re.compile(regex)
