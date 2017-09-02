dirlog
======

.. contents::

dirlog is a wrapper for ``cd`` that keeps a database of all the
directories you visit, so you only have to type the first few letters of
the basename to get back to them the next time.

Ramblings
---------
The tradition of our unix forefathers teaches us that the command line
is the most efficient way to do any task on a unix system. This is
frequently the case. However, there are a few tasks which are more
difficult. For example, editing video. ``dirlog`` will not fix that.
``dirlog`` does something else useful however; It makes it so you have
to type long directory names less frequently, or cd+ls your way around
the filesystem until you get where you're going. The primary function of
dirlog is to replace the ``cd`` command.

Now, you can't actually replace the ``cd`` command. It's a shell builtin,
and it *must* be a shell builtin. Each process has its own working
directory, inherited from its parent. There is no (sane) way for a child
process to change the directory of its parent. This is why ``cd`` must
run as part of the shell's process itself. This is why ``dirlog`` is
used as part of a shell function to wrap the ``cd`` command. There is no
other way.

Installation
------------
You can install dirlog from PyPI with ``pip3`` or by cloning this repo
and using ``pip3``. e.g. (you can use ``pip2`` as well, but you may
encounter some bugs.

.. code:: sh

  $ git clone https://github.com/ninjaaron/dirlog.git
  $ sudo pip3 install dirlog

Or, perhaps you'll prefer to install in your user directory (in which
case you must have ``~/.local/bin/`` in your path, or wherever your
user's python stuff is).

.. code:: sh

  $ pip3 install --user dirlog

Alternatively, There is an AUR Arch Linux and derived distros.

After that, run the the ``dirlog`` command, which will give you the
function you need to get ``dirlog`` and ``cd`` to work together.

.. code:: sh

  c() {
    dir="$(dirlog-cd "$@")"
    if [ "$dir" != "" ]; then
      cd "$dir" && ls
    fi
  }

If you run a non-POSIX shell (huge mistake), like fish or tcsh, you'll
need something else. Here's the fish version:

.. code:: fish

  function c
    set dir (dirlog-cd $argv)
    if [ "$dir" != "" ]
      cd "$dir"; and ls
    end
  end

In fish, you can just enter this at the command line and then use
``funcsave c`` to make it permanent.

I don't know tcsh, so I leave it to you to figure it out.

Naturally, you may omit the ``ls`` command, if you wish. I find it
handy.

Tip:
  I tweak the above POSIX script slightly for quickly switching back and
  forth betweeen two directories:

  .. code:: sh

    c() {
      local dir=$(dirlog-cd "$@")
      if [ "$dir" != "" ]; then
        LAST="$PWD"
        cd "$dir"&& ls
      fi
    }

    b() {
      c "$LAST"
    }

  ``local`` is not strictly POSIX, but it works in many shells, and then
  I stick the previous directory in a global variable so I can get back
  to it quickly. If you want some more sophisticated directory history,
  I suppose it would be easy enough to use pushd and popd in a dirlog
  wrapper.

Usage
-----

``c`` function
^^^^^^^^^^^^^^
To start off with, you can do *almost* everything with the ``c``
function that you can with ``cd``. (Some version of ``cd`` have some
extra flags. ``c`` has none.) However, whenever you use ``c``, it will
remember the complete path of the directory you move to. To return to
that directory, you can simply type the first part of the name of the
directory, and it will take you back to the last directory where the
beginning of the name of matches the hint you give.

.. code:: sh

  ~$ c src/stupid-project
  setup.py  stupid.py
  ~/src/stupid-project$ c
  Downloads  Documents  Music  Pictures  pr0n  src
  ~$ # now watch close
  ~$ c st
  setup.py stupid.py
  ~/src/stupid-project$

The more directories you visit, the more will be stored in your history.
Makes it quick to get around.

Now, what if you have to directories with the same name, or similar for
the first few characters? It takes you to the matching directory
that was most recently visited. If you want to go back to an earlier
directory that match, you may use numbers to indicate how far back it
is on the list. ``2`` is the match before last, ``3`` the one before
that, etc.

.. code:: sh

  ~/src/stupid-project$ c ~/Documents/stupid-lists
  amimals-that-smell  people-who-smell  goverment-agencies-that-smell
  ~/Documents/stupid-lists$ c stu
  amimals-that-smell  people-who-smell  goverment-agencies-that-smell
  ~/Documents/stupid-lists$ # takes us back to this directory
  ~/Documents/stupid-lists$ # because it is most recent match
  ~/Documents/stupid-lists$ c stu 2
  setup.py  stupid.py
  ~/src/stupid-project$

This is really fairly trivial, but I have found it to be extremely
handy, if I do say so myself. I use it much more frequently that any
other, eh, "software," I've written. The history is stored in an
independent sqlite database, so it is updated across all shell sessions
simultaneously.

You may also ``from dirlog import c`` in a python shell to get a native
implementation. The syntax is a bit "magical" for convenience in the
shell. It's use is documented in the docstring. However, because it is
rather magical, it breaks ``help()``. ("oops"), so I'll copy it here.

.. code:: python

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

Don't use this object in a script. Its __repr__ is a lie.. If you need
dirlog functionality in a script (which you shouldn't...), use the
``getpath()`` function, or ``get_and_update()`` These functions are
non-magicall.


``dlog`` command wrapper
^^^^^^^^^^^^^^^^^^^^^^^^
It recently occurred to me that it might be useful the have this
directory  history mechanism available to other commands. ``dlog`` is a
simple way to do this. Put the ``dlog`` command in front of the command
you wish to run, and it will expand the last argument to the last
matching directory you visited.

.. code:: sh

  ~/Documents/boring-work$ dlog ln -sr data.csv stu
  ln -sr data.cvs /home/luser/src/stupid-project
  ~/Documents/boring-work$ c
  Downloads  Documents  Music  Pictures  junk.txt  pr0n  src
  ~$ dlog mv junk.txt bo
  mv junk.txt /home/luser/Documents/boring-work
  ~$

You may add a subpath, if you wish. No globbing yet :(

.. code:: sh

  ~$ dlog cp -R src bo/boring-code
  cp -R src /home/luser/Documents/boring-work/boring-code
  ~$

As you see, dlog will echo back the command it executes to stderr.

You may also access directories further back in the history, using the
``@`` symbol (this symbol was chosen because it is not used by any of
the popular shells for globbing, as far as I know).

.. code:: sh

  ~$ dlog ls st@2
  ls /home/luser/Documents/stupid-lists
  amimals-that-smell  people-who-smell  goverment-agencies-that-smell
  ~$

History and subpaths can be combined, like this:
``st@2/animals-that-smell``.

If you wish to use any other argument than the last one for directory
expansion, it must be prefixed with ``@``.

.. code:: sh

  ~$ dlog cp @Mr@2/egg.mp3 .
  cp '/home/luser/Music/Mr. Bungle/Mr. Bungle/egg.mp3' .
  ~$

If you have any arguments prefixed in this way, the final argument will
no longer automatically be expanded. However, you can prefix as many
arguments as you like with ``@`` in a single command 

.. code:: sh

  ~$ dlog true @st @bor
  true /home/luser/src/stupid-project /home/luser/Documents/boring-work
  ~$

If ``dlog`` is given only one argument, it will simply print the name of
all matching directories to stdout, and not try to execute a command.

.. code:: sh

  ~$ dlog Mr
  /home/luser/Music/Mr. Bungle
  ~$
