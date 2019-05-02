#!/usr/bin/env python3
# vim: ft=python ts=4 sw=4 et
# -*- encoding: utf-8 -*-

import os
import re
import sys
import requests
from colored import fg, bg, attr
import base64

# Retrieve from the environment variables usefull infos
# after Drone as cloned the project

REPO = "TestCoopengo"
PR = 39
GH_TOKEN = os.environ['GH_TOKEN']
RM_TOKEN = os.environ['REDMINE_TOKEN']

# Initialize GH information for api (template)
GH_URL_PULL = 'https://api.github.com/repos/MaxTeiger/{repo}/pulls/{pr}'
GH_URL_ISSUE = 'https://api.github.com/repos/MaxTeiger/{repo}/issues/{pr}'
GH_HEADERS = {'Authorization': 'Bearer {}'.format(GH_TOKEN)}

# Initialize information for Redmine
RM_URL = 'https://support.coopengo.com/issues/{issue}.json'
RM_HEADERS = {'X-Redmine-API-Key': RM_TOKEN}

# compile regular expression for title, body, changelog
title_regexp = re.compile('\w+: .+')
body_regexp = re.compile('.*(fix|ref) #(\d+)', re.M | re.I | re.S)
changelog_regexp = re.compile('\* (BUG|FEA|OTH)#(\d+)')
bug_regexp = re.compile('## \[title_en\]((.|\n)*)## \[title_fr\]((.|\n)*)### \[repro_fr\]((.|\n)*)### \[correction_fr\]((.|\n)*)\[parametrage_fr\]((.|\n)*)### \[scripts_fr\]((.|\n)*)## \[business_modules\]((.|\n)*)## \[original_description\]((.|\n)*$)')
feature_regexp = re.compile('## \[title_en\]((.|\n)*)## \[title_fr\]((.|\n)*)### \[parametrage_fr\]((.|\n)*)### \[scripts_fr\]((.|\n)*)## \[business_modules\]((.|\n)*)## \[original_description\]((.|\n)*$)')

# dict containing tracker name values
rm_trackers = {1: 'bug', 2: 'fea'}
# 35 stand for Non-Coog
issues_projects = [1, 31, 37, 35]

# initialize variables
gh_pull = None
# 
gh_issue = None
# list of labels for the specific pull request 
gh_labels = None
# list of modified files in the repository
ghIssueFiles = None
# equals to the identifier defined in the body of the pull request 
rm_issue = None

# feature or bug => defined depending on the label on the gh pull request 
rm_issue_type = None


# function to retrieve request and parse to JSON
# in one time
def requestInJson(url, headers):
    r = requests.get(url, headers=headers)

    if r.status_code < 200 or r.status_code > 300:
        print(('error   :gh:{}:{}:{}'.format(url, r.status_code, r.text)))
        sys.exit(1)

    return r.json()

# set the GitHub pull JSON object
def set_gh_pull():
    global gh_pull
    url = GH_URL_PULL.format(repo=REPO, pr=PR)
    gh_pull = requestInJson(url, headers=GH_HEADERS)

# get issue from github repo
def set_gh_issue():
    global gh_issue
    url = GH_URL_ISSUE.format(repo=REPO, pr=PR)
    gh_issue = requestInJson(url, headers=GH_HEADERS)

# name of issues stored in an array
def set_gh_labels():
    global gh_labels
    gh_labels = [l['name'] for l in gh_issue['labels']]

# informations about files changed in the pull request
# create a dict of modified files 
# key    : filename
# Value  : URL to the content of the file
# Moreover, this function return the object from github
def get_gh_files():

    global ghIssueFiles
    ghIssueFiles = dict()
    url = (GH_URL_PULL + '/files').format(repo=REPO, pr=PR)

    gh_files = requestInJson(url, headers=GH_HEADERS)
    for f in gh_files:
        if str(rm_issue) +".md" in f['filename']:
            ghIssueFiles[f['filename']] = f['contents_url']
    
    return gh_files


# Labels check, retrieve the type of the issue (if it is a feature or a bug)
# define :
# rm_issue_type
# check run order : 1st
def check_labels():

    global rm_issue_type
    if 'enhancement' in gh_labels:
        rm_issue_type = 'fea'
    elif 'bug' in gh_labels:
        rm_issue_type = 'bug'
    print(fg('green') +'labels  :ok' +attr(0))
    return True

# check the title of the pull request (if it match the regex above
# or if the title can be bypassed)
# define :
# nothing just check title
# check run order : 2nd
def check_title():
    ok = True
    if 'bypass title check' in gh_labels:
        print('title   :bypass')
    else:
        if title_regexp.match(gh_pull['title']):
            print('title   :ok')
        else:
            ok = False
            print('title   :ko')
    return ok

