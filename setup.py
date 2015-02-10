# -*- coding: utf-8 -*-

import os

from setuptools import setup, find_packages

here = os.path.dirname(os.path.abspath(__file__))
README = open(os.path.join(here, 'README.rst')).read()

setup(
    name='httptestserver',
    version='0.2.0',
    author='Javier Santacruz',
    author_email='javier.santacruz.lc@gmail.com',
    long_description=README,
    description='HTTP(s) and SMTP testing server',
    include_package_data=True,
    packages=find_packages(),
    install_requires=[],
    classifiers=[
        "Topic :: Software Development :: Testing"
    ],
)
