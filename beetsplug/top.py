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
    "(select $what, album, count(*) as tracks, sum(length) as length from items $where group by $what, album) "
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
DEFAULT_COUNT = 10
DEFAULT_ORDER = "albums"

log = logging.getLogger('beets')

def top(lib, args, opts):
    params = parse_args(args)
    q = SQL.substitute(params)
    log.debug(q)
    with lib.transaction() as tx:
        rows = tx.query(q)
    print_result(rows, opts)

def print_result(rows, opts):
    for what, albums, tracks, time in rows:
        print "%s - %d - %d - %s" % (what, albums, tracks, timedelta(seconds=int(time)))
  
def parse_args(args):
    what  = None
    where = None
    count = DEFAULT_COUNT
    order = DEFAULT_ORDER
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
        years, args = expand_years(args[0]), args[1:]
        ys = ','.join(years)
        where = "where (original_year <> 0 and original_year in (%s)) or (original_year = 0 and year in (%s))" % (ys, ys)

    if not what or not order or not count:
        raise ui.UserError(u'invalid arguments')
    return { 'what': what, 'where': where, 'order': order, 'count': count }

def expand_years(years_spec):
    ranges = [[int(y) for y in se.split('-')] for se in years_spec.split(',')]
    years = [range(r[0], r[1] + 1) if len(r) > 1 else [r[0]] for r in ranges]
    return [str(y) for yrs in years for y in yrs]
  
class TopPlugin(BeetsPlugin):
    def commands(self):
        cmd = ui.Subcommand('top', help='show top artists, genres, years, or labels')
        def func(lib, opts, args):
            top(lib, args, opts)
        cmd.func = func
        return [cmd]
