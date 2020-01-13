"""Nanoservice installation script

https://github.com/walkr/nanoservice
"""
import sys

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


def read_long_description(readme_file):
    """ Read package long description from README file """
    try:
        import pypandoc
    except (ImportError, OSError) as exception:
        print('No pypandoc or pandoc: %s' % (exception,))
        if sys.version_info.major == 3:
            handle = open(readme_file, encoding='utf-8')
        else:
            handle = open(readme_file)
        long_description = handle.read()
        handle.close()
        return long_description
    else:
        return pypandoc.convert(readme_file, 'rst')


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
    long_description=read_long_description('README.md'),
    download_url=NANOSERVICE_DOWNLOAD_URL,
    install_requires=[
        'msgpack',
        'nanomsg @ git+https://github.com/freepn/nanomsg-python@master',
    ],
    dependency_links=[
        'git+https://github.com/freepn/nanomsg-python.git@master#egg=nanomsg',
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
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
