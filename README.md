**Don't rely on this branch at the moment: It may be force-pushed to at any time.**

---

# reFill 2

**reFill** fixes [bare URLs](https://en.wikipedia.org/wiki/Wikipedia:Bare_URLs) on Wikipedia articles, semi-automatically. It extracts bibliographical information from web pages referenced by bare URL citations, generates complete references and replace them on the original page.

This README gives you all the details needed to set up a reFill instance for testing and development. If you only intend to use reFill, [the manual](https://en.wikipedia.org/wiki/User:Zhaofeng_Li) may be more helpful.

## Overview
The tool depends on three parts: A web server that serves the static frontend, a WSGI-compatible web server that serves Flask-based API, and Celery workers that fulfill the tasks submitted by users.

## Hints
### Result expiration
By default, tasks on Celery [expire in a day](http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-result_expires). If you are using a database backend, be sure to have `celery beat` running in order to clear the old results. This is especially important if you are running a public instance.

