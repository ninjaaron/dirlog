'''
Monkey patch setuptools to write faster console_scripts with this format:

    from mymodule import entry_function
    entry_function()

This is better.
'''
from setuptools.command import easy_install


@classmethod
def get_args(cls, dist, header=None):
    """
    Yield write_script() argument tuples for a distribution's
    console_scripts and gui_scripts entry points.
    """
    if header is None:
        header = cls.get_header()
    spec = str(dist.as_requirement())
    for type_ in 'console', 'gui':
        group = type_ + '_scripts'
        for name, ep in dist.get_entry_map(group).items():
            cls._ensure_safe_name(name)
            script_text = 'from {0} import {1}\n{1}()'.format(
                          ep.module_name, ep.attrs[0])
            args = cls._get_script_args(type_, name, header, script_text)
            for res in args:
                yield res


easy_install.ScriptWriter.get_args = get_args


def main():
    import shutil
    import sys
    dests = sys.argv[1:] if sys.argv[1:] else ['.']
    for dst in dests:
        shutil.copy(__file__, dst)
