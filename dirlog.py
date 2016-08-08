#!/usr/bin/env python2
'''
History database for directories visited to make getting around easier.
'''
from __future__ import print_function
import os, sys, re
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
  dir="$(dirlog-cd "$@")"
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
''')


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
        return

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

    print(*(quote(i) for i in args), file=sys.stderr)
    sp.call(args)


# from shlex in python3
_find_unsafe = re.compile(r'[^\w@%+=:,./-]').search

def quote(s):
    """Return a shell-escaped version of the string *s*."""
    if not s:
        return "''"
    if _find_unsafe(s) is None:
        return s

    # use single quotes, and put single quotes into double quotes
    # the string $'b is then quoted as '$'"'"'b'
    return "'" + s.replace("'", "'\"'\"'") + "'"


def get_and_update(directory=None, hist=1):
    '''
    utility designed to be wrapped in a shell function with `cd` in such a way
    that tracks the directories you visit and need only track the first few
    letters of the basename to return. Read the docs for more information.

    Instead of using the normal "console_scripts" method of entry, this
    function is executed when running this source file as a script. It's a bit
    faster that way.
    '''
    if not directory:
        return(HOME)

    if not os.path.isdir(directory):
        path = getpath(directory, hist)
        dbex('UPDATE dirs SET time = datetime("now") WHERE path = ?', (path,))
    else:
        path = os.path.abspath(directory)
        dbex('INSERT OR REPLACE INTO dirs VALUES(?, ?, datetime("now"))',
             (path, os.path.basename(path)))

    db.commit()
    return path


class Trigger:
    '''
    lazy ways to supply function arguments, mostly for the interactive
    prompt... he... I hope.
    '''
    def __init__(self, func):
        self.func = func

    def __repr__(self):
        self.func()
        return ''

    def __truediv__(self, other):
        return self.func(other)

    def __getattr__(self, name):
        return self.func(name)

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)


@Trigger
def c(hint=''):
    """
    Python version of the `c` shell function for use in python shells. The
    interface is a bit 'magical' thanks to the Trigger class.

    >>> c # goes to home dir
    Documents  Downloads  Movies (etc...)

    >>> # prints and extra newline because this is a trick with __repr__
    >>> c.Mo # assuming you have been there in the past...
    'Lord of The Rings Trilogy' (etc...)
    >>> # if you need to type a full path, use `/` operator and a string.
    >>> c/'/etc/sshd'
    (sshd config files...)
    >>> # if you don't like all the magic, call with normal syntax:
    >>> c('/etc/sshd')
    """
    os.chdir(get_and_update(os.path.expanduser(hint)))
    ls = sp.Popen(['ls', '--color=auto'])
    ls.wait()


def main():
    '''
    function called by `dirlog-cd`, to be wrapped with `cd` in a shell function
    in ~/.bashrc or wherever.
    '''
    directory = sys.argv[1] if sys.argv[1:] else ''
    hist = sys.argv[2] if sys.argv[2:] else 1
    directory = get_and_update(directory, hist)
    print(directory) if directory else exit(1)


if __name__ == '__main__':
    main()
