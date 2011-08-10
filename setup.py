import os
from setuptools import setup
from simple_sso import __version__ as version

README = os.path.join(os.path.dirname(__file__), 'README.rst')

with open(README) as fobj:
    long_description = fobj.read()

setup(name="django-simple-sso",
    version=version,
    description="Simple SSO for Django",
    long_description=long_description,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Topic :: Software Development',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='django sso',
    author='Jonas Obrist',
    author_email='jonas.obrist@divio.ch',
    url='http://github.com/ojii/django-simple-sso',
    license='BSD',
    packages=['simple_sso', 'simple_sso.sso_client', 'simple_sso.sso_server'],
    install_requires=['Django>=1.3', 'django-load'],
    include_package_data=True,
    zip_safe=False
)
