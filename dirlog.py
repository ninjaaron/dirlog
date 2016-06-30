#!/usr/bin/env python2
'''
History database for directories visited to make getting around easier.
'''
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
    'Print install instructions'
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
    """
    return a path whose basename matches the given `hint`. Defaults to the most
    recent item, though earlier matches may be specified with the `hist`
    parameter.
    """
    hist = int(hist)
    dbex('SELECT path FROM dirs WHERE name LIKE ? ORDER BY time DESC',
         (hint + '%',))
    try:
        match = cur.fetchall()[hist-1][0]
    except (TypeError, IndexError):
        print('no matching directory in history', file=sys.stderr)
        exit(1)

    if not os.path.isdir(match):
        dbex('DELETE FROM dirs WHERE path = ?', (match,))
        match = getpath(hint, hist)
        db.commit()

    return match


def cleanup():
    'remove entrys for directories that no longer exist'
    print('cleaning out paths which no longer exist...')
    dbex('SELECT path FROM dirs')
    for path in (i[0] for i in cur.fetchall()):
        if not os.path.isdir(path):
            print(path)
            dbex('DELETE FROM dirs WHERE path = ?', (path,))


def wrap():
    '''
    utility for wrapping commands to take advantage of the directory history.
    Read the docs for further information.
    '''
    args = sys.argv[1:]
    token = 0

    def unpack(hint):
        hint, slash, name = hint.partition('/')
        hint, _, hist = hint.partition('@')
        hist = hist if hist else 1
        return getpath(hint, hist) + slash + name

    if len(args) == 1:
        cleanup() if args[0] == '-c' else print(unpack(args[0]))
        db.commit()
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
    '''
    utility designed to be wrapped in a shell function with `cd` in such a way
    that tracks the directories you visit and need only track the first few
    letters of the basename to return. Read the docs for more information.

    Instead of using the normal "console_scripts" method of entry, this
    function is executed when running this source file as a script. It's a bit
    faster that way.
    '''
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
