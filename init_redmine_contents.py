#!/usr/bin/env python3
import requests
import os
import sys

REDMINE_URL = 'https://support.coopengo.com'
REDMINE_TOKEN = os.environ['REDMINE_TOKEN']
TRACKERS = {
    'Feature': 'feature',
    'Bug': 'bug',
    }


def parse_description(issueTitle, issueDescr, trackerName, issue_number, isAlreadyHere):


    # Here, we find the right path to store issues.md files
    thisfolder = os.path.dirname(os.path.abspath(__file__))
    sep = "/coog/"
    goodFolder = thisfolder.split(sep, 1)[0] +"/coog/doc/issues/"
    pathToFile = goodFolder +issue_number +".md"
    print("Path to file :\t " +pathToFile)


    # We open the file with the right name
    file = open(pathToFile,"w") 
    print("File opened !")

    if isAlreadyHere == 0:
        # If the issue is related to a Bug, we create the appropriate template 
        if trackerName == 'Bug':
        
            file.write("## [title_en] " +issueTitle +" (required)\n")
            file.write("## [title_fr] " +issueTitle +" (required)\n\n")

            file.write("### [repro_fr] (required)\n\n")
            file.write("<Scenario de reprodution français>\n\n")

            file.write("### [correction_fr] (required)\n\n")
            file.write("<Explication de la correction en français>\n\n")

            file.write("### [parametrage_fr]\n\n")
            file.write("<Paramétrage (éventuel) à faire>\n\n")

            file.write("### [scripts_fr]\n\n")
            file.write("<Scripts à passer>\n\n")

            file.write("## [business_modules] (required)\n\n")
            file.write("* module_1\n")
            file.write("* module_2\n\n")

            file.write("## [original_description] (required / automatic)\n")
            file.write(issueDescr +"\n")

            file.close() 

        # If the issue is related to a Feature, we create the appropriate template 
        elif trackerName == 'Feature':


            file.write("## [title_en] " +issueTitle +" (required)\n")
            file.write("## [title_fr] " +issueTitle +" (required)\n\n")

            file.write("### [parametrage_fr]\n")
            file.write("<Paramétrage (éventuel) à faire>\n\n")

            file.write("### [scripts_fr]\n")
            file.write("<Scripts à passer>\n\n")

            file.write("## [business_modules] (required)\n\n")

            file.write("* module_1\n")
            file.write("* module_2\n\n")

            file.write("## [original_description] (required / automatic)\n")
            file.write(issueDescr +"\n")

            file.close()

        # If the tracker of the error is neither a bug or a feature 
        else:
            raise NotImplementedError


        print("Written in file !")

    elif isAlreadyHere == 1:
        print("Updating the file from redmine...")
        file.write(issueDescr)



# retrieve the issue number (user input)
# maybe we need to check that this input is a number before we continue?
issue_number = sys.argv[1]

# Request on the redmine page to retrieve json about the issue 
data = requests.get(
    REDMINE_URL + '/issues/%s.json' % issue_number,
    auth=(REDMINE_TOKEN, ''))

# If the website return a json object when an error occurs, it raise the status 
# of the response (maybe check if the status != 200 ?)
data.raise_for_status()

# parse data in order to use them
parsed = data.json()['issue']

trackerName = parsed['tracker']['name']
issueTitle  = parsed['subject']
issueDescr  = parsed['description']

# Print retrieved informations
print("Tacker      :\t " +parsed['tracker']['name'])
print("Title       :\t " +parsed['subject'])
print("Description :\t " +parsed['description'])


if "## [title_en]" in parsed['description']:
    print("ticket has been formated once...")
    parse_description(issueTitle, issueDescr, trackerName, issue_number, isAlreadyHere=1)

elif "## [title_en]" not in parsed['description']:
    print("ticket never been formated\n\n")
    parse_description(issueTitle, issueDescr, trackerName, issue_number, isAlreadyHere=0)























# #!/usr/bin/env python3
# import requests
# import os
# import sys

# REDMINE_URL = 'https://support.coopengo.com'
# REDMINE_TOKEN = os.environ['REDMINE_TOKEN']
# TRACKERS = {
#     'Feature': 'feature',
#     'Bug': 'bug',
#     }


# def parse_description(description, tracker):

#     # # Dictionnary used to define the template for a bug fix
#     #           #----------------------- BUG TEMPLATE --------------------------------#
#     #               ## [title_en] Titre en anglais (required)

#     #               ## [title_fr] Titre en français (required)

#     #               ### [repro_fr] (required)

#     #               <Scenario de reprodution français>

#     #               ### [correction_fr] (required)

#     #               <Explication de la correction en français>

#     #               ### [parametrage_fr]

#     #               <Paramétrage (éventuel) à faire>

#     #               ### [scripts_fr]

#     #               <Scripts à passer>

#     #               ## [business_modules] (required)

#     #               * module_1
#     #               * module_2

#     #               ## [original_description] (required / automatic)

#     #               <Description existant dans redmine>

#     if tracker == 'Bug':
#         return {
#             'english': {
#                 'title': '',
#                 'scenario': '',
#                 'fix': '',
#                 'conf': '',
#                 'script': '',
#                 },
#             'french': {
#                 'title': '',
#                 'scenario': '',
#                 'fix': '',
#                 'conf': '',
#                 'script': '',
#                 },
#             'original_description': '',
#             'business_modules': [],
#             }

    
#     # Dictionnary used to define the template for a feature fix
#     # --------------------------- FEATURE TEMPLATE ---------------------------------- #
#                         # # ## [title_en] Titre en anglais (required)

#                         # ## [title_fr] Titre en français (required)

#                         # ### [parametrage_fr]

#                         # <Paramétrage (éventuel) à faire>

#                         # ### [scripts_fr]

#                         # <Scripts à passer>

#                         # ## [business_modules] (required)

#                         # * module_1
#                         # * module_2

#                         # ## [original_description] (required / automatic)

#                         # <Description existant dans redmine>


#     elif tracker == 'Feature':
#         return {
#             'english': {
#                 'title': '',
#                 'conf': '',
#                 'script': '',
#                 },
#             'french': {
#                 'title': '',
#                 'conf': '',
#                 'script': '',
#                 },
#             'original_description': '',
#             'business_modules': [],
#             }
    
#     # If the tracker of the error is not a bug or a feature 
#     else:
#         raise NotImplementedError


# # retrieve the issue number (user input)
# # maybe we need to check that this input is a number before we continue?
# issue_number = sys.argv[1]

# # Request on the redmine page to retrieve json about the issue 
# data = requests.get(
#     REDMINE_URL + '/issues/%s.json' % issue_number,
#     auth=(REDMINE_TOKEN, ''))

# # If the website return a json object when an error occurs, it raise the status 
# # of the response (maybe check if the status != 200 ?)
# data.raise_for_status()

# # parse data in order to use them
# parsed = data.json()['issue']

# trackerName = parsed['tracker']['name']
# issueTitle  = parsed['subject']
# issueDescr  = parsed['description']


# # Print retrieved informations
# print("Tacker :\t " +parsed['tracker']['name'])
# print("Title  :\t " +parsed['subject'])
# print("Description :\t " +parsed['description'])


