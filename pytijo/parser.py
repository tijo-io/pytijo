import re
import six
import importlib
from .constants import (
    KEYWORD_ID,
    KEYWORD_START,
    KEYWORD_END,
    KEYWORD_CHAR,
    MODULE_CHAR,
    CORE_MODULE_PACKAGE,
    DEFAULT_MODULE_NAME,
)


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

        # if it is such a key name without module check if we need to keep parsing inside
        if (module_name is None or len(module_name) == 0) and (
            keyword is None or len(keyword) == 0
        ):
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

        if keyword not in (KEYWORD_START, KEYWORD_END):
            parsed[k] = parser_module.parse(text, k, v)

    return parsed


def _load_module(module_name=DEFAULT_MODULE_NAME):
    # TODO: Load module from other packages
    if module_name is None or len(module_name) == 0:
        module_name = DEFAULT_MODULE_NAME
    return importlib.import_module("{}.{}".format(CORE_MODULE_PACKAGE, module_name))


def _parse_dict(value, text, return_list=False):
    if KEYWORD_START in value or KEYWORD_ID in value:
        chunks = _chunk_lines(text, value)
        if chunks is not None and len(chunks) > 0:
            if return_list:
                return [parse_struct(chunk, value) for chunk in chunks]
            return parse_struct(chunks[0], value)

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
    # '#start': {'regex': '<the-regex>',skip: true, group:1} that will allow to customize
    # thinks like which group to use and if the text matched should be included or not
    start = struct[KEYWORD_START] if KEYWORD_START in struct else struct[KEYWORD_ID]
    start_regex = _compile_regex(KEYWORD_ID, start)

    end = struct[KEYWORD_END] if KEYWORD_END in struct else None
    end_regex = _compile_regex(KEYWORD_END, end) if end is not None else None

    chunks = []
    if not end_regex:
        start_position = -1
        for match in start_regex.finditer(text):
            if start_position < 0:
                start_position = match.span()[0]
                continue
            chunk = text[start_position : match.span()[0]]
            if len(chunk) > 0:
                chunks.append(chunk)
            start_position = match.span()[0]
        if start_position >= 0 and len(text) > start_position:
            chunk = text[start_position : len(text)]
            chunks.append(chunk)
    else:
        while len(text) > 0:
            start_match = start_regex.search(text)
            end_match = end_regex.search(text)
            if not start_match or not end_match:
                break
            chunk = text[start_match.span()[0] : end_match.span()[1]]
            text = text[
                end_match.span()[0] - 1
                if start_match.span()[1] < end_match.span()[0]
                else start_match.span()[1] + 1 :
            ]
            if len(chunk) > 0:
                chunks.append(chunk)

    return chunks if len(chunks) > 0 else None


def _compile_regex(key, regex):
    if not isinstance(regex, six.string_types):
        raise TypeError(
            "The value at key '{}' must be a regular expression string".format(key)
        )
    return re.compile(regex)
