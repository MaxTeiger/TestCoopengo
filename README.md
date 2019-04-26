# RedMine syncronization with GitHub 

## Setup

### On GitHub

* Go to your **GitHub** repository
* Go to settings > Webhooks section
* Create new webhook
* Add the address of the server on which the application will run
* Add a **secret key** for the security of the application (upper case, lower case, numbers...). Please note this key we will use it later
* Choose the activation mode on "Pull request".
* Save the webhook

### In config.py file

* Change SECRET_TOKEN to your **secret key**
* Change REDMINE_API_KEY to your **redmine api key**
* Change REDMINE_URL to your **RedMine URL desposit**

### On your server
You just have to run :

```bash
$ docker-compose up
```
or 
```bash
$ docker-compose up -d
```

For the moment, it performs the same action regardless of the action performed on a pull request (whether it is opened, merged, re-opened, or edited).
Maybe a next version that will change the RedMine status to :

| GitHub                        | RedMine                     |
|-------------------------------|-----------------------------|
| New Pull Request              | En revue                    |
| Pull request closed           | A traiter                   |
| Merge pull request            | Traité                      |
