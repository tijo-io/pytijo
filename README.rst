PyTiJo - Text In JSON Out
=========================

Structures semi-structured text, useful when parsing command line output
from unix systems and networking devices.

What is it
----------

| If you’re reading this you’ve probably been tasked with
  programmatically retrieving information from a CLI driven device and
  you’ve got to the point
| where you have a nice string of text and say to yourself, “wow I wish
  it just returned something structured that I could deal with like JSON
  or some other key/value format”.

Well that’s where ``pytijo`` tries to help. It lets you define
the payload you wish came back to you, and with a sprinkle of the right
regular expressions it does!

Installation
------------

With pip:
::

  pip install pytijo

From source
::

  make install


Usage
-----

Pass your text and a "structure" (python dictionary) to the ``parser`` modules ``parse`` method.

::

  from pytijo import parser

  output = """
    eth0      Link encap:Ethernet  HWaddr 00:11:22:3a:c4:ac
              inet addr:192.168.1.2  Bcast:192.168.1.255  Mask:255.255.255.0
              UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
              RX packets:147142475 errors:0 dropped:293854 overruns:0 frame:0
              TX packets:136237118 errors:0 dropped:0 overruns:0 carrier:0
              collisions:0 txqueuelen:1000
              RX bytes:17793317674 (17.7 GB)  TX bytes:46525697959 (46.5 GB)

    eth1      Link encap:Ethernet  HWaddr 00:11:33:4a:c8:ad
              inet addr:192.168.1.3  Bcast:192.168.1.255  Mask:255.255.255.0
              inet6 addr: fe80::225:90ff:fe4a:c8ad/64 Scope:Link
              UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
              RX packets:51085118 errors:0 dropped:251 overruns:0 frame:0
              TX packets:3447162 errors:0 dropped:0 overruns:0 carrier:0
              collisions:0 txqueuelen:1000
              RX bytes:4999277179 (4.9 GB)  TX bytes:657283496 (657.2 MB)
    """

  struct = {
          'interfaces': [{
              'id': '(eth\d{1,2})',
              'ipv4_address': 'inet addr:(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})',
              'mac_address': 'HWaddr\s((?:[a-fA-F0-9]{2}[:|\-]?){6})'
            }]
         }

  parsed = parser.parse(output, struct)
  print parsed

This will return the python dictionary

::

  {
    'interfaces': [
        {
            'id': 'eth0',
            'ipv4_address': '192.168.1.2',
            'mac_address': '00:11:22:3a:c4:ac'
        },
        {
            'id': 'eth1',
            'ipv4_address': '192.168.1.3',
            'mac_address': '00:11:33:4a:c8:ad'
        }
    ]
  }

Which you can then do with as you please, maybe return as JSON as part of a REST service...

The Struct
~~~~~~~~~~

| A stuct or structure or payload or whatever have you, is just a
  dictionary that resembles what you wish to get back.
| With the values either being a dictionary ``{}``, a list ``[]``, or a
  regular expression string ``[a-z](\d)`` with **one group** (to populate
  the value).

The structure is recursively parsed, populating the
dictionary/structure that was provided with values from the input text.

| Quite often, similar sections of semi-structured text are repeated in
  the text you are trying to parse.
| To parse these sections of text, we define a dictionary with key of
  either ``#id`` or ``#start`` the difference being ``#start``
  key/value is dropped from the resulting output.
| This ``#id`` or ``#start`` marks the beginning and end for each
  “chunk” that you’d like parsed.
| You can forcefully mark the end of a “chunk” by specifying a
  ``#end`` key and regex value.

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
