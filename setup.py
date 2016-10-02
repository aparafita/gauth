# Author: Álvaro Parafita (parafita.alvaro@gmail.com)

from distutils.core import setup

setup(
    name = "gauth",
    packages = ["gauth"],
    version = "0.1",
    description = "Google APIs connector",
    author = "Álvaro Parafita",
    author_email = "parafita.alvaro@gmail.com",
    keywords = ["google", "api"],
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    long_description = """\
Easy connector to Google APIs.

This version requires Python 3 or later; no Python 2 version is available.
"""
)