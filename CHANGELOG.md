Changelog
=========

### 0.7.2-2

* Convert to PEP 517/518 project format
* Migrate travis CI to github
* Limit CI to Python 3.6 - 3.9 on focal and macos

### 0.7.2p1

* Pull in enhancements from Jan Bos fork
* Minor integration and test cleanup


### 0.7.2

* Add pickle encoder
* Add timeouts to tests


### 0.7.1

* Subscriber bug fix


### 0.7.0

This release includes heavy refactoring

* Renamed Classes: `Client` becomes `Requester`, and `Service` becomes `Responder`. Although old classes are still accessible, when instantiated they will emit warnings.
* Added a new abstract class Endpoint
* Rewrote process method of Subscriber
* Any endpoint (Requester, Publisher, etc) can now be `binded` OR `connected` to a nanomsg address; simply supply the boolean flag `bind` when instantiated.
* Add support for timeouts. When instantiating an endpoint, just supply a pair `timeouts=(10, 10)` which represents (sendTimeout, recvTimeout) AS MILLISECONDS


### 0.5.0

* Part of service module were rewritten, so that it does not explode when failing to decode a request
* Better testing


### 0.4.1

* Improve authenticator performance


### 0.4.0

* Rename Service and Client `recv` method to `receive`
* Add crypto module
* Add optional message authentication between endpoints
* PubSub logic moved to a new module
* PubClient renamed to Publisher
* SubService renamed to Subscriber

### 0.1.0

* Initial release
