#!/usr/bin/env python3
# vim: ft=python ts=4 sw=4 et
# coding: utf8

import os
import re
import sys
from github import Github
from redminelib import Redmine
import base64

# Retrieve from the environment variables usefull infos
# after Drone as cloned the project

REPO = 'TestCoopengo'
PR = 39
GH_TOKEN = os.environ['GITHUB_TOKEN']


RM_URL = 'https://support.coopengo.com/'
RM_TOKEN = os.environ['REDMINE_TOKEN']


filePath = "doc/issues/{issueId}.md"


body_regexp = re.compile('.*(fix|ref) #(\d+)', re.M | re.I | re.S)

print('Trying to connect...')
# or using an access token
g = Github(GH_TOKEN)
print('Connected ! \nRetrieving ' +REPO +'...', end='')

repo = g.get_user().get_repo(REPO)
print("\tOK !")

print("Retrieving pull request #" +str(PR), end='')
pr = repo.get_pull(PR)    
print("\tOK !")



m = body_regexp.match(pr.body)
if m:
    # retrieve ticket number (issue number)
    issue = int(m.group(2))
    print("Pull request for issue : " +str(issue) +"\tOK !")
else:
    print("Body of the pull request not matching")
    sys.exit(1)



fileNames = []
for file in pr.get_files():
    fileNames.append(file.filename)


# Updating Redmine 
print("\nTrying to connect to RedMine...", end='')
redmine = Redmine(RM_URL, key=RM_TOKEN)
print("\tOK !")


for fileName in fileNames:
    if 'doc/issues/' in fileName and fileName.endswith('.md'):
        tmpFileName = fileName.replace('doc/issues/','')
        issueId = int(tmpFileName.replace('.md', ''))


        print("\nRetrieving the file...", end='')
        # Retrieve content of relative file
        content = base64.b64decode(repo.get_contents(fileName).content)
        content = content.decode('utf8')
        print("\t\tOK !")

        print("Update issue " +str(issueId) +"...", end='')
        redmine.issue.update(issueId, description=content)
        print("\t\tOK !")

        print("Delete file from Github...", end='')
        contentToDelete = repo.get_contents(fileName)

        if pr.is_merged: 
            print("\nThis pull request is already merged, impossible to delete file...")
        else:
            repo.delete_file(contentToDelete.path, "Remove "+fileName, contentToDelete.sha, pr.title)
            print("\tOK !")





# Delete files from GitHub
# Good

# for repo in g.get_user().get_repos():
#     if repo.name == REPO:
#         print('Great found the repo: ' +repo.name)
#         break




# def main():


# if __name__ == '__main__':
#     main()
