
# Feature #10604

## Objectives

  

In order to improve the quality of informations that is delivered to the client, we want a way to:

  

- Structure bug fixes / features details

- Allow a peer review of those details

- Automatically check the contents

- Generate and include the contents in the delivery notes

  

Doing so will require the following:

  

- Add a command line utility to pre-set the details from an issue number. This utility will be used by the developper to easily describe their doing, and will use a pre-defined parsable markdown structure [#10605](https://support.coopengo.com/issues/10605)

- Improve pre-commit checks to validate said structure [#10606](https://support.coopengo.com/issues/10606)

- Post-commit (hook or cron?) update the redmine issue description with the contents that were reviewed [#10607](https://support.coopengo.com/issues/10607  "Task: Update redmine descriptions according to contents of #10605 (A traiter)")

- Update integration scripts to properly parse and use the structure [#10608](https://support.coopengo.com/issues/10608  "Task: Update delivery slip generation for 10604 (A traiter)")

  
  

## Prerequisites

  

#### New libraries used:

python-redmine : used in coog redmine update (**step 1**) and when updating redmine (**step3**)
```bash
~$ pip3 install python-redmine
```
colored : used in drone check-meta (**step 2**)
```bash
~$ pip3 install colored --upgrade
```
PyGitHub : used in **step 3** in premerge-script.py
```bash
~$ pip3 install PyGithub 
```
#### Template engines
> Both used in **step 4** when generating html file

Mako 

```bash
~$ pip3 install Mako
```

mistune

```bash
~$ pip3 install mistune
```
  

## How to use

#### Step 1

In **coog** virtualenv, use:

```bash
(coog)~$ coog redmine update <issue_number>
```
This will call the script *coog-redmine* which calls *init_redmine_content.py*

It will open and create an editable .md file in **[COOG]/doc/issues**.

>**WARNING: Do not remove or modify tags**

Once your modifications are finished, you can save and close the editor.

----

#### Step 2

**check-meta.py** in coog-drone as been updated, it doesn't check the changelog anymore, but instead, it check depending on issue type if the required file is present in the pull request, moreover, it checks if the fields in the file are filled. (*check_content* function)

  ----

#### Step 3

Two solutions were implemented : 
1. premerge-script.py : 
	* Its purpose is to update directly the repository on **GitHub** 
	* The project is neither cloned nor pushed. The script just commit on the branch of the pull request after having updated RedMine
	```bash
	~$ python3 premerge-script.py
	```
2. upgrade-github, upgrade-github.py
	* launch upgrade-github it will clone the repository you want, run upgrade-github.py on it
	* upgrade-github.py will update redmine according to files present in the git repo, and delete theses files
	* then, upgrade-github will push changes on github 
		
	```bash
	~$ ./upgrade-github git@github.com:owner/repo.git
	```


  ----
#### Step 4

You just have to run bl_fr2.py *(can be converted into command line)* with the project name and version for which you want a review.
bl_fr.py has been updated on coog too, so you can use : 
```bash
(coog)~$ python bl_fr2.py <api_key> "<project_name>"  "<version>"
```

This will create a HTML file in doc/reviews which name is version-review.html

----