#!/usr/bin/env python
from setuptools import find_packages, setup

from simple_sso import __version__


REQUIREMENTS = [
    "Django>=4.2",
    "itsdangerous<1.0.0",
    "requests",
]


CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Environment :: Web Environment',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.10',
    'Programming Language :: Python :: 3.11',
    'Programming Language :: Python :: 3.12',
    'Programming Language :: Python :: 3.13',
    'Framework :: Django',
    'Framework :: Django :: 4.2',
    'Framework :: Django :: 5.2',
    'Framework :: Django :: 6.0',
    'Topic :: Internet :: WWW/HTTP',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    'Topic :: Software Development',
    'Topic :: Software Development :: Libraries',
]


setup(
    name='django-simple-sso',
    version=__version__,
    author='Divio AG',
    author_email='info@divio.com',
    url='http://github.com/aldryn/django-simple-sso',
    license='BSD-3-Clause',
    description='Simple SSO for Django',
    long_description=open('README.rst').read(),
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=REQUIREMENTS,
    classifiers=CLASSIFIERS,
)
