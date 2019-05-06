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
PR = 40
GH_TOKEN = os.environ['GITHUB_TOKEN']


RM_URL = 'https://support.coopengo.com/'
RM_TOKEN = os.environ['REDMINE_TOKEN']

print('Trying to connect to GitHub...')
# or using an access token
g = Github(GH_TOKEN)
print('Connected ! \nRetrieving ' +REPO +'...', end='')
repo = g.get_user().get_repo(REPO)
print("\tOK !")

print("Retrieving pull request #" +str(PR), end='')
pr = repo.get_pull(PR)    
print("\tOK !")
    

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
        content = base64.b64decode(repo.get_contents(fileName, ref=pr.head.ref).content)
        content = content.decode('utf8')
        
        print("\t\tOK !")

        print("Update issue " +str(issueId) +"...", end='')
        redmine.issue.update(issueId, description=content)
        print("\t\tOK !")

        print("Delete file from Github...", end='')
        contentToDelete = repo.get_contents(fileName, ref=pr.head.ref)

        if pr.is_merged(): 
            print("\nThis pull request is already merged, impossible to delete file...")
        else:
            repo.delete_file(contentToDelete.path, "Remove "+fileName, contentToDelete.sha, pr.head.ref)
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
