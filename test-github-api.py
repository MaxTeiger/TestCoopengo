#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
import requests
import sys
import base64

# retrieve 
REPO = 'TestCoopengo'
PR = 37
GH_TOKEN = '8b60c86505bc4c46c9725e8559e1bcc38d096d57'

# Initialize GH information for api (template)
GH_URL_PULL = 'https://api.github.com/repos/MaxTeiger/{repo}/pulls/{pr}'
GH_URL_ISSUE = 'https://api.github.com/repos/MaxTeiger/{repo}/issues/{pr}'
GH_HEADERS = {'Authorization': 'Bearer {}'.format(GH_TOKEN)}

gh_pull=None
gh_issue=None
gh_labels=None
gh_commits=None
gh_commit=None


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

def get_gh_commits():
    global gh_pull, gh_commits
    url = gh_pull['_links']['commits']['href']
    r = requests.get(url, headers=GH_HEADERS)    
    if r.status_code < 200 or r.status_code > 300:
        print(('error:gh:{}:{}:{}'.format(url, r.status_code, r.text)))
        sys.exit(1)
    
    gh_commits=r.json()

def get_spec_gh_commit(commit_number):
    global gh_commits, gh_commit
    url = gh_commits[commit_number]['url']
    r = requests.get(url, headers=GH_HEADERS)    
    if r.status_code < 200 or r.status_code > 300:
        print(('error:gh:{}:{}:{}'.format(url, r.status_code, r.text)))
        sys.exit(1)
    
    gh_commit=r.json()


set_gh_pull()
set_gh_issue()
set_gh_labels()
get_gh_commits()


print('GH PULL INFO : ')
print(gh_pull)
print("\n\n\n")

print('GH ISSUES INFO')
print(gh_issue)
print("\n\n\n")

print('GH LABELS')
print(gh_labels)
print("\n\n\n")

print("GH FILES INFO")
print(get_gh_files())
print("\n\n\n")


# print(base64.b64decode(get_gh_file_content()['content']))
# print("\n\n\n")

print("GH COMMITS INFO")
print(gh_commits)
print("\n\n\n")

get_spec_gh_commit(len(gh_commits)-1)

print("GH SPEC COMMIT INFO :")
print(gh_commit)




