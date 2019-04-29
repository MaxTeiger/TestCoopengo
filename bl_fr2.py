#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import datetime
import requests
import sys
import os
from collections import defaultdict
from mako.template import Template

REDMINE_URL = 'https://support.coopengo.com'

# Retrieve information from the input 
try:
    _, redmine_api_key, project_name, version_name, test_version = sys.argv
except ValueError:
    try:
        _, redmine_api_key, project_name, version_name = sys.argv
        test_version = None
    except ValueError:
        sys.stderr.write('''
Usage :
    bl.py <redmine_api_key> <project_name> <version_name> [<test_version>]

Example :
    bl.py <valid_api_key> Coog sprint a

    Will output html with all closed issues of test version "a" (if applicable,
    else all versions) of production version "sprint" of project "Coog".
''')
        sys.exit()

# Here, we find the right path to store issues.md files
thisfolder = os.path.dirname(os.path.abspath(__file__))
sep = "/TestCoopengo/"
goodFolder = thisfolder.split(sep, 1)[0] +"/doc/reviews/"
pathToFile = goodFolder +version_name +"-review2.html"
print("Path to file :\t " +pathToFile)

# We open the file with the right name
writeFile = open(pathToFile,"w") 

# We retrieve the template file
templateFile = thisfolder.split(sep, 1)[0] +"/doc/templates/review-template.html"
print("Path to template file :\t " +templateFile)


template = Template(filename=templateFile, default_filters=['decode.utf8'], input_encoding='utf-8', output_encoding='utf-8', encoding_errors='replace')
print("Template found")

# We request redmine for projects 
r = requests.get(REDMINE_URL + '/projects.json?limit=100',
    auth=(redmine_api_key, ''), verify=False)

parsed = r.json()['projects']
possible_projects = []

# If the request returned nothing 
if not parsed:
    sys.stderr.write('No projects found, check redmine api key !\n')
    sys.exit()

# for all projects in the response 
for project in parsed:
    # if we find the project we are looking for 
    if project['name'].encode('utf-8') == project_name:
        # set variables, and quit the loop
        project_identifier = project['identifier']
        project_id = project['id']
        break
    # We create a list of other projects
    else:
        possible_projects.append(project['name'].encode('utf-8'))

# if project hasn't been found
else:
    sys.stderr.write('Project %s not found\n\n' % project_name)
    sys.stderr.write('Possible projects :\n    ' +
        '\n    '.join(possible_projects))
    sys.stderr.write('\n')
    sys.exit()


# Asking redmine for issues on a certain project 
r = requests.get(REDMINE_URL +
    '/projects/%s/versions.json' % project_identifier,
    auth=(redmine_api_key, ''), verify=False)

# retrieve versions for this project
parsed = r.json()['versions']
possible_versions = []

# for each version 
for version in parsed:
    # if the version match the input 
    if version['name'].encode('utf-8') == version_name:
        # we define the variable for the version and quit the loop
        fixed_version_id = version['id']
        break
    else:
        # possible versions tab 
        possible_versions.append(version['name'].encode('utf-8'))
else:
    # if the version hasn't been found 
    sys.stderr.write('Version %s not found\n' % version_name)
    sys.stderr.write('Possible versions :\n    ' +
        '\n    '.join(possible_versions))
    sys.stderr.write('\n')
    sys.exit()

# return the list of issue related to a specific version of a specific project
def get_issues():
    offset = 20
    end = False

    # while end == False 
    while not end:
        
        # define URL of the request based on the input
        search_url = REDMINE_URL + '/issues.json?' \
            'offset=%s&limit=100&' % offset + \
            'project_id=%s&' % project_id + \
            'fixed_version_id=%i&' % fixed_version_id + \
            'status_id=closed&' \
            'sort=priority,updated_on'

        # make the request...
        r = requests.get(search_url, auth=(redmine_api_key, ''), verify=False)
        parsed = r.json()['issues']


        # if the request return nothing
        if not parsed:
            end = True
        else:
            for issue in parsed:
                # permet de retourner toutes les issues d'un coup (voir générateurs python) 
                yield issue
            offset += 100


version['custom_fields'] = {x['id']: x.get('value', '').encode('utf-8')
        for x in version['custom_fields'] if not x.get('multiple', False)}

# Initialize list...
features, bugs, params, scripts = [], [], [], []

# for each issue, create a list for each type of issues (features, bugs, params, script)
for issue in get_issues():

    issue['custom_fields'] = {x['id']: x.get('value', '').encode('utf-8')
        for x in issue['custom_fields'] if not x.get('multiple', False)}
    
    if issue['status']['id'] == 6:
        # Rejected => ignored
        continue

    if test_version and issue['custom_fields'][11] != test_version:
        continue

    issue['subject'] = issue['subject'].encode('utf-8')
    issue['updated_on'] = datetime.datetime.strptime(issue['updated_on'],
        '%Y-%m-%dT%H:%M:%SZ')

    if issue['tracker']['name'] == 'Feature':
        features.append(issue)
    else:
        bugs.append(issue)
    # Custom field 7 => Param
    if issue['custom_fields'].get(7, ''):
        params.append(issue)
    # Custom field 9 => Script
    if issue['custom_fields'].get(9, ''):
        scripts.append(issue)


render = template.render_unicode(version_name=version_name, 
    livraison_recette=version['custom_fields'][5], 
    livraison_production=version['custom_fields'][6], 
    featuresIssues=features,
    bugsIssues=bugs, 
    paramsIssues=params).encode('utf-8', 'replace')

writeFile.write(render)
print("File created :\t" +pathToFile)