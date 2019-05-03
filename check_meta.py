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

REPO = os.environ['DRONE_REPO_NAME']
PR = os.environ['DRONE_PULL_REQUEST']
GH_TOKEN = os.environ['GITHUB_TOKEN']
RM_TOKEN = os.environ['REDMINE_TOKEN']

GH_URL_PULL = 'https://api.github.com/repos/coopengo/{repo}/pulls/{pr}'
GH_URL_ISSUE = 'https://api.github.com/repos/coopengo/{repo}/issues/{pr}'

# Initialize information for Redmine
RM_URL = 'https://support.coopengo.com/issues/{issue}.json'
RM_HEADERS = {'X-Redmine-API-Key': RM_TOKEN}

# compile regular expression for title, body, changelog
title_regexp = re.compile('\w+: .+')
body_regexp = re.compile('.*(fix|ref) #(\d+)', re.M | re.I | re.S)

bug_regexp = re.compile(
    '## \[title_en\]((.|\n)*)## \[title_fr\]((.|\n)*)### \[repro_fr\]((.|\n)*)### \[correction_fr\]((.|\n)*)\[parametrage_fr\]((.|\n)*)### \[scripts_fr\]((.|\n)*)## \[business_modules\]((.|\n)*)## \[original_description\]((.|\n)*$)')
feature_regexp = re.compile(
    '## \[title_en\]((.|\n)*)## \[title_fr\]((.|\n)*)### \[parametrage_fr\]((.|\n)*)### \[scripts_fr\]((.|\n)*)## \[business_modules\]((.|\n)*)## \[original_description\]((.|\n)*$)')
