Structify Text
==============

Structures semi-structured text, useful when parsing command line output
from networking devices.

What is it
----------

| If you’re reading this you’ve probably been tasked with
  programmatically retrieving information from a CLI driven device and
  you’ve got to the point
| where you have a nice string of text and say to yourself, “wow I wish
  it just returned something structured that I could deal with like JSON
  or some other key/value format”.

Well that’s where ``structifytext`` tries to help. It lets you define
the payload you wish came back to you, and with a sprinkle of the right
regular expressions it does!

Usage
-----

At less than 100 lines of code it’s quite simple. The ``parse_struct``
method expects a “structure” and an output string converted to a list (I
found the easiest way to do this is to use ``StringIO.readlines()``).

The Struct
~~~~~~~~~~

| A stuct or structure or payload or whatever have you, is just a
  dictionary that resembles what you wish to get back.
| With the values either being a dictionary ``{}``, a list ``[]``, or a
  regular expression string ``[a-z](\d)`` with one group (to populate
  the value).

The structure is recursively parsed, to populate the
dictionary/structure that was provided with values from the input string
list.

| Quite often, similar sections of semi-structured text are repeated in
  the text you are trying to parse.
| To parse these sections of text, we define a dictionary with key of
  either ``id`` or ``block_start`` the difference being ``block_start``
  key/value is dropped from the resulting output.
| This ``id`` or ``block_start`` marks the beginning and end for each
  “chunk” that you’d like parsed.
| You can forcefully mark the end of a “chunk” by specifying a
  ``block_end`` key and regex value.

An example is useful here.

E.g. The following structure.

::

    {
            'tables': [
                {
                    'id': '\[TABLE (\d{1,2})\]',
                    'flows': [
                        {
                            'id': '\[FLOW_ID(\d+)\]',
                            'info': 'info\s+=\s+(.*)'
                        }
                    ]
                }
            ]
        }

Will create a “chunk/block” from the following output

::

    [TABLE 0] Total entries: 3
        [FLOW_ID1]
        info = related to table 0 flow 1
    [TABLE 1] Total entries: 31
        [FLOW_ID1]
        info = related to table 1 flow 1

That will be parsed as:

::

    {
        'tables': [{
            'id': '0',
            'flows': [{ 'id': '1', 'info': 'related to table 0 flow 1' }],
            }, {
            'id': '1',
            'flows': [{ 'id': '1', 'info': 'related to table 1 flow 1' }]
        }]
    }

See under ``tests/test_parser_api.py`` for more usage examples.