from setuptools import setup

try:
    from urllib import request
except ImportError:
    import urllib2 as request

fastep = request.urlopen('https://raw.githubusercontent.com/ninjaaron/fast-entry_points/master/fastentrypoints.py')
namespace = {}
exec(fastep.read(), namespace)

setup(
    name='dirlog',
    version='0.2.8',
    description='keep a log of directories you visit to get back fast',
    long_description=open('README.rst').read(),
    url='https://github.com/ninjaaron/dirlog',
    author='Aaron Christianson',
    author_email='ninjaaron@gmail.com',
    py_modules = ['dirlog'],
    classifiers=['Programming Language :: Python :: 3.5'],
    entry_points={'console_scripts': [
        'dirlog=dirlog:install',
        'dlog=dirlog:wrap',
        'dirlog-cd=dirlog:main']},
)
