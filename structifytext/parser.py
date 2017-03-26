
def parse_struct(lines, struct):
    parsed = {}
    for k,v in struct.iteritems():
        if isinstance(v, (list, tuple)) and not isinstance(v, basestring) and len(v) > 0:
            if isinstance(v[0], dict):
                chunks = chunk_lines(lines, v[0])
                parsed[k] = [parse_struct(chunk, v[0]) for chunk in chunks]
            else:
                parsed[k] = parse_regex(lines, v[0], return_list=True)
        elif isinstance(v, dict):
            parsed[k] = parse_struct(lines, v)
        else:
            parsed[k] = parse_regex(lines, v)
    return parsed


def chunk_lines(lines, struct):
    id_regex = struct['id']
    matched_ids = filter(id_regex.match, lines)
    match_indexes = sorted(list(set(map(lambda x: lines.index(x), matched_ids))))

    chunks = []
    block_end = match_indexes[-1]
    for idx, val in enumerate(match_indexes):
        if idx+1 >= len(match_indexes):
            chunks.append(lines[val::])
        elif val <= block_end:
            if match_indexes[idx + 1] >= block_end:
                chunks.append(lines[val:block_end])
            else:
                chunks.append(lines[val:match_indexes[idx + 1]])
    return chunks


def parse_regex(lines, regex, return_list=False):
    values = [m.group(1) for l in lines for m in [regex.search(l)] if m]
    if not return_list or 0 < len(values) < 2:
        return values[0]
    return values
