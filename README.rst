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

.. image:: https://travis-ci.org/freepn/nanoservice.svg?branch=master
    :target: https://travis-ci.org/freepn/nanoservice
    :alt: Build Status

.. image:: https://img.shields.io/github/issues/freepn/nanoservice
    :target: https://github.com/freepn/nanoservice/issues?q=is:issue+is:open
    :alt: Open Issues

.. image:: https://img.shields.io/github/issues-pr/freepn/nanoservice
    :target: https://github.com/freepn/nanoservice/issues?q=is:open+is:pr
    :alt: Pull Requests


Install
=======

1) Make sure you have the nanomsg library installed.

For Gentoo use the package available in portage: dev-libs/nanomsg.
There is also a Launchpad PPA with packages built for `Ubuntu xenial`_.

.. _Ubuntu xenial: https://launchpad.net/~nerdboy/+archive/ubuntu/embedded

If no packages are available for your Linux platform, install manually::

    $ git clone git@github.com:nanomsg/nanomsg.git
    $ ./configure
    $ make
    $ make check
    $ sudo make install


For more details visit the official `nanomsg GitHub repo`_.

On OS X you can also do::

    $ brew install nanomsg


2) Install the correct version of msgpack and remove old pkg if needed.

Note the name change upstream has a "transitional" package so when
upgrading from msgpack-0.4 or earlier, don’t do ``pip install -U msgpack-python``.

If upgrading as above, do::

    $ pip uninstall msgpack-python; pip install msgpack

Otherwise just do::

    $ pip install msgpack


3) Install nanoservice.

On Gentoo you can use this `portage overlay`_ otherwise try the PPA
above for Ubuntu xenial, Debian stretch, etc.

.. _portage overlay: https://github.com/sarnold/portage-overlay

Alternatively, from the project directory::

$ make install


Or via pip::

$ pip install nanoservice (it's broken)


Example Usage
=============

The service:

.. code:: python
   :number-lines:

  from nanoservice import Responder

  def echo(msg):
      return msg

  s = Responder('ipc:///tmp/service.sock')
  s.register('echo', echo)
  s.start()


::

  $ python echo_service.py


The client:

.. code:: python
   :number-lines:

  from nanoservice import Requester

  c = Requester('ipc:///tmp/service.sock')
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
as package builds (ie, using FEATURES="test" in portage).

MIT Licensed
