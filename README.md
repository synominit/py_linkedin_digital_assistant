# Digital Assistant for LinkedIn
Automate the application process on LinkedIn
A Digital assistant that automatically applys to jobs for you

## Setup
Python 3.10 using a pipenv venv enviromnment

Run the following to setup the environment
```bash
python -m pip install -r requirements.txt
python -m pipenv install
```

Enter your phone number, inputs, dropdowns and search settings into the `config.yaml` file

```yaml
phone_number: # Enter your phone number

positions:
- # positions you want to search for
- # Another position you want to search for
- # A third position you want to search for

locations:
- # Location you want to search for
- # A second location you want to search in

# name of resume that has already been uploaded to linkedin
existing_resume: name-of-resume

# Technical skills to add along with a numeric number for years of experience, it will search the input field by contains
tech_skills:
  python: 3
  terraform: 2
  # put in as default number of years experience if not listed
  default: 2

# company names you want to ignore
blacklist_companies:
  - company name 1
  - company name 2

# job titles you want to ignore
blacklist_titles:
  - Oracle
  - Remote SAP


# Salary anount in numeric value
salary: 100000


# for radio and dropdown questions, these will be located dynamically as linkedin questions change up often, so use a word or short part of the question and then the answer (only alphabetical letters allowed)
# NOTE: default if not found will be YOLO and select the first option so be sure to do a bit of leg work and go through some of the applications manually to get a feel for the questions and answers
radio_and_dropdowns:
  bachelors: no
  high school: yes
  aws solutions architect associate: yes
  remote: yes # this is for remote work settings questions i.e. "Are you comfortable working in a remote work setting?"
  # work authorization
  require sponsorship: no
  authorized: yes
  # other random questions
  minimum 8 years experience: no
  local to texas: no
  license: yes
  english: native
  background check: yes

```

## Execute

Run the following to start the digital assistant
```
python -m pipenv run python main.py
```

Enter your username and password for LinkedIn in the terminal

Press Enter once you have confirmed you are fully logged in
