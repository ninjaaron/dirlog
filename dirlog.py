#!/usr/bin/env python2
from __future__ import print_function
import os, sys, shlex
import subprocess as sp
import sqlite3

HOME = os.environ['HOME']
DBPATH = HOME + '/.cache/dirlog.db'
db = sqlite3.connect(DBPATH)
cur = db.cursor()
dbex = cur.execute
dbex('CREATE TABLE IF NOT EXISTS '
     'dirs(path TEXT PRIMARY KEY, name TEXT, time TEXT)')


def install():
    print('''\
dirlog doesn't do much by itself. To use it, put a function like
this in your ~/.bashrc (or whatever POSIX shell configuration
file).

c() {
  dir="$(python %s "$@")"
  if [ "$dir" != "" ]; then
    cd "$dir" && ls
  fi
}

If you use fish, tcsh or any other non-POSIX shells (God have
mercy on your soul), you will need to modify this slightly. Then,
use `c` as you would the `cd` command. You may wish to ommit the
`&& ls`. I find it convinient.

dirlog also provides the `dlog` command to help you wrap other
commands in a way  that benefits from directory history. See
http://github.com/ninjaaron/dirlog for more details.\
''' % (__file__))



def getpath(hint, hist=1):
    hist = int(hist)
    dbex('SELECT path FROM dirs WHERE name LIKE ? ORDER BY time DESC',
         (hint + '%',))
    try:
        match = cur.fetchall()[hist-1][0]
    except (TypeError, IndexError):
        print('no matching directory in history', file=sys.stderr)
        exit(1)
    return match


def wrap():
    args = sys.argv[1:]
    token = 0


    def unpack(hint):
        hint, slash, name = hint.partition('/')
        hint, _, hist = hint.partition('@')
        hist = hist if hist else 1
        return getpath(hint, hist) + slash + name

    if len(args) == 1:
        print(unpack(args[0]))
        exit()

    for index, arg in enumerate(args):
        if arg.startswith('@'):
            token = 1
            args[index] = unpack(arg[1:])

    if not token:
        args[-1] = unpack(args[-1])

    print(*(shlex.quote(i) for i in args), file=sys.stderr)
    sp.call(args)


def main():
    directory = sys.argv[1] if sys.argv[1:] else ''
    hist = sys.argv[2] if sys.argv[2:] else 1
    if not directory:
        print(HOME)
        exit()
    if not os.path.isdir(directory):
        path = getpath(directory, hist)
        dbex('UPDATE dirs SET time = datetime("now") WHERE path = ?', (path,))
    else:
        path = os.path.abspath(directory)
        dbex('INSERT OR REPLACE INTO dirs VALUES(?, ?, datetime("now"))',
             (path, os.path.basename(path)))
    db.commit()
    print(path)


if __name__ == '__main__':
    main()
