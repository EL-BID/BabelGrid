#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

with open('requirements.txt', encoding='utf-8') as f:
    requirements = [line.strip() for line in f if line]

setup_requirements = [ ]

test_requirements = [ ]

setup(
    author="Joao Carabetta",
    author_email='joao.carabetta@gmail.com',
    python_requires='>=3',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3'
    ],
    description="Python bindings for S2, a hierarchical square geospatial indexing system.",
    entry_points={
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    name='s2',
    packages=find_packages(include=['s2', 's2.*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/JoaoCarabetta/s2',
    version='0.1.9',
    zip_safe=False,
)
