#!/usr/bin/env python2
'''
History database for directories visited to make getting around easier.
'''
from __future__ import print_function
import os, sys, re
import subprocess as sp
import sqlite3
INSTALL_MESSAGE = '''\
# dirlog doesn't do much by itself. To use it, put a function like
# this in your ~/.bashrc (or whatever POSIX shell configuration
# file).

c() {
  dir="$(dirlog-cd "$@")"
  if [ "$dir" != "" ]; then
    cd "$dir" && ls
  fi
}

# If you use fish, tcsh or any other non-POSIX shells (God have
# mercy on your soul), you will need to modify this slightly. Then,
# use `c` as you would the `cd` command. You may wish to ommit the
# `&& ls`. I find it convinient.

# dirlog also provides the `dlog` command to help you wrap other
# commands in a way  that benefits from directory history. See
# http://github.com/ninjaaron/dirlog for more details.\

# run dirlog -c to clean the cache if you wish.
'''
HOME = os.environ['HOME']
DBPATH = HOME + '/.cache/dirlog.db'
db = sqlite3.connect(DBPATH)
cur = db.cursor()
dbex = cur.execute
dbex('CREATE TABLE IF NOT EXISTS '
     'dirs(path TEXT PRIMARY KEY, name TEXT, time TEXT)')
db.commit()


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
# end of shlex stuff


class NotInHistory(Exception):
    pass


def getpaths(hint):
    """
    return a path whose basename matches the given `hint`. Defaults to the most
    recent item, though earlier matches may be specified with the `hist`
    parameter.
    """
    dbex('SELECT path FROM dirs WHERE name LIKE ? ORDER BY time DESC',
         (hint + '%',))
    match = [d[0] for d in cur.fetchall()]
    if not match:
        raise NotInHistory('no matching directory in history')
    return match


def getpath(hint, hist=None):
    if not hist:
        hist = 1
    hist = int(hist)
    match = getpaths(hint)[hist-1]
    if not os.path.isdir(match):
        dbex('DELETE FROM dirs WHERE path = ?', (match,))
        db.commit()
        match = getpath(hint, hist)
    return match


def get_and_update(directory=None, hist=1):
    '''
    utility designed to be wrapped in a shell function with `cd` in such a way
    that tracks the directories you visit and need only track the first few
    letters of the basename to return. Read the docs for more information.
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


def cleanup():
    'remove entrys for directories that no longer exist'
    dbex('SELECT path FROM dirs')
    for path in (i[0] for i in cur.fetchall()):
        if not os.path.isdir(path):
            yield path
            dbex('DELETE FROM dirs WHERE path = ?', (path,))
    db.commit()


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
    >>> c.Mo # Movies... assuming you have been there in the past...
    'Lord of The Rings Trilogy' (etc...)
    >>> # if you don't like the magic or need a path with special characters,
    >>> #call with normal syntax:
    >>> c('/etc/sshd')
    """
    os.chdir(get_and_update(os.path.expanduser(hint)))
    ls = sp.Popen(['ls', '--color=auto'])
    ls.wait()


def unpack(hint):
    hint, _, name = hint.partition('/')
    hint, _, hist = hint.partition('@')
    return os.path.join(getpath(hint, hist), name)


def wrap():
    '''
    utility for wrapping commands to take advantage of the directory history.
    Read the docs for further information.
    '''
    args = sys.argv[1:]
    token = 0

    if len(args) == 1:
        try:
            print(*('{:>2}  {}'.format(p[0]+1, p[1]) for p in
                    enumerate(getpaths(args[0]))),
                  sep='\n')
        except NotInHistory as e:
            print(e, file=sys.stderr)
        exit()

    for index, arg in enumerate(args):
        if arg.startswith('@'):
            token = 1
            args[index] = unpack(arg[1:])
    if not token:
        args[-1] = unpack(args[-1])

    print(*(quote(i) for i in args), file=sys.stderr)
    sp.call(args)


def install():
    'Print install instructions'
    if sys.argv[1:] and sys.argv[1] == '-c':
        print(*cleanup(), sep='\n')
    else:
        print(INSTALL_MESSAGE)


def main():
    '''
    function called by `dirlog-cd`, to be wrapped with `cd` in a shell function
    in ~/.bashrc or wherever.
    '''
    directory = sys.argv[1] if sys.argv[1:] else ''
    hist = sys.argv[2] if sys.argv[2:] else 1
    try:
        directory = get_and_update(directory, hist)
        print(directory) if directory else exit(1)
    except NotInHistory as e:
        print(e, file=sys.stderr)


if __name__ == '__main__':
    main()
