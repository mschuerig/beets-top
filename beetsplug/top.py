# coding=utf-8
#
# Copyright (C) 2013 Michael Schürig <michael@schuerig.de>
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

"""Shows top albums, genres, and years."""

from beets.plugins import BeetsPlugin
from beets import library
from beets import ui
from beets import util
from datetime import timedelta
from string import Template
import logging

SQL = Template(
    "select $what, count(*) as albums, sum(tracks) as tracks, sum(length) as time from "
    "(select $what, album, count(*) as tracks, sum(length) as length from $table group by $what, album) "
    "group by $what "
    "order by $order desc "
    "limit $count"
)

WHATS = {
    "artists":      "artist",
    "albumartists": "albumartist",
    "composers":    "composer",
    "formats":      "format",
    "genres":       "genre",
    "labels":       "label",
    "years":        "year"
}
ORDERS = {
    "albums": "albums",
    "tracks": "tracks",
    "time":   "time"
}
DEFAULT_COUNT = 10 # TODO read from config
DEFAULT_ORDER = "albums" # TODO read from config

log = logging.getLogger('beets')

def top(lib, args, opts):
    params = parse_args(args)
    q = SQL.substitute(params)
    log.debug(q)
    with lib.transaction() as tx:
        rows = tx.query(q, params['subvals'])
    print_result(rows, opts)

def print_result(rows, opts):
    for what, albums, tracks, time in rows:
        # TODO use a template and allow user to set it
        print "%s - %d - %d - %s" % (what, albums, tracks, timedelta(seconds=int(time)))
  
def parse_args(args):
    # TODO use options instead of interspersed keywords
    what    = None
    table   = 'items'
    count   = DEFAULT_COUNT
    order   = DEFAULT_ORDER
    subvals = []
    if len(args) >= 1:
        if args[0].isdigit():
            count = int(args[0])
            args = args[1:]
    if len(args) >= 1:
        what, args = WHATS.get(args[0]), args[1:]
    if len(args) >= 2 and args[0] == "by":
        args = args[1:]
        order, args = ORDERS.get(args[0]), args[1:]
    if len(args) >= 2 and args[0] == "in":
        args = args[1:]
        table2, subvals2 = library.get_query(args).statement()
        table = '(' + table2 + ')'
        subvals += subvals2

    if not what or not order or not count:
        raise ui.UserError(u'invalid arguments')
    return { 'what': what, 'table': table, 'order': order, 'count': count, 'subvals': subvals }

class TopPlugin(BeetsPlugin):
    def commands(self):
        cmd = ui.Subcommand('top', help='show top artists, genres, years, or labels')
        def func(lib, opts, args):
            top(lib, args, opts)
        cmd.func = func
        return [cmd]
