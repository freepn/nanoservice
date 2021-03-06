=============
 nanoservice
=============

nanoservice is a small Python library for writing lightweight networked
services using `nanomsg`_.  With nanoservice you can break up monolithic
applications into small, specialized services which communicate with
each other.

.. _nanomsg: http://nanomsg.org/
.. _nanomsg GitHub repo: https://github.com/nanomsg/nanomsg


.. image:: https://img.shields.io/github/license/freepn/nanoservice
    :target: https://github.com/freepn/nanoservice
    :alt: License

.. image:: https://img.shields.io/github/v/tag/freepn/nanoservice?color=green&include_prereleases&label=latest%20release
    :target: https://github.com/freepn/nanoservice/releases
    :alt: GitHub tag (latest SemVer pre-release)

.. image:: https://img.shields.io/github/workflow/status/freepn/nanoservice/ci
    :target: https://github.com/freepn/nanoservice/actions?query=workflow:ci
    :alt: GitHub CI Build Status

.. image:: https://img.shields.io/github/issues/freepn/nanoservice
    :target: https://github.com/freepn/nanoservice/issues?q=is:issue+is:open
    :alt: Open Issues

.. image:: https://img.shields.io/github/issues-pr/freepn/nanoservice
    :target: https://github.com/freepn/nanoservice/issues?q=is:open+is:pr
    :alt: Pull Requests

.. image:: https://img.shields.io/codecov/c/github/freepn/nanoservice
    :target: https://codecov.io/gh/freepn/nanoservice
    :alt: Codecov

.. image:: https://img.shields.io/codeclimate/maintainability/freepn/nanoservice
    :target: https://codeclimate.com/github/freepn/nanoservice
    :alt: Code Climate maintainability

Install
=======

Make sure you have the nanomsg library installed
------------------------------------------------

For Gentoo use the package available in portage: dev-libs/nanomsg.
There is also a Launchpad PPA with packages built for `Ubuntu`_ 
LTS releases: xenial, bionic, and focal.

.. _Ubuntu: https://launchpad.net/~nerdboy/+archive/ubuntu/embedded

If no packages are available for your Linux platform, install manually::

    $ git clone git@github.com:nanomsg/nanomsg.git
    $ ./configure
    $ make
    $ make check
    $ sudo make install


For more details visit the official `nanomsg GitHub repo`_.

On OS X you can also do::

    $ brew install nanomsg


Install the correct version of msgpack
--------------------------------------

On Gentoo you can use this `portage overlay`_ otherwise install it from the
usual Ubuntu repos (or use the PPA above for a xenial backport, still named
python3-msgpack).

Note the name change upstream has a "transitional" package so when
upgrading from msgpack-0.4 or earlier, don’t do ``pip install -U msgpack-python``.

If upgrading as above, do::

    $ pip uninstall msgpack-python; pip install msgpack

Otherwise just do::

    $ pip install msgpack


Install nanoservice
-------------------

On Gentoo you can use this `portage overlay`_ otherwise use the PPA
above for Ubuntu.

.. _portage overlay: https://github.com/sarnold/portage-overlay

Alternatively, from the project directory::

$ make install


Or via pip::

$ pip install nanoservice (it's broken)


Example Usage
=============

The service:

.. code::

  from nanoservice import Responder

  def echo(msg):
      return msg

  s = Responder('ipc:///tmp/service.sock', timeouts=(None, None))
  s.register('echo', echo)
  s.start()


::

  $ python echo_service.py


The client:

.. code::

  from nanoservice import Requester

  c = Requester('ipc:///tmp/service.sock', timeouts=(None, None))
  res, err = c.call('echo', 'hello world’)
  print('Result is {}'.format(res))


::

  $ python my_client.py
  $ Result is: hello world


Other
=====

To run tests, first install tox (see Testing Notes below) then run::

    $ make test


To run benchmarks::

    $ make bench


Check out the examples directory for more examples.

Testing Notes
=============

Tests using python multiprocessing have been separated out into their own
directory (`test2`) due to sporadic failures triggering NanoMsgAPIError
exceptions, `Address already in use` followed by `Connection timed out`
(the unittest-based tests are still under the `test` directory).

Although random failures are occasionally seen in travis-ci tests, all
tests *should* run successfully with tox and pytest on the desktop as well
as package builds (ie, using FEATURES="test" in portage with -userpriv).

MIT Licensed
