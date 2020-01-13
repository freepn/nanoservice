nanoservice
===========
nanoservice is a small Python library for writing lightweight networked services
using [nanomsg](http://nanomsg.org/)

With nanoservice you can break up monolithic applications into small,
specialized services which communicate with each other.

[![Build Status](https://travis-ci.org/walkr/nanoservice.svg?branch=master)](https://travis-ci.org/walkr/nanoservice)

## Install

1) Make sure you have the nanomsg library installed.

For Gentoo use the package available in portage: dev-libs/nanomsg.  There is also
a Launchpad PPA with packages built for [Ubuntu xenial](https://launchpad.net/~nerdboy/+archive/ubuntu/embedded)

If no packages are available for your Linux platform, install manually:

```shell
$ git clone git@github.com:nanomsg/nanomsg.git
$ ./configure
$ make
$ make check
$ sudo make install
```

For more details visit the official [nanomsg repo](https://github.com/nanomsg/nanomsg)

On OS X you can also do:

```shell
$ brew install nanomsg
```

2) Install nanoservice:

On Gentoo you can use this [portage overlay](https://github.com/sarnold/portage-overlay)
or try the PPA above for Xenial, Stretch, etc.

Alternatively, from project directory:

```shell
$ make install
```

Or via pip

```shell
$ pip install nanoservice (it's broken)
```


## Example Usage


The service:

```python
from nanoservice import Responder

def echo(msg):
    return msg

s = Responder('ipc:///tmp/service.sock')
s.register('echo', echo)
s.start()
```


```shell
$ python echo_service.py
```

The client:

```python
from nanoservice import Requester

c = Requester('ipc:///tmp/service.sock')
res, err = c.call('echo', 'hello world’)
print('Result is {}'.format(res))
```

```shell
$ python my_client.py
$ Result is: hello world
```

## Other

To run tests, first install tox (see Testing Notes below) then run:

```shell
$ make test
```

To run benchmarks

```shell
$ make bench
```

Check out examples directory for more examples.

## Testing Notes

Tests using python multiprocessing have been separated out into their own
directory (`test2`) due to sporadic failures triggering NanoMsgAPIError
exceptions, `Address already in use` followed by `Connection timed out`
(the unittest-based tests are still under the `test` directory).

Although random failures are occasionally seen in travis-ci tests, all
tests *should* run successfully with tox and pytest on the desktop as well
as package builds (ie, using FEATURES="test" in portage).

MIT Licensed
