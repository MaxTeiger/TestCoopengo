#!/usr/bin/env python3
# coding: utf8

import os
import sys
from redminelib import Redmine
import shutil


# Scenario : 
# On part du principe que le repo est cloné
# et contient les fichiers <issue_number>.md 
# dans le dossier doc/issues/
# que l'on souhiate supprimer. Ce script va simplement
# mettre à jour RedMine avec ces fichiers, puis
# les supprimer, (les actions de clone, add, commit et 
# push seront probablement réalisées depuis un script shell)
# celui ci pourrait envoyer en parametre le chemin du dossier cloné ?

cloneAbsolutePath = '/home/max/Bureau/TestCoopengo' #sys.argv[1]
fileFolderPath = cloneAbsolutePath +"/doc/issues/"  
RM_URL = 'https://support.coopengo.com/'
RM_TOKEN = os.environ['REDMINE_TOKEN']


def main():

    # Updating Redmine 
    print("\nTrying to connect to RedMine...", end='')
    redmine = Redmine(RM_URL, key=RM_TOKEN)
    print("\tOK !\n")

    for filename in os.listdir(fileFolderPath):
        if filename.endswith('.md'):
            filePath = fileFolderPath +filename
            issueId = filename.split(".",1)[0]
            print("---------------(" +issueId +")--------------")
            try: 
                print("Reading file...", end='')
                file = open(filePath, "r")
                fileContent = file.read()
                print("\t\t\tOK !")
            except:
                print('\t\tError : Impossible to read the file')
                


            try:
                print("Updating Redmine...", end='')
                redmine.issue.update(issueId, description=fileContent)
                print("\t\tOK !")
            except:
                print("\t\tError : Issue doesn't exist or file hasn't been read")
                

            try:
                print("Removing file...", end='')    
                os.remove(filePath)
                print("\t\tOK !")
            except:
                print("\t\t")

        else:
            continue

    if not os.listdir(fileFolderPath):
        print("\nFolder empty, delete...", end='')
        os.rmdir(fileFolderPath)
        print("\t\tOK !")
    else: 
        print("\nFolder not empty, not deleting it")


if __name__ == '__main__':
    main()
