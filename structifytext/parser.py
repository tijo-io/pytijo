import re
import six
import warnings


def parse_struct(lines, struct):
    parsed = {}
    for k, v in six.iteritems(struct):
        if isinstance(v, (list, tuple)) and not isinstance(v, six.string_types) and len(v) > 0:
            parsed[k] = _parse_list(k, v, lines)
        elif isinstance(v, dict):
            parsed[k] = _parse_dict(v, lines)
        else:
            if k != 'block_start' and k != 'block_end':
                parsed[k] = _parse_regex(lines, k, v)
    return parsed


def _parse_list(key, value, lines):
    if isinstance(value[0], dict):
        return _parse_dict(value[0], lines, return_list=True)
    else:
        return _parse_regex(lines, key, value[0], return_list=True)


def _parse_dict(value, lines, return_list=False):
    if 'block_start' in value or 'id' in value:
        chunks = _chunk_lines(lines, value)
        if chunks is not None:
            parsed = [parse_struct(chunk, value) for chunk in chunks]
            return parsed if return_list else parsed[0]
        return None
    return parse_struct(lines, value)


def _chunk_lines(lines, struct):
    if 'id' not in struct and 'block_start' not in struct:
        raise KeyError("'id' or 'block_start' key is required in a list containing a dictionary")
    id = struct['block_start'] if 'block_start' in struct else struct['id']
    id_regex = _compile_regex('id', id)
    matches = filter(id_regex.search, lines)
    if not matches:
        return None
    match_indexes = _index_of_matches(matches, lines)
    force_block_end_index = -1
    if 'block_end' in struct:
        block_end_regex = _compile_regex('block_end', struct['block_end'])
        block_end_matches = filter(block_end_regex.search, lines)
        if block_end_matches:
            block_end_indexes = _index_of_matches(block_end_matches, lines)
            force_block_end_index = next(i for i in block_end_indexes if i > match_indexes[0])
        else:
            warnings.warn("The block_end regular expression does not find a match")

    return _do_chunk_lines(lines, match_indexes, force_block_end_index)


def _do_chunk_lines(lines, match_indexes, force_block_end_index=-1):
    chunks = []
    if force_block_end_index >= 0:
        return [lines[match_indexes[0]:force_block_end_index]]
    for idx, val in enumerate(match_indexes):
        if idx+1 >= len(match_indexes):
            chunks.append(lines[val::])
        elif val <= match_indexes[-1]:
            if match_indexes[idx + 1] >= match_indexes[-1]:
                chunks.append(lines[val:match_indexes[-1]])
            else:
                chunks.append(lines[val:match_indexes[idx + 1]])
    return chunks


def _parse_regex(lines, key, regex, return_list=False):
    regex = _compile_regex(key, regex)
    if regex.groups < 1:
        raise ValueError("The regular expression at key '{}' must contain a regex group (...)".format(key))
    elif regex.groups > 1:
        warnings.warn("The regular expression at key '{}' should contain only one regex group".format(key))
    values = [m for l in lines for m in regex.findall(l) if m]
    if len(values) > 0 and not return_list:
        return values[0]
    return values if len(values) > 0 else None


def _index_of_matches(matches, lines):
    # list(set([])) removes duplicates
    return sorted(list(set(map(lambda x: lines.index(x), matches))))


def _compile_regex(key, regex):
    if not isinstance(regex, six.string_types):
        raise TypeError("The value at key '{}' must be a regular expression string".format(key))
    return re.compile(regex)
