Positronic Brain
================

<img align="right" src="https://rawgit.com/develersrl/positronic-brain/master/logo.svg" width="200" height="200"/>

> *Opinionated BuildBot workflow.*

[![Build Status](https://img.shields.io/travis/develersrl/positronic-brain.svg?style=flat)](https://travis-ci.org/develersrl/positronic-brain)
[![Coverage Status](http://img.shields.io/coveralls/develersrl/positronic-brain.svg?style=flat)](https://coveralls.io/r/develersrl/positronic-brain)
[![License](http://img.shields.io/badge/license-GPLv2-blue.svg?style=flat)](http://choosealicense.com/licenses/gpl-2.0/)

Positronic Brain makes it extremely easy to get up and running with your BuildBot server by dropping
few lines in your `master.cfg` file. Gone are the days of having to figure out how to wire all
pieces together.

Adding a positronic brain to your BuildBot brings you:

* Sensible defaults for your BuildBot master.
* Notification emails sent to _developers_ after a build failure.
* Notification emails sent to _administrators_ for all builds on all projects.
* No need to mess with Change Sources or Schedulers.
* Archiving of artifacts on the master after each successful build.
* Automatic deletion of old artifacts on the master.


Installation
------------

This package is not being published to PyPI, so for the time being you have to install it by
running:

    pip install https://github.com/develersrl/positronic-brain/archive/master.zip#egg=positronic-brain

Please note that this package depends on a very specific version of the BuildBot master and you have
to make sure to have it installed first (see [requirements.txt](requirements.txt) for more details).


Usage
-----

In your BuildBot master configuration file (`master.cfg`) import everything from the
"positronic.brain" package and perform some basic initialization:

```python
from positronic.brain import *

#      basedir=basedir looks weird, but we need it.
master(basedir=basedir, url='https://buildbot.example.com/')

worker('my-first-worker', 'secretpassword')
worker('my-second-worker', 'anothersecretpassword')

with FreestyleJob('my-project', workers=['my-first-worker', 'my-second-worker']) as j:
    j.checkout('project', 'svn+ssh://svn.example.com/svn/project', 'trunk')
    j.command('make')
    j.command('make', 'check')
    j.command('make', 'packages')
    j.notify('dev1@example.com')
```
