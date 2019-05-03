#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
import requests
import sys
import base64
import re 




# retrieve 
REPO = 'TestCoopengo'
PR = 39
GH_TOKEN = os.environ['GH_TOKEN']

# Initialize GH information for api (template)
GH_URL_PULL = 'https://api.github.com/repos/MaxTeiger/{repo}/pulls/{pr}'
GH_URL_ISSUE = 'https://api.github.com/repos/MaxTeiger/{repo}/issues/{pr}'
GH_HEADERS = {'Authorization': 'Bearer {}'.format(GH_TOKEN)}

gh_pull=None
gh_issue=None
gh_labels=None
gh_commits=None
gh_commit=None

body_regexp = re.compile('.*(fix|ref) #(\d+)', re.M | re.I | re.S)

# function to retrieve request and parse to JSON
# in one time
def requestInJson(url, headers):
    r = requests.get(url, headers=GH_HEADERS)

    if r.status_code < 200 or r.status_code > 300:
        print(('error:gh:{}:{}:{}'.format(url, r.status_code, r.text)))
        sys.exit(1)

    return r.json()


# set the dict with information about the pull request
def set_gh_pull():
    global gh_pull
    url = GH_URL_PULL.format(repo=REPO, pr=PR)
    gh_pull = requestInJson(url, headers=GH_HEADERS)


# get issue for github repo
def set_gh_issue():
    global gh_issue
    url = GH_URL_ISSUE.format(repo=REPO, pr=PR)
    gh_issue = requestInJson(url, headers=GH_HEADERS)


# informations about files changed in the pull request 
def get_gh_files():
    global gh_filesInfo
    gh_filesInfo = dict()
    url = (GH_URL_PULL + '/files').format(repo=REPO, pr=PR)
    gh_files = requestInJson(url, headers=GH_HEADERS)

    for f in gh_files:
        gh_filesInfo[f['filename']] = f['contents_url']
    

def get_gh_file_content():
    url = ('https://api.github.com/repos/MaxTeiger/TestCoopengo/contents/README.md').format(repo=REPO, pr=PR)
    return requestInJson(url, headers=GH_HEADERS)


# def get_gh_commits():
#     global gh_pull, gh_commits
#     url = gh_pull['_links']['commits']['href']
#     r = requests.get(url, headers=GH_HEADERS)    
#     if r.status_code < 200 or r.status_code > 300:
#         print(('error:gh:{}:{}:{}'.format(url, r.status_code, r.text)))
#         sys.exit(1)
    
#     gh_commits=r.json()

# def get_spec_gh_commit(commit_number):
#     global gh_commits, gh_commit
#     url = gh_commits[commit_number]['url']
#     r = requests.get(url, headers=GH_HEADERS)    
#     if r.status_code < 200 or r.status_code > 300:
#         print(('error:gh:{}:{}:{}'.format(url, r.status_code, r.text)))
#         sys.exit(1)
    
#     gh_commit=r.json()


set_gh_pull()
set_gh_issue()
#get_gh_commits()
get_gh_files()

m = body_regexp.match(gh_pull['body'])
if m:
    rm_issue = int(m.group(2))
    print('REDMINE ISSUE NUMBER : ')
    print(rm_issue)
    print("\n\n\n")

print('GH PULL INFO : ')
print(gh_pull['body'])
print("\n\n\n")

print('GH ISSUES INFO')
print(gh_issue)
print("\n\n\n")

print('GH LABELS')
print(gh_labels)
print("\n\n\n")
  

print("GH FILES INFO")
for name, content_url in gh_filesInfo.items():
    if str(rm_issue) +".md" not in name:
        gh_filesInfo.pop(name)
    else:
        print("-------------------\nFilename :\t" +name +"\nContent URL :\t" +content_url) +"\n\n----------------------------------------------------------------\n"
        
        
        r = requests.get(content_url, headers=GH_HEADERS)

        if r.status_code < 200 or r.status_code > 300:
            
            print(('error:gh:{}:{}:{}'.format(url, r.status_code, r.text)))
            sys.exit(1)
        
        print(base64.b64decode(r.json()['content']))

print("\n\n\n")


# print(base64.b64decode(get_gh_file_content()['content']))
# print("\n\n\n")

# print("GH COMMITS INFO")
# print(gh_commits)
# print("\n\n\n")

# get_spec_gh_commit(len(gh_commits)-1)

# print("GH SPEC COMMIT INFO :")
# print(gh_commit)