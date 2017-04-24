#!/usr/bin/env python
'''
Setup for Structify Text
'''
from setuptools import setup, find_packages

setup(name='structifytext',
      version='0.2.0',
      description='Structure semi-structured text',
      license='Apache',
      author='Darin Sikanic',
      author_email='darin.sikanic@gmail.com',
      url='https://github.com/darinsikanic/structifytext',
      packages=find_packages(exclude=['tests']),
      install_requires=['six'],
      keywords='sructuretext structifytext structure text network cli parser',
      classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'Intended Audience :: Developers',
          'Intended Audience :: Telecommunications Industry',
          'License :: OSI Approved :: Apache Software License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
          'Topic :: Software Development :: Libraries',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: System :: Networking'
      ])
