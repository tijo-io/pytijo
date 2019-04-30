import re
import six
import warnings
import importlib

KEYWORD_ID = "@id"
COPY_ID = True
KEYWORD_START = "@start"
KEYWORD_END = "@end"

DEFAULT_MODULE_NAME = "tijo_re"


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

    # to be backwards compatible @id attributed is added as id to the output
    # TODO discuss if this should be like this
    if KEYWORD_ID in struct and COPY_ID and "id" not in struct:
        struct["id"] = struct[KEYWORD_ID]

    for k, v in six.iteritems(struct):
        if not isinstance(k, six.string_types) or len(k) <= 0:
            continue

        k = k.strip()
        index_at = k.find("@")

        # if k starts by @ then we need to skip it
        # because there is no need to process it
        if index_at == 0:
            continue

        # it is a key without @ so we need to first verify
        # if there is a dict to process
        # the key can contain either dict or a list which the first position is a dict
        if index_at == -1:
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

        # we need to process the key/value with a module
        # by default we use re module
        key_name = k if index_at < 0 else k[:index_at]
        module_name = DEFAULT_MODULE_NAME if index_at < 0 else k[index_at + 1 :]
        module_name = module_name if len(module_name) > 0 else DEFAULT_MODULE_NAME

        parser_module = importlib.import_module("pytijo.modules.{}".format(module_name))
        parsed[key_name] = parser_module.parse(text, key_name, v)

    return parsed


def _parse_dict(value, text, return_list=False):
    if KEYWORD_START in value or KEYWORD_ID in value:
        chunks = _chunk_lines(text, value)
        if chunks is not None:
            parsed = [parse_struct(chunk, value) for chunk in chunks]
            return parsed if return_list else parsed[0]
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
        if not match:
            break
        end_match = end_regex.match(text) if end_regex else None

        if start_position < 0 and end_match is None:
            start_position = match.span()[0]
            continue

        end_position = end_match.span()[1] if end_match else start_match.span()[0] - 1
        chunk = chunk_to_text[start_position, end_position]
        chunk_to_text = chunk_to_text[end_position + 1 :]
        chunks.append(chunk)
        start_position = match.span()[0]

    if len(chunk_to_text) > 0:
        chunks.append(chunk_to_text)

    return chunks


def _compile_regex(key, regex):
    if not isinstance(regex, six.string_types):
        raise TypeError(
            "The value at key '{}' must be a regular expression string".format(key)
        )
    return re.compile(regex)
