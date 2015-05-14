import os
from setuptools import setup


setup(
    name='bamboo.py',
    version='0.1.1',
    author='Matt Rasband',
    author_email='matt.rasband@gmail.com',
    description='Easily query bamboo results for a run',
    license='MIT',
    keywords='bamboo atlassian continuous integration',
    url='https://github.com/mrasband/bamboo.py',
    platforms=['any'],
    py_modules=['bamboo'],
    install_requires=['colorama>=0.3.0', 'requests>=2.5.0'],
    entry_points={
        'console_scripts': [
            'bambooed = bamboo:main'
        ]
    })
