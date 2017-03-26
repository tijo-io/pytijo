# Structify Text

Structures semi-structured text, useful when parsing command line output from networking devices.

## Usage

Define what you would like the dictionary/JSON output to look like. With a regex expression identifying the value you would like extracted.

Every list containing a dictionary must have an `'id'` key and regex expression that will "chunk/block" the text.

E.g. The following structure.

```
{
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
```

Will create a "chunk/block" from the following output

```
[TABLE 0] Total entries: 3
    [FLOW_ID1]
[TABLE 1] Total entries: 31
    [FLOW_ID1]
```

That will be parsed as:

```
{
    'tables': [{
		'id': '0',
		'flows': [{ 'id': '1' }],
		}, {
		'id': '1',
		'flows': [{ 'id': '1' }]
	}]
}
```

See `tests/test_parser.py` for more usage examples.