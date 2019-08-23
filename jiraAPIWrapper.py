#!/usr/bin/env python3

import os
import sys
from pathlib import Path
from jira import JIRA

def jiraAuthentication():
    options = {
      'server': 'https://jira.kiwi.com',
    }
    jiraInstance = JIRA(options, basic_auth=('mobilebot', os.environ['mobilebotPassword']))

    return jiraInstance

def printUsersInProgressIssues(jiraInstance):
    jql = ('project=MOBILE AND (assignee="{0}" AND issuetype=story AND status="In Progress") OR (assignee="{0}" AND status=New)'.format(os.environ['GITLAB_USER_EMAIL']))
    issues_in_proj = jiraInstance.search_issues(jql, maxResults=15)

    for issue in issues_in_proj:
        print(issue.key + " " + issue.fields.summary)
        if issue.fields.summary == "New issue from jira-python":
            issue.delete()

def openJson(fileName):
    if ".json" not in fileName:
        fileName = fileName + ".json"

    file_path = str(Path(Path(os.getcwd()).parent).parent) + "/scripts/jira/jsons/" + fileName

    return file_path

def getSummaryAndStoryNameFromBranchName():
    branchName = os.environ['CI_COMMIT_REF_NAME']

    if "feature/" in branchName:
        branchName = branchName.replace("feature/", "")

    if "bugfix/" in branchName:
        branchName = branchName.replace("bugfix/", "")

    if "sub-task/" in branchName:
        branchName = branchName.replace("sub-task/", "")

    if "MOBILE" in branchName:
        storyName = branchName[0:11]
        branchName = branchName.replace("MOBILE", "")
        branchName = branchName[6:len(branchName)]
    else:
        print("Not a Jira branch.")
        sys.exit(0)

    if "-" in branchName:
        branchName = branchName.replace("-", " ")

    return branchName.capitalize(), storyName
