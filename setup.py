"""Nanoservice installation script

https://github.com/walkr/nanoservice
"""
import codecs

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


NANOSERVICE_VERSION = '0.7.2-1'
# try making setuptools happy with PEP 440-compliant post version
REL_TAG = NANOSERVICE_VERSION.replace('-', 'p')

NANOSERVICE_DOWNLOAD_URL = (
    'https://github.com/freepn/nanoservice/tarball/' + REL_TAG
)


def read_file(filename):
    """
    Read a utf8 encoded text file and return its contents.
    """
    with codecs.open(filename, 'r', 'utf8') as f:
        return f.read()


setup(
    name='nanoservice',
    version=NANOSERVICE_VERSION,
    packages=['nanoservice'],
    author='Tony Walker',
    author_email='walkr.walkr@gmail.com',
    url='https://github.com/walkr/nanoservice',
    license='MIT',
    description='nanoservice is a small Python library for '
                'writing lightweight networked services using nanomsg',
    long_description=read_file('README.rst'),
    download_url=NANOSERVICE_DOWNLOAD_URL,
    install_requires=[
        'msgpack',
        'nanomsg @ git+https://github.com/freepn/nanomsg-python@master',
    ],
    dependency_links=[
        'git+https://github.com/freepn/nanomsg-python.git@master#egg=nanomsg',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
)
