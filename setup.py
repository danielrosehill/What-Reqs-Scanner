#!/usr/bin/env python3
"""Setup script for Requirements Scanner CLI."""

from setuptools import setup

setup(
    name='requirements-scanner',
    version='1.0.0',
    description='CLI tool to scan repositories for requirements.txt files and analyze package usage',
    author='Daniel Rosehill',
    author_email='public@danielrosehill.com',
    url='https://github.com/danielrosehill/What-Reqs-Scanner',
    py_modules=['requirements_scanner'],
    python_requires='>=3.7',
    entry_points={
        'console_scripts': [
            'requirements-scanner=requirements_scanner:main',
            'reqs-scan=requirements_scanner:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
    ],
    keywords='requirements pip packages analysis scanning',
)
