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

SQL = Template(
  "select $what, count(*) as albums, sum(tracks) as tracks, sum(length) as time from "
  "(select $what, album, count(*) as tracks, sum(length) as length from items group by $what, album) "
  "group by $what "
  "order by $order desc "
  "limit $limit"
)

WHATS = {
  "artists":      "artist",
  "albumartists": "albumartist",
  "composers":    "composer",
  "formats":      "format",
  "genres":       "genre",
  "years":        "year"
}
ORDERS = {
  "albums": "albums",
  "tracks": "tracks",
  "time":   "time"
}
DEFAULT_COUNT = 10
DEFAULT_ORDER = "albums"

def top(lib, args, opts):
  what, order, count = parse_args(args)
  with lib.transaction() as tx:
    rows = tx.query(SQL.substitute(what=what, order=order, limit=count))
  print_result(rows, opts)

def print_result(rows, opts):
  for what, albums, tracks, time in rows:
    print "%s - %d - %d - %s" % (what, albums, tracks, timedelta(seconds=int(time)))
  
def parse_args(args):
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
  if len(args) >= 1:
    order, args = ORDERS.get(args[0]), args[1:]
  if not what or not order or not count:
    raise ui.UserError(u'invalid arguments')
  return what, order, count
  
class TopPlugin(BeetsPlugin):
  def commands(self):
    cmd = ui.Subcommand('top', help='show top artists, genres, years, or labels')
    def func(lib, opts, args):
      top(lib, args, opts)
    cmd.func = func
    return [cmd]
