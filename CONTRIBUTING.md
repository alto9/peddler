# Code Contribution Guidelines

## Welcome to Peddler! These instructions will help you with the steps to be able to make contributions.

### If you've found a bug
Submit a GitHub issue with our issue template. Please make sure to do your due diligence and verify your config settings before creating an issue. When you create an issue, please make sure to include all relevant config, but not any secure information like database passwords. 

### If you want to fix the bug or make an enhancement
Great! Follow the steps below to get your workstation setup. These steps are verified on Mac OSX but are very similar to other platforms.

#### Prerequisites
- Python 3.8
- Docker Desktop 20.10.7

#### 1. Clone peddler
`> git clone https://github.com/alto9/peddler.git && cd peddler`

#### 2. Check out a new branch from master
`> git checkout -b <yourname>/<issuenumber>`

#### 3. Setup a virtualenv for Python
`> cd peddler && python3 -m venv v38`

#### 4. Activate the virtual environment
`> source v38/bin/activate`

#### 5. Install dependencies
`> make bootstrap-dev`

#### 6. Install Peddler locally in the venv, so that you can update and test in real time
`> pip3 install --editable .`

#### 7. When you are done working, exit your virtual env
`> deactivate`

#### 8. Finally, [create a pull request](https://help.github.com/articles/creating-a-pull-request). We'll then review and merge it.