minimum_regexp = re.compile('[\s\S]{15,}')


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
    isHere = False

    gh_files = requestInJson(url, headers=GH_HEADERS)
    for f in gh_files:
        if str(rm_issue) + ".md" in f['filename']:
            print(f['filename'] +" added to the queue...")
            ghIssueFiles[f['filename']] = f['contents_url']
            isHere = True

    if isHere:    
        return gh_files

    else:
        print("content :'+fg('red') + 'ko' +attr(0) +':{}.md".format(rm_issue))
        sys.exit(1)



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
    print('labels  :'+fg('green') + 'ok' + attr(0))
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
            print('title   :'+fg('green') + 'ok' +attr(0))
        else:
            ok = False
            print('title   :'+fg('red') + 'ko' +attr(0) )
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
            print(('body    :'+fg('green') + 'ok' +attr(0) +':issue:{}'.format(issue)))
            rm_issue = issue

    # if it doesn't match
    else:
        ok = False
        print('body    :'+fg('red') + 'ko' +attr(0) )
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
        if str(rm_issue) in name:
            r = requestInJson(content, headers=GH_HEADERS)
            fileContent = base64.b64decode(r['content'])



    if real_issue_type == 'fea':
        m = feature_regexp.match(fileContent.decode('utf8'))

        # if the file match the pattern, tags are respected
        if m:

            print('content :'+fg('green') + 'ok' +attr(0) +':fea')
            title_en = m.group(1).replace("(required)", "")
            title_fr = m.group(3).replace("(required)", "")
            parametrage_fr = m.group(5).replace(
                "<Paramétrage (éventuel) à faire>", "")
            scripts_fr = m.group(7).replace("<Scripts à passer>", "")
            business_modules = m.group(9)
            original_description = m.group(11).replace(
                "(required / automatic)", "")

            if not minimum_regexp.match(title_en):
                ok = False
                print('content :'+fg('red') + 'ko' +attr(0) +':title not specified')
            else:
                print('content :'+fg('green') + 'ok' +attr(0) +':title_en')

            if not minimum_regexp.match(title_fr):
                ok = False
                print('content :'+fg('red') + 'ko' +attr(0) +':title not specified')
            else:
                print('content :'+fg('green') + 'ok' +attr(0) +':title_fr')
            if not minimum_regexp.match(business_modules):
                ok = False
                print('content :'+fg('red') + 'ko' +attr(0) +':business_modules not specified')
            else:
                print('content :'+fg('green') + 'ok' +attr(0) +':business_modules')
            if not minimum_regexp.match(original_description):
                ok = False
                print('content :'+fg('red') + 'ko' +attr(0) +':original_description')
            else:
                print('content :'+fg('green') + 'ok' +attr(0) +':original_description')

        else:
            print('content :'+fg('red') + 'ko' +attr(0) +':tags not respected')
            ok = False

    elif real_issue_type == 'bug':
        m = bug_regexp.match(fileContent.decode('utf8'))

        # if the file match the pattern, tags are respected
        if m:
            print('content :'+fg('green') + 'ok' +attr(0) +':bug')
            title_en = m.group(1).replace("(required)", "")
            title_fr = m.group(3).replace("(required)", "")
            parametrage_fr = m.group(9).replace(
                "<Paramétrage (éventuel) à faire>", "")
            scripts_fr = m.group(11).replace("<Scripts à passer>", "")
            business_modules = m.group(13)
            original_description = m.group(15).replace(
                "(required / automatic)", "")

            if not minimum_regexp.match(title_en):
                ok = False
                print('content :'+fg('red') + 'ko' +attr(0) +':title not specified')
            else:
                print('content :'+fg('green') + 'ok' +attr(0) +':title_en')

            if not minimum_regexp.match(title_fr):
                ok = False
                print('content :'+fg('red') + 'ko' +attr(0) +':title not specified')
            else:
                print('content :'+fg('green') + 'ok' +attr(0) +':title_fr')
            if not minimum_regexp.match(business_modules):
                ok = False
                print('content :'+fg('red') + 'ko' +attr(0) +':business_modules not specified')
            else:
                print('content :'+fg('green') + 'ok' +attr(0) +':business_modules')
            if not minimum_regexp.match(original_description):
                ok = False
                print('content :'+fg('red') + 'ko' +attr(0) +':original_description')
            else:
                print('content :'+fg('green') + 'ok' +attr(0) +':original_description')

        else:
            print('content :'+fg('red') + 'ko' +attr(0) +':tags not respected')
            ok = False

    if ok:
        print('content :'+fg('green') + 'ok' +attr(0))
    else:
        print('content :'+fg('red') + 'ko' +attr(0) )
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

        print(('redmine :'+fg('green') + 'ok' +attr(0) +':issue:{}'.format(issue['id'])))

        # if issue type is defined (issue type == feature or bug)
        if rm_issue_type:
            # ensure the issue type is the same on redmine
            issue_type = rm_trackers[issue['tracker']['id']]
            real_issue_type = issue_type

            #
            if issue_type == rm_issue_type:
                print(('redmine :'+fg('green') + 'ok' +attr(0) +':issue_type:{}'.format(issue_type)))
            else:
                ok = False
                print(('redmine :'+fg('red') + 'ko' +attr(0) +':issue_type:{}-{}'.format(
                    issue_type, rm_issue_type)))

            issue_project = issue['project']['id']
            if issue_project in issues_projects:
                print(('redmine :'+fg('green') + 'ok' +attr(0) +':issue_project:{}'.format(
                    issue['project']['name'])))
            else:
                ok = False
                print(('redmine :'+fg('red') + 'ko' +attr(0) +':issue_project:{}'.format(
                    issue['project']['name'])))

        # if issue type is not defined
        else:
            ok = False
            print('redmine :'+fg('red') + 'ko' +attr(0) +':issue_type:empty')

    # if redmine issue is not defined
    elif rm_issue is None:
        # No problem if issue is #0000
        ok = False
        print('redmine :'+fg('red') + 'ko' +attr(0) +':issue:empty')

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
    ok = check_labels() and ok
    ok = check_title() and ok
    ok = check_body() and ok
    ok = check_redmine() and ok
    ok = check_content() and ok

    print("main:ok")


if __name__ == '__main__':
    main()
