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
    if isinstance(text, six.string_types):
        return parse_struct(text.splitlines(), struct)
    return None


def parse_struct(lines, struct):
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
                parsed[k] = _parse_dict(v, lines, return_list=return_as_list)
                continue

        # we need to process the key/value with a module
        # by default we use re module
        key_name = k if index_at < 0 else k[:index_at]
        module_name = DEFAULT_MODULE_NAME if index_at < 0 else k[index_at + 1 :]
        module_name = module_name if len(module_name) > 0 else DEFAULT_MODULE_NAME

        parser_module = importlib.import_module("pytijo.modules.{}".format(module_name))
        parsed[key_name] = parser_module.parse(lines, key_name, v)

    return parsed


def _parse_dict(value, lines, return_list=False):
    if KEYWORD_START in value or KEYWORD_ID in value:
        chunks = _chunk_lines(lines, value)
        if chunks is not None:
            parsed = [parse_struct(chunk, value) for chunk in chunks]
            return parsed if return_list else parsed[0]
        return None
    return parse_struct(lines, value)


def _chunk_lines(lines, struct):
    if KEYWORD_ID not in struct and KEYWORD_START not in struct:
        raise KeyError(
            "'{}' or '{}' key is required in a list containing a dictionary".format(
                KEYWORD_ID, KEYWORD_START
            )
        )
    id = struct[KEYWORD_START] if KEYWORD_START in struct else struct[KEYWORD_ID]
    id_regex = _compile_regex(KEYWORD_ID, id)
    matches = list(filter(id_regex.search, lines))
    if not matches:
        return None
    match_indexes = _index_of_matches(matches, lines)
    force_block_end_index = -1
    if KEYWORD_END in struct:
        block_end_regex = _compile_regex(KEYWORD_END, struct[KEYWORD_END])
        block_end_matches = list(filter(block_end_regex.search, lines))
        if block_end_matches:
            block_end_indexes = _index_of_matches(block_end_matches, lines)
            force_block_end_index = next(
                (i for i in block_end_indexes if i > match_indexes[0]), -1
            )
        else:
            warnings.warn("The block_end regular expression does not find a match")

    return _do_chunk_lines(lines, match_indexes, force_block_end_index)


def _do_chunk_lines(lines, match_indexes, force_block_end_index=-1):
    chunks = []
    if force_block_end_index >= 0:
        return [lines[match_indexes[0] : force_block_end_index]]
    for idx, val in enumerate(match_indexes):
        if idx + 1 >= len(match_indexes):
            chunks.append(lines[val::])
        elif val <= match_indexes[-1]:
            if match_indexes[idx + 1] >= match_indexes[-1]:
                chunks.append(lines[val : match_indexes[-1]])
            else:
                chunks.append(lines[val : match_indexes[idx + 1]])
    return chunks


def _parse_regex(lines, key, regex, return_list=False):
    regex = _compile_regex(key, regex)
    values = []
    for line in lines:
        # TODO: think if we shuold take more values from a single line
        # match only takes one
        match = regex.search(line)
        if match:
            values.append(match.group(1) if regex.groups > 0 else match.group())
    if len(values) > 0 and not return_list:
        return values[0]
    return values if len(values) > 0 else None


def _index_of_matches(matches, lines):
    # list(set([])) removes duplicates
    return sorted(list(set(map(lambda x: lines.index(x), matches))))


def _compile_regex(key, regex):
    if not isinstance(regex, six.string_types):
        raise TypeError(
            "The value at key '{}' must be a regular expression string".format(key)
        )
    return re.compile(regex)
