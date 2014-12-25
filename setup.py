# -*- coding: utf-8 -*-
import os
from setuptools import setup


def read(*paths):
    """Build a file path from *paths* and return the contents."""
    with open(os.path.join(*paths), 'r') as f:
        return f.read()

setup(
    name='crosstag',
    version='0.0.1',
    description='Tag-in system for a gym',
    long_description=(read('README.rst') + '\n\n' +
                      read('HISTORY.rst') + '\n\n' +
                      read('AUTHORS.rst')),
    url='https://github.com/lundstrj/crosstag',
    license='MIT',
    author='Johan Lundstrom',
    author_email='lundstrom.se@gmail.com',
    py_modules=['crosstag'],
    include_package_data=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires=['flask', 'flask-WTF', 'flask-security', 'pyserial',
                      'requests', 'flask-sqlalchemy', 'screen'],
)
