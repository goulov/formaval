#!/bin/sh

gunicorn --workers 4 --bind localhost:8800 formaval:app --daemon
