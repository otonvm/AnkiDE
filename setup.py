# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(name="AnkiDE",
      version="1.0",
      packages=find_packages(),
      install_requires=[
          "attrs",
          "requests",
          "docopt",
          "microsofttranslator"
      ],
      entry_points={
          "console_scripts": ["ankide = ankide.__main__:main"]
      }
      )
