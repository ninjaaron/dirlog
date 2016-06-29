from setuptools import setup, find_packages

setup(
    name='dirlog',
    version='0.1.1',
    description='keep a log of directories you visit to get back fast',
    long_description=open('README.rst').read(),
    url='https://github.com/ninjaaron/dirlog',
    author='Aaron Christianson',
    author_email='ninjaaron@gmail.com',
    py_modules = ['dirlog'],
    classifiers=['Programming Language :: Python :: 3.5'],
    entry_points={'console_scripts': [
        'dirlog=dirlog:install',
        'dlog=dirlog:wrap']},
)
