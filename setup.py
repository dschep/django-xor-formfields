from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='django-xor-formfields',

    version='0.0.3',

    description='Mutually Exclusive form field wigets for Django',
    long_description=long_description,

    url='https://github.com/dschep/django-mutuallyexclusive-formfields',

    author='Daniel Schep',
    author_email='dschep@gmail.com',

    license='MIT',

    classifiers=[
        'Development Status :: 4 - Beta',

        'Intended Audience :: Developers',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],

    keywords='django development forms',

    packages=['xorformfields', 'xorformfields.forms'],

    install_requires=['django', 'requests'],

    package_data={
        'xorformfields': ['static/mutually_exclusive_widget.js'],
    },
)
