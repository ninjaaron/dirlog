dirlog
======
The tradition of our unix forefathers teaches us that the command line
is the most efficient way to do any task on a unix system. This is
frequently the case. However, there are a few tasks which are more
difficult. For example, editing video. `dirlog` will not fix that.
`dirlog` does something else useful however; It makes it so you have to
type long directory names less frequently, or cd+ls your way around the
filesystem until you get where you're going. The primary function of
dirlog is to replace the `cd` command.

Now, you can't actually replace the `cd` command. It's a shell builtin,
and it *must* be a shell builtin. Each process has its own working
directory, inherited from its parent. There is no (sane) way for a child
process to change the directory of its parent. This is why `cd` must run
as part of the shell's process itself. This is why `dirlog` used as part
of a shell function to wrap the `cd` command. There is no other way.

Installation
------------
You can install dirlog from PyPI with `pip` or by cloning this repo and
using `pip`. Of course, you could just run the setup script or use
