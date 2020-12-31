"""Package configuration."""

import os
import pathlib

from manager import __version__
from setuptools import (
    find_packages,
    setup,
)

HERE = pathlib.Path(__file__).parent

# README = (HERE / 'README.md').read_text()
readme_path = os.path.join(HERE, 'README.md')
README = open(readme_path, 'rt').read()

setup(
    name='botblox',
    version=__version__,
    description='BotBlox Manager CLI tool',
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://github.com/botblox/botblox-manager-software',
    author='Aaron Elijah',
    author_email='aaronzakelijah@googlemail.com',
    license='MIT',
    python_requires='>=3.6',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Operating System :: OS Independent',
    ],
    packages=find_packages(include=['manager', 'manager.*']),
    include_package_data=True,
    install_requires=[
        'pyserial>=3.5',
    ],
    extras_require={
        'dev': [
            'flake8==3.8.4',
            'flake8-import-order==0.18.1',
            'flake8-builtins==1.5.3',
            'flake8-docstrings==1.5.0',
            'flake8-rst-docstrings==0.0.14',
            'flake8-annotations==2.4.1',
            'flake8-print==4.0.0',
            'pep8-naming==0.11.1',
        ],
    },
    entry_points={
        'console_scripts': [
            'botblox=manager.__main__:main',
        ],
    },
)
