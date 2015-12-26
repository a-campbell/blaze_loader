#!/usr/bin/env python
from distutils.core import setup
import sys

long_description = ''

if 'upload' in sys.argv:
    with open('README.md') as f:
        long_description = f.read()


install_reqs = [
    'blaze>=0.8.3',
    'SQLAlchemy>=1.0.8',
]


if __name__ == "__main__":
setup(
    name='blaze_loader',
    version='0.1.1',
    description='Easily save and load Blaze Data objects.',
    author='Andrew Campbell',
    author_email='andrew@quantopian.com',
    packages=[
        'blaze_loader',
    ],
    long_description=long_description,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python',
        'Topic :: Utilities',
    ],
    url='https://github.com/a-campbell/blaze_loader',
    install_requires=install_reqs
)