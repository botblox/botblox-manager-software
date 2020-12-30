"""Package configuration."""

import os
import pathlib

from setuptools import setup, find_packages
from manager import __version__

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
    entry_points={
        'console_scripts': [
            'botblox=manager.__main__:main',
        ],
    },
)
