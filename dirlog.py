#!/usr/bin/env python2
from __future__ import print_function
import os, sys
import subprocess as sp
import sqlite3

HOME = os.environ['HOME']
DBPATH = HOME + '/.cache/dirlog.db'
db = sqlite3.connect(DBPATH)
cur = db.cursor()
dbex = cur.execute
dbex('CREATE TABLE IF NOT EXISTS '
     'dirs(path TEXT PRIMARY KEY, name TEXT, time TEXT)')



def getdir(directory, hist=1):
    dbex('SELECT path FROM dirs WHERE name LIKE ? ORDER BY time DESC',
         (directory + '%',))
    try:
        match = cur.fetchall()[hist-1][0]
    except (TypeError, IndexError):
        print('no matching directory in history', file=sys.stderr)
        exit(1)
    dbex('UPDATE dirs SET time = datetime("now") WHERE path = ?', (match,))
    return match


def wrap():
    hint, _, name = sys.argv.pop().partition('/')
    path = getdir(hint) + _ + name
    sp.call(sys.argv[1:] + [path])


def install():
    print('''\
dirlog doesn't do much by itself. To use it, put a function like
this in your ~/.bashrc (or whatever POSIX shell configuration
file).

c() {
  dir="$(python %s/dirlog.py "$@")"
  if [ "$dir" != "" ]; then
    cd "$dir"
    ls
  fi
}

If you use fish, tcsh or any other non-POSIX shells (God have
mercy on your soul), you will need to modify this slightly. Then,
use `c` as you would the `cd` command. You may wish to ommit the
line with `ls`. I find it convinient.

dirlog also provides the `dl` command to help you wrap other
command in a way  that benefits from directory history. See
http://github.com/ninjaaron/dirlog for more details.\
''' % (sys.path[0]))


def main():
    directory = sys.argv[1] if sys.argv[1:] else ''
    hist = int(sys.argv[2]) if sys.argv[2:] else 1
    if not directory:
        print(HOME)
        exit()
    if not os.path.isdir(directory):
        path = getdir(directory, hist)
    else:
        path, name = os.path.abspath(directory), os.path.basename(directory)
        dbex('INSERT OR REPLACE INTO dirs VALUES(?, ?, datetime("now"))',
             (path, name))
    print(path)
    db.commit()


if __name__ == '__main__':
    main()
