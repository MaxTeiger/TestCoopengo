# Feature #10604
## Objectives

In order to improve the quality of informations that is delivered to the client, we want a way to:

-   Structure bug fixes / features details
-   Allow a peer review of those details
-   Automatically check the contents
-   Generate and include the contents in the delivery notes

Doing so will require the following:

-   Add a command line utility to pre-set the details from an issue number. This utility will be used by the developper to easily describe their doing, and will use a pre-defined parsable markdown structure [#10605](https://support.coopengo.com/issues/10605) 
-   Improve pre-commit checks to validate said structure [#10606](https://support.coopengo.com/issues/10606)
-   Post-commit (hook or cron?) update the redmine issue description with the contents that were reviewed [#10607](https://support.coopengo.com/issues/10607 "Task: Update redmine descriptions according to contents of #10605 (A traiter)")
-   Update integration scripts to properly parse and use the structure [#10608](https://support.coopengo.com/issues/10608 "Task: Update delivery slip generation for 10604 (A traiter)")


## Prerequisites

#### New libraries used: 
python-redmine
```bash
$pip install python-redmine
```
Mako
```bash
$pip install Mako
```
or
```bash
$pip3 install Mako
```

mistune
```bash
$pip install mistune
```

Define REDMINE_TOKEN as an environment variable:
```bash
$export REDMINE_TOKEN=<your_token>
```

## How to use
#### Step 1
In **coog** virtualenv, use: 
```bash
$coog redmine update <issue_number>
```
this will open and create an editable .md file in **[COOG]/doc/issues**. 
>**WARNING: Do not remove tags** 

Once your modifications are finished, you can save and close the editor.

#### Step 2
Must update drone to test files from issues: 
* If files exists (check project in Redmine, list tickets, observe if .md files are in the project)
* If files contains the required tags (check if fields are not empty)
* Check if the en tags match the fr ones

#### Step 3

For the moment, only prepare-commit-message in **.git/hooks** is implemented. This hook is triggered before a merge request is done, but it stays local. 
The hook updates redmine tickets with the contents of files in **doc/issues**, and then delete the files because we don't need them after the merge. 


#### Step 4
You just have to run bl_fr2.py *(can be converted into command line)* with the project name and version for which you want a review.
```bash
$python bl_fr2.py <api_key> "<project_name>" "<version>"
```
This will create a HTML file in doc/reviews which name is version-review.html
