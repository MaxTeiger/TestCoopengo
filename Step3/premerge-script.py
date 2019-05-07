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

REPO = os.environ['REPO_NAME'] # OR RETRIEVE THE NAME OF THE GITHUB REPO (TestCoopengo for tests)
PR = os.environ['PULL_REQUEST_ID'] # OR RETRIEVE PULL REQUEST ID (39 or 40)
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
pr = repo.get_pull(int(PR))    
print("\tOK !")
    

fileNames = []
for file in pr.get_files():
    fileNames.append(file.filename)


# Updating Redmine 
print("\nTrying to connect to RedMine...", end='')
redmine = Redmine(RM_URL, key=RM_TOKEN)
print("\tOK !")

# for each file
for fileName in fileNames:
    if 'doc/issues/' in fileName and fileName.endswith('.md'):
        tmpFileName = fileName.replace('doc/issues/','')
        issueId = int(tmpFileName.replace('.md', ''))

        # read file content 
        try: 
            print("\nRetrieving the file...", end='')
            # Retrieve content of relative file
            content = base64.b64decode(repo.get_contents(fileName, ref=pr.head.ref).content)
            content = content.decode('utf8')
            print("\t\tOK !")
        except:
            print("\t\tError : File doesn't exists")
            continue
            
        # Update the corresponding issue on redmine with the content of the file
        try: 
            print("Update issue " +str(issueId) +"...", end='')
            redmine.issue.update(issueId, description=content)
            print("\t\tOK !")
        except:
            print("\t\tError : Issue doesn't exist or impossible to read the content of the file")
            continue
            
        # delete the file in github repo
        try: 
            print("Delete file from Github...", end='')
            contentToDelete = repo.get_contents(fileName, ref=pr.head.ref)

            if pr.is_merged(): 
                print("\nThis pull request is already merged, impossible to delete file...")
            else:
                repo.delete_file(contentToDelete.path, "Remove "+fileName, contentToDelete.sha, pr.head.ref)
                print("\tOK !")
        except:
            print("\tError : Impossible to delete file")
            continue

    # c'est même possible de merge la pull request après directment depuis le code 