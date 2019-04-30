#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import os
import mistune
import requests

REDMINE_URL = 'https://support.coopengo.com'
REDMINE_TOKEN = os.environ['REDMINE_TOKEN']

# Request on the redmine page to retrieve json about the issue 
data = requests.get(
    REDMINE_URL + '/issues/%s.json' % 11466,
    auth=(REDMINE_TOKEN, ''))

# If the website return a json object when an error occurs, it raise the status 
# of the response (maybe check if the status != 200 ?)
data.raise_for_status()

# parse data in order to use them
parsed = data.json()['issue']


print(mistune.markdown(parsed['description']))

