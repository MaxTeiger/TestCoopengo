#!/usr/bin/env python3
# vim: ft=python ts=4 sw=4 et
# coding: utf8
# pip install python-redmine
# pip install pygithub
# python path/to/premerge_script.py

import os
import re
import sys
from github import Github
from redminelib import Redmine
import base64

# Retrieve from the environment variables usefull infos
# after Drone as cloned the project

REPO = 'TestCoopengo' # OR RETRIEVE THE NAME OF THE GITHUB REPO (TestCoopengo for tests)
PR = 41 # OR RETRIEVE PULL REQUEST ID (39 or 40)
GH_TOKEN = os.environ['GITHUB_TOKEN']


RM_URL = 'https://support.coopengo.com/'
RM_TOKEN = os.environ['REDMINE_TOKEN']

DELETE_FILES_GITHUB = False

def update_redmine():
    print('Trying to connect to GitHub...')
    # or using an access token
    g = Github(GH_TOKEN)
    print('Connected ! \nRetrieving ' + REPO + '...', end='')
    repo = g.get_user().get_repo(REPO)
    print("\tOK !")

    print("Retrieving pull request #" + str(PR), end='')
    pr = repo.get_pull(int(PR))
    print("\tOK !")


    fileNames = []
    for file in pr.get_files():
        if 'doc/issues/' in file.filename and file.filename.endswith('.md'):
            fileNames.append(file.filename)


    # Updating Redmine
    print("\nTrying to connect to RedMine...", end='')
    redmine = Redmine(RM_URL, key=RM_TOKEN)
    print("\tOK !")

    # for each file
    for fileName in fileNames:
        tmpFileName = fileName.replace('doc/issues/', '')
        issueId = int(tmpFileName.replace('.md', ''))
        # read file content
        try:
            print("\nRetrieving the file...", end='')
            # Retrieve content of relative file
            encodedContent = repo.get_contents(fileName, ref=pr.head.ref).content
            content = base64.b64decode(encodedContent)
            content = content.decode('utf8')
            print("\t\tOK !")
        except:
            print("\t\tError : File doesn't exists (maybe already deleted ?)")
            continue
        
        # Update the corresponding issue on redmine with the content of the file
        try:        
            newTitle=content.split("\n")[0].replace('## ', '').replace('[title_en]','')
            newDescr=content.split("\n",2)[2]
            print("Update issue " + str(issueId) + "...", end='')
            redmine.issue.update(issueId, description=newDescr, subject=newTitle)
            print("\t\tOK !")
        except:
            print(
                "\t\tError : Issue doesn't exist or impossible to read the content of the file")
            continue

        if DELETE_FILES_GITHUB:
            # delete the file in github repo
            try:
                print("Delete file from Github...", end='')
                contentToDelete = repo.get_contents(fileName, ref=pr.head.ref)
                if pr.is_merged():
                    print(
                        "\nThis pull request is already merged, impossible to delete file...")
                else:
                    repo.delete_file(contentToDelete.path, "Remove " +
                                     fileName, contentToDelete.sha, pr.head.ref)
                    print("\tOK !")
            except:
                print("\tError : Impossible to delete file")
                continue

if __name__=='__main__':
    update_redmine()



# c'est même possible de merge la pull request après directment depuis le code