# Check the body of the pull request
# if the body of the pull request match the
# regex above,
# define :
# rm_issue
# check run order : 3rd
def check_body():
    ok = True
    m = body_regexp.match(gh_pull['body'])

    # it maatch
    if m:
        # retrieve ticket number (issue number)
        issue = int(m.group(2))
        # what i don't understand is here, rm_issue is ==None everytime ?
        global rm_issue
        # if both are defined but doesn't match 
        if issue and rm_issue and issue != rm_issue:
            ok = False
            print(('body    :ko:issue:{}-{}'.format(issue, rm_issue)))
        else:
            # set rm_issue
            print(('body    :ok:issue:{}'.format(issue)))
            rm_issue = issue

    # if it doesn't match
    else:
        ok = False
        print('body    :ko')
    return ok

# Check if files are present and if the content match 

# pattern if feature : ## \[title_en\]((.|\n)*)## \[title_fr\]((.|\n)*)### \[parametrage_fr\]((.|\n)*)### \[scripts_fr\]((.|\n)*)## \[business_modules\]((.|\n)*)## \[original_description\]((.|\n)*$)
# grp1 = title_en, grp3 = title_fr, grp5 = parametrages_fr, grp7 = scripts_fr, grp9 = business modules, grp11 = original description

# pattern if bug : ## \[title_en\]((.|\n)*)## \[title_fr\]((.|\n)*)### \[repro_fr\]((.|\n)*)### \[correction_fr\]((.|\n)*)\[parametrage_fr\]((.|\n)*)### \[scripts_fr\]((.|\n)*)## \[business_modules\]((.|\n)*)## \[original_description\]((.|\n)*$)
# grp1 = title_en, grp3 = title_fr, grp5 = Scenario de reproduction, grp7 = correction, grp9 = parametrages_fr, grp11 = scripts_fr, grp13 = business modules, grp15 = original description


def check_content():
    ok = True
    gh_files = get_gh_files()

    for name, content in ghIssueFiles.items():
        print("-------------------\nFilename :\t" +name +"\nContent URL :\t" +content +"\n\n----------------------------------------------------------------\n")
        r = requestInJson(content, headers=GH_HEADERS)
        fileContent = base64.b64decode(r['content'])

    if real_issue_type == 'fea':
        m = feature_regexp.match(fileContent.decode('utf8'))
        title_en = m.group(1).replace("(required)","")
        title_fr = m.group(3).replace("(required)","")
        parametrage_fr = m.group(5).replace("<Paramétrage (éventuel) à faire>","")
        scripts_fr = m.group(7).replace("<Scripts à passer>","")
        business_modules = m.group(9)
        original_description = m.group(11).replace("(required / automatic)","")
        print(original_description)
    
    elif real_issue_type == 'bug':
        

    return ok


#
def check_redmine():
    ok = True
    global rm_issue, rm_issue_type, real_issue_type

    # if rm issue is defined
    if rm_issue:
        # connect to redmine
        url = RM_URL.format(issue=rm_issue)
        issue = requestInJson(url, headers=RM_HEADERS)['issue']

        print(('redmine :ok:issue:{}'.format(issue['id'])))

        # if issue type is defined (issue type == feature or bug)
        if rm_issue_type:
            # ensure the issue type is the same on redmine
            issue_type = rm_trackers[issue['tracker']['id']]
            real_issue_type = issue_type

            # 
            if issue_type == rm_issue_type:
                print(('redmine :ok:issue_type:{}'.format(issue_type)))
            else:
                ok = False
                print(('redmine :ko:issue_type:{}-{}'.format(
                    issue_type, rm_issue_type)))

            issue_project = issue['project']['id']
            if issue_project in issues_projects:
                print(('redmine :ok:issue_project:{}'.format(
                    issue['project']['name'])))
            else:
                ok = False
                print(('redmine :ko:issue_project:{}'.format(
                    issue['project']['name'])))

        # if issue type is not defined
        else:
            ok = False
            print('redmine :ko:issue_type:empty')
    
    # if redmine issue is not defined
    elif rm_issue is None:
        # No problem if issue is #0000
        ok = False
        print('redmine :ko:issue:empty')

    return ok



def main():

    # set usefull data
    set_gh_pull()
    set_gh_issue()
    set_gh_labels()

    # checking args send by user
    # if user send more than 2 values,
    if len(sys.argv) >= 2 and sys.argv[1] == 'tests':
        # if tests checks needs to be bypassed
        if 'bypass tests check' in gh_labels:
            # no need to check exit without error
            print('tests:bypass')
            sys.exit(0)
        else:
            # exit with error
            sys.exit(1)

    # Special manner to check if every check is complete
    ok = True
    ok = check_labels()  and ok
    ok = check_title()   and ok
    ok = check_body()    and ok
    ok = check_redmine() and ok
    ok = check_content() and ok



    print("main:ok")


if __name__ == '__main__':
    main()
