=========
Changelog
=========

1.4.0 (2026-03-XX)
==================

* Dropped support for Python 3.5, 3.6, 3.7, 3.8, and 3.9
* Dropped support for Django 2.2, 3.0, and 3.1
* Confirmed support for Python 3.10, 3.11, 3.12, and 3.13
* Confirmed support for Django 4.2, 5.2, and 6.0
* All Python code is now formatted with `black`.

1.3.0 (2025-05-05)
==================

* Remove the abandoned dependency `webservices`, causing issues in the newer python versions because of the use of reserved names.


1.2.0 (2022-12-14)
==================

* Increased the max length of the Token.Token.redirect_to field to 1023


1.1.0 (2021-08-16)
==================

* Added support to update user-data on login (#61)


1.0.0 (2020-09-03)
==================

* Added changelog
* Added test framework
* Added support for Django 3.1
* Dropped support for Python 2.7 and Python 3.4
* Dropped support for Django < 2.2
* Aligned files with other addons
* Pinned itsdangerous<1.0.0 as the timestamp calculations changed
