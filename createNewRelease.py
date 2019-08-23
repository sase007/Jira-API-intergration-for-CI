#!/usr/bin/env python3

import os, sys, json, re
from pprint import pprint
from jira import JIRA
from jiraAPIWrapper import jiraAuthentication, openJson, getSummaryAndStoryNameFromBranchName

def assembleReleaseName(version, buildNumber):
    return "TestFlight_" + version + " (" + buildNumber + ")"

def getBuildNumberFromImportParameters():
    if "--buildNumber:" in sys.argv[1]:
        buildNumber = sys.argv[1].split(":")[1]
    else:
        print("Import parameter is not valid, exiting script.")
        sys.exit()

    return buildNumber

def getMarketingAppVersion():
    return os.popen('(cd ..; agvtool what-marketing-version -terse) | cut -d "=" -f 2').read().splitlines()[1]

def getComponentFromStory(jira, storyName):
    issue = jira.issue(storyName)
    return issue.raw["fields"]["components"]

def main():

    if "[skip jira]" in os.environ['CI_COMMIT_MESSAGE'].lower():
        print("Commit message contains exiting code.")
        sys.exit(0)

    if "devel" in os.environ['CI_COMMIT_REF_NAME']:
        print("Functionality for RC builds is not implemented.")
        sys.exit(0)

    jira = jiraAuthentication()
    marketingVersion = getMarketingAppVersion()
    buildNumber = getBuildNumberFromImportParameters()
    versionName = assembleReleaseName(marketingVersion, buildNumber)
    branchName, storyName = getSummaryAndStoryNameFromBranchName()
    component = getComponentFromStory(jira, storyName)
    originalStory = jira.issue(storyName)

    with open(openJson("version.json")) as f:
        versionDictionary = json.loads(f.read())

    with open(openJson("qaRequest.json")) as f:
        qaReqData = json.loads(f.read())

    for key, value in versionDictionary.items():
        versionDictionary["name"] = versionName
        versionDictionary["description"] = branchName

    for key, value in qaReqData.items():
        qaReqData["summary"] = branchName
        qaReqData["description"] = "Build: " + buildNumber
        qaReqData["components"] = component
        qaReqData['versions'].append({
            'name': versionName
        })
        qaReqData = json.dumps(qaReqData)

    jira.create_version(versionDictionary["name"], "MOBILE", versionDictionary["description"])
    originalStory.update({"fixVersions": [versionDictionary]})
    newQARequest = jira.create_issue(fields=qaReqData)
    jira.create_issue_link("Relates", originalStory, newQARequest)

if __name__ == '__main__':
    main()
