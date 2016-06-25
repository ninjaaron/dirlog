dirlog
======

.. contents::

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
You can install dirlog from PyPI with ``pip`` or by cloning this repo
and using ``pip``. e.g.

.. code::

  $ git clone https://github.com/ninjaaron/dirlog.git
  $ sudo pip install dirlog

Or, perhaps you'll prefer to install in your user directory (in which
case you must have ``~/.local/bin/`` in your path, or wherever your
user's python stuff is).

.. code::

  $ pip install --user dirlog

After that, run the the ``dirlog`` command, which will give you the
function you need to get ``dirlog`` and ``cd`` to work together. It
will be a site-specific version of this:

.. code:: sh

  c() {
    dir="$(python /path/to/dirlog.py "$@")"
    if [ "$dir" != "" ]; then
      cd "$dir"
      ls
    fi
  }

If you run a non-POSIX shell (huge mistake), like fish or tcsh, you'll
need something else. Because I assume (perhaps wrongly) that most people
using fish don't actually know how to write anything useful in fish,
I'll do it for you:

.. code::

  function c
    set dir (python /path/to/dirlog.py $argv)
    if [ $dir != "" ]
      cd $dir
      ls
    end
  end

*(fish is actually a better scripting language than POSIX in many ways,
but, you know, I kind of like interoperability.)*

In fish, you can just enter this at the command line and then use
``funcsave c`` to make it permanent. 

Because I assume that anyone using tcsh actually knows how to write
scripts for it (as, indeed, I do not), I leave it to you to figure it
out.

Whichever horrible, non-POSIX shell you use, you'll need to modify the
``/path/to/dirlog.py`` to whatever it says when you run ``dirlog``. It
will be site-specific. Naturally, you may omit the ``ls`` command, if
you wish. I find it handy.

Usage
-----

``c`` function
^^^^^^^^^^^^^^
To start off with, you can do *almost* everything with the ``c``
function that you can with ``cd``. (Some version of ``cd`` have some
extra flags. ``c`` has none.) However, whenever you use ``c``, it will
remember the complete path of the directory you move to database. To
return to that directory, you can simply type the first part of the name
of the directory, and it will take you back to the last directory the
beginning of the name of which matches the hint you give.

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
the first few characters? It takes you to the the matching directory
that was most recently visited. If you want to go back to an earlier
directory that matches, you may use numbers to indicate how far back it
is on the list. ``2`` is the match before last, ``3`` the one before
that, etc.

(this example assumes ``~/src/stupid-project`` is already in the
database)

.. code:: sh

  ~/src/stupid-project$ c ~/Documents/stupid-lists
  amimals-that-smell  people-who-smell  goverment-agencies-that-smell
  ~/Documents/stupid-lists$ c stu
  amimals-that-smell  people-who-smell  goverment-agencies-which-smell
  ~/Documents/stupid-lists$ # takes us back to this directory
  ~/Documents/stupid-lists$ # because it is most recent match
  ~/Documents/stupid-lists$ c stu 2
  setup.py  stupid.py
  ~/src/stupid-project$

This is really fairly trivial, but I have found it to be extremely
handy, if I do say so myself. I use it much more frequently that any
other, eh, "software," I've written. The history is stored in an
independent sqlite database, so it is updated across all shell sessions
simultaniously.

``dl`` command wrapper
^^^^^^^^^^^^^^^^^^^^^^
It recently occured to me that it might be useful the have this
directory  history mechanism available to other commands. ``dl`` (for
"dirlog") is a very simple, not very flexible way to do this. It may
grow in sophistication later. or not. You simply put the ``dl`` command
in front of the command you wish to run, and it will expand the last
argument to the last matching directory you visited. At present it
**only** works on the last argument in the command, and it does not
support earlier directories that match the same hint with the number
mechanism of the ``c`` function. This may change in the future. or not.

.. code:: sh

  ~/Documents/boring-work$ dl ln -s data.csv stu
  ~/Documents/boring-work$ # data.csv has been linked to ~/src/stupid-project
  ~/Documents/boring-work$ c
  Downloads  Documents  Music  Pictures  junk.txt  pr0n  src
  ~$ dl mv junk.txt bo
  ~$ # junk.txt has been moved to ~/Documents/boring-work

Also, you can add a subpath, if you wish.

.. code:: sh

  ~$ dl cp -R src bo/boring-code
  ~$ # the ~/src directory has been copied to ~/Documents/boring-work/boring-code

I guess that's about it. Other commands may be added as I think of more
things for which a directory history may be useful.
