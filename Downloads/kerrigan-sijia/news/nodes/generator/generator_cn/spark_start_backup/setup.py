from setuptools import setup, find_packages

setup(
    name         = 'generator',
    version      = '1.0',
    packages     = find_packages(),
    package_data = {'resources':['*']},
)
