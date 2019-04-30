#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
import requests
import sys
import base64

# retrieve 
REPO = 'TestCoopengo'
PR = 37
GH_TOKEN = 'githubtoken'

# Initialize GH information for api (template)
GH_URL_PULL = 'https://api.github.com/repos/MaxTeiger/{repo}/pulls/{pr}'
GH_URL_ISSUE = 'https://api.github.com/repos/MaxTeiger/{repo}/issues/{pr}'
GH_HEADERS = {'Authorization': 'Bearer {}'.format(GH_TOKEN)}

gh_pull=None
gh_issue=None
gh_labels=None
def set_gh_pull():
    url = GH_URL_PULL.format(repo=REPO, pr=PR)
    r = requests.get(url, headers=GH_HEADERS)
    if r.status_code < 200 or r.status_code > 300:
        print(('error:gh:{}:{}:{}'.format(url, r.status_code, r.text)))
        sys.exit(1)
    global gh_pull
    gh_pull = r.json()


# get issue for github repo
def set_gh_issue():
    url = GH_URL_ISSUE.format(repo=REPO, pr=PR)
    r = requests.get(url, headers=GH_HEADERS)
    if r.status_code < 200 or r.status_code > 300:
        print(('error:gh:{}:{}:{}'.format(url, r.status_code, r.text)))
        sys.exit(1)
    global gh_issue
    gh_issue = r.json()

# name of issues stored in an array
def set_gh_labels():
    global gh_labels
    gh_labels = [l['name'] for l in gh_issue['labels']]


# informations about files changed in the pull request 
def get_gh_files():
    url = (GH_URL_PULL + '/files').format(repo=REPO, pr=PR)
    r = requests.get(url, headers=GH_HEADERS)
    if r.status_code < 200 or r.status_code > 300:
        print(('error:gh:{}:{}:{}'.format(url, r.status_code, r.text)))
        sys.exit(1)
    return r.json()

def get_gh_file_content():
    url = ('https://api.github.com/repos/MaxTeiger/TestCoopengo/contents/README.md').format(repo=REPO, pr=PR)
    r = requests.get(url, headers=GH_HEADERS)
    if r.status_code < 200 or r.status_code > 300:
        print(('error:gh:{}:{}:{}'.format(url, r.status_code, r.text)))
        sys.exit(1)
    return r.json()

set_gh_pull()
set_gh_issue()
set_gh_labels()



print(gh_pull)
print("\n\n\n")
print(gh_issue)
print("\n\n\n")
print(gh_labels)
print("\n\n\n")
print(get_gh_files())
print("\n\n\n")
print(base64.b64decode(get_gh_file_content()['content']))




