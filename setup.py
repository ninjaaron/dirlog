from setuptools import setup
import fastentrypoints

setup(
    name='dirlog',
    version='1.2.0',
    description='keep a log of directories you visit to get back fast',
    long_description=open('README.rst').read(),
    url='https://github.com/ninjaaron/dirlog',
    author='Aaron Christianson',
    license='BSD',
    author_email='ninjaaron@gmail.com',
    py_modules = ['dirlog'],
    classifiers=['Programming Language :: Python :: 3.5'],
    entry_points={'console_scripts': [
        'dirlog=dirlog:install',
        'dlog=dirlog:wrap',
        'dirlog-cd=dirlog:main']},
)
