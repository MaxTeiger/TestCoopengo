#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import requests
import sys
from collections import defaultdict

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

# 
else:
    sys.stderr.write('Project %s not found\n\n' % project_name)
    sys.stderr.write('Possible projects :\n    ' +
        '\n    '.join(possible_projects))
    sys.stderr.write('\n')
    sys.exit()

r = requests.get(REDMINE_URL +
    '/projects/%s/versions.json' % project_identifier,
    auth=(redmine_api_key, ''), verify=False)
parsed = r.json()['versions']
possible_versions = []
for version in parsed:
    if version['name'].encode('utf-8') == version_name:
        fixed_version_id = version['id']
        break
    else:
        possible_versions.append(version['name'].encode('utf-8'))
else:
    sys.stderr.write('Version %s not found\n' % version_name)
    sys.stderr.write('Possible versions :\n    ' +
        '\n    '.join(possible_versions))
    sys.stderr.write('\n')
    sys.exit()


def get_issues():
    offset = 0
    end = False
    while not end:
        search_url = REDMINE_URL + '/issues.json?' \
            'offset=%s&limit=100&' % offset + \
            'project_id=%s&' % project_id + \
            'fixed_version_id=%i&' % fixed_version_id + \
            'status_id=closed&' \
            'sort=priority,updated_on'

        r = requests.get(search_url, auth=(redmine_api_key, ''), verify=False)
        parsed = r.json()['issues']
        if not parsed:
            end = True
        else:
            for issue in parsed:
                yield issue
            offset += 100


version['custom_fields'] = {x['id']: x.get('value', '').encode('utf-8')
        for x in version['custom_fields'] if not x.get('multiple', False)}

features, bugs, params, scripts = defaultdict(list), defaultdict(list), [], []
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
        features[issue['priority']['name']].append(issue)
    else:
        bugs[issue['priority']['name']].append(issue)
    # Custom field 7 => Param
    if issue['custom_fields'].get(7, ''):
        params.append(issue)
    # Custom field 9 => Script
    if issue['custom_fields'].get(9, ''):
        scripts.append(issue)


def get_issue_id(issue):
    return '<a href="https://support.coopengo.com/issues/%i' % issue['id'] + \
        '">%i</a>' % issue['id']


print('<html>')
print('<head>')
print('<meta charset="utf-8"/>')
print('<style>')
print('''
h1 {
    font-size: 150%;
}
h2 {
    font-size: 120%;
}
table {
    border:#ccc 1px solid
    table-layout: fixed;
    width: 600px;
    border-width: 1px;
    border-color: #666666;
    border-collapse: collapse;
    border-spacing: 10px;
}
th {
    font-size: 90%;
    align: left;
    border-width: 1px;
    padding: 5px;
    border-style: solid;
    border-color: #666666;
    background-color: #dedede;
}
td {
    font-size: 80%;
    border-width: 1px;
    vertical-align: middle;
    padding: 2px;
    border-style: solid;
    border-color: #666666;
    background-color: #ffffff;
}
tr td:first-child {
    width: 70px;
}
tr td:last-child {
    width: 40px;
}
''')
print('</style>')
print('</head>')
print('<body>')

count = 1
print('<h2>Version: %s</h2>' % version_name)
print('<p>Livraison en recette: %s</p>' % version['custom_fields'][5])
print('<p>Livraison en production: %s</p>' % version['custom_fields'][6])
if features:
    print('<h2>%i. Fonctionnalités</h2>' % count)
    count += 1
    print('<table>')
    print('    <tr><th>#</th><th>Priorité</th><th>Sujet</th>' + \
        '<th>Version</th></tr>')
    for priority in ('Immediate', 'High', 'Normal', 'Low'):
        issues = features[priority]
        if not issues:
            continue
        for issue in sorted(issues, key=lambda x: x['custom_fields'][11]):
            print('    <tr><td>' + '</td><td>'.join([get_issue_id(issue),
                    issue['priority']['name'].encode('utf-8'),
                    issue['subject'],
                    issue['custom_fields'][11],
                    ]) + '</td></tr>')
    print('</table>')

if bugs:
    print('<h2>%i. Anomalies</h2>' % count)
    count += 1
    print('<table>')
    print('    <tr><th>#</th><th>Priorité</th><th>Sujet</th>' + \
        '<th>Version</th></tr>')
    for priority in ('Immediate', 'High', 'Normal', 'Low'):
        issues = bugs[priority]
        if not issues:
            continue
        for issue in sorted(issues, key=lambda x: x['custom_fields'][11]):
            print('    <tr><td>' + '</td><td>'.join([get_issue_id(issue),
                    issue['priority']['name'].encode('utf-8'),
                    issue['subject'],
                    issue['custom_fields'][11],
                    ]) + '</td></tr>')
    print('</table>')


if params:
    print('<h2>%i. Params</h2>' % count)
    count += 1
    print('<table>')
    print('    <tr><th>#</th><th>Subject</th><th width="200">Param</th> ' + \
        '<th>Version</th></tr>')
    for issue in sorted(params, key=lambda x: x['custom_fields'][11]):
        print('    <tr><td>' + get_issue_id(issue) + '</td><td>' + \
            issue['subject'] + '</td><td>' + \
            issue['custom_fields'][7] + '</td><td>' + \
            issue['custom_fields'][11] + '</td></tr>')
    print('</table>')


if scripts:
    print('<h2>%i. Scripts</h2>' % count)
    count += 1
    print('<table>')
    print('    <tr><th>#</th><th>Subject</th><th width="200">Script</th>' + \
        '<th>Version</th></tr>')
    for issue in sorted(scripts, key=lambda x: x['custom_fields'][11]):
        print('    <tr><td>' + get_issue_id(issue) + '</td><td>' + \
            issue['subject'] + '</td><td>' + \
            issue['custom_fields'][9] + '</td><td>' + \
            issue['custom_fields'][11] + '</td></tr>')
    print('</table>')
print('</body>')
print('</html>')
