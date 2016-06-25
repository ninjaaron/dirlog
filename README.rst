dirlog
======
The tradition of our unix forefathers teaches us that the command line
is the most efficient way to do any task on a unix system. This is
frequently the case. However, there are a few tasks which are more
difficult. For example, editing video. ``dirlog`` will not fix that.
``dirlog`` does something else useful however; It makes it so you have to
type long directory names less frequently, or cd+ls your way around the
filesystem until you get where you're going. The primary function of
dirlog is to replace the ``cd`` command.

Now, you can't actually replace the ``cd`` command. It's a shell builtin,
and it *must* be a shell builtin. Each process has its own working
directory, inherited from its parent. There is no (sane) way for a child
process to change the directory of its parent. This is why ``cd`` must
run as part of the shell's process itself. This is why ``dirlog`` used
as part of a shell function to wrap the ``cd`` command. There is no
other way.

Installation
------------
You can install dirlog from PyPI with ``pip`` or by cloning this repo
and using ``pip``. e.g.

.. code::

  $ git clone https://github.com/dirlog.git
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

.. code:: sh

  function c
    set dir (python /path/to/dirlog.py $argv)
    if [ $dir != "" ]
      cd $dir
      ls
    end
  end

*(fish is actually a better scripting language than POSIX in some ways,
but, you know I sometimes like interoperability.)*

On the other hand, because I assume that anyone using tcsh actually
knows how to write scripts for it (as, indeed, I do not), I leave it to
you to figure it out.
