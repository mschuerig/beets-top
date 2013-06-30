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
    "select $subject, count(*) as albums, sum(tracks) as tracks, sum(length) as time from "
    "(select $subject, album, count(*) as tracks, sum(length) as length from $table group by $subject, album) "
    "group by $subject "
    "order by $order desc "
    "limit $count"
)

SUBJECTS = {
    "artists":      "artist",
    "albumartists": "albumartist",
    "composers":    "composer",
    "formats":      "format",
    "genres":       "genre",
    "labels":       "label",
    "years":        "year"
}
ORDERS = {
    "albums":  "albums",
    "tracks":  "tracks",
    "time":    "time",
    "seconds": "time"
}
TEMPLATES = {
    "albumartist": Template("$subject"),
    "albums":  Template("$subject - $albums albums"),
    "artist": Template("$subject"),
    "composer": Template("$subject"),
    "format": Template("$subject"),
    "genre": Template("$subject"),
    "label": Template("$subject"),
    "seconds": Template("$subject - $seconds"),
    "tracks":  Template("$subject - $tracks tracks"),
    "time":    Template("$subject - $time"),
    "year": Template("$subject")
}

DEFAULT_COUNT = 10 # TODO read from config
DEFAULT_ORDER = "albums" # TODO read from config

log = logging.getLogger('beets')

def top(lib, args, opts):
    params = parse_args(args, opts)
    q = SQL.substitute(params)
    log.debug(q)
    with lib.transaction() as tx:
        rows = tx.query(q, params['subvals'])
    print_result(rows, params['template'])

def print_result(rows, template):
    for subject, albums, tracks, secs in rows:
        seconds = int(secs)
        time    = timedelta(seconds=seconds)
        print template.safe_substitute(
            subject=subject, albums=albums, tracks=tracks, seconds=seconds, time=time
        )
  
def parse_args(args, opts):
    # TODO use options instead of interspersed keywords
    subject    = None
    table   = 'items'
    count   = DEFAULT_COUNT
    order   = DEFAULT_ORDER
    subvals = []
    if len(args) >= 1:
        if args[0].isdigit():
            count = int(args[0])
            args = args[1:]
    if len(args) >= 1:
        subject, args = SUBJECTS.get(args[0]), args[1:]
        template = TEMPLATES.get(subject)
    if len(args) >= 2 and args[0] == "by":
        args = args[1:]
        by, args = args[0], args[1:]
        order = ORDERS.get(by)
        template = TEMPLATES.get(by)
    if len(args) >= 2 and args[0] == "in":
        args = args[1:]
        table2, subvals2 = library.get_query(args).statement()
        table = '(' + table2 + ')'
        subvals += subvals2

    if not subject or not order or not count:
        raise ui.UserError(u'invalid arguments')
    return {
        'subject':  subject,
        'table':    table,
        'order':    order,
        'count':    count,
        'template': template,
        'subvals':  subvals
    }

class TopPlugin(BeetsPlugin):
    def commands(self):
        cmd = ui.Subcommand('top', help='show top artists, genres, years, or labels')
        def func(lib, opts, args):
            top(lib, args, opts)
        cmd.func = func
        return [cmd]
