import json
import requests
import csv

import os

if not os.path.exists("data"):
 os.makedirs("data")


def write_files_to_csv(file_counts, output_file):
    """
    Writes filename and modification counts to CSV. Identifies the file with the highest modifications.
    - dictfiles: Dictionary {filename: modification count}.
    - file: Base name for the output CSV file.
    """
    fileOutput = 'data/file_' + file + '.csv'
    rows = ["Filename", "Touches"]
    fileCSV = open(fileOutput, 'w')
    writer = csv.writer(fileCSV)
    writer.writerow(rows)

    bigcount = None
    bigfilename = None
    for filename, count in dictfiles.items():
        rows = [filename, count]
        writer.writerow(rows)
        if bigcount is None or count > bigcount:
            bigcount = count
            bigfilename = filename
    fileCSV.close()
    print('The file ' + bigfilename + ' has been touched ' + str(bigcount) + ' times.')

# GitHub Authentication function
def github_auth(url, lsttoken, ct):
    """
    Authenticates and fetches data from GitHub API using token rotation.
    - url: GitHub API URL.
    - lsttoken: List of authentication tokens.
    - ct: Current token index, returns updated index and JSON data.
    """
    jsonData = None
    try:
        ct = ct % len(lstTokens)
        headers = {'Authorization': 'Bearer {}'.format(lsttoken[ct])}
        request = requests.get(url, headers=headers)
        jsonData = json.loads(request.content)
        ct += 1
    except Exception as e:
        pass
        print(e)
    return jsonData, ct

# @dictFiles, empty dictionary of files
# @lstTokens, GitHub authentication tokens
# @repo, GitHub repo
def countfiles(dictfiles, lsttokens, repo):
    """
    Counts modifications per file in a repo by iterating over all commits.
    - dictfiles: Empty dict for storing counts.
    - lsttokens: Tokens for GitHub API.
    - repo: Repository name 'username/repo'.
    """
    ipage = 1  # url page counter
    ct = 0  # token counter

    try:
        # loop though all the commit pages until the last returned empty page
        while True:
            spage = str(ipage)
            commitsUrl = 'https://api.github.com/repos/' + repo + '/commits?page=' + spage + '&per_page=100'
            jsonCommits, ct = github_auth(commitsUrl, lsttokens, ct)

            # break out of the while loop if there are no more commits in the pages
            if len(jsonCommits) == 0:
                break
            # Fetch and process each commit's details including affected files.
            for shaObject in jsonCommits:
                sha = shaObject['sha']
                # For each commit, use the GitHub commit API to extract the files touched by the commit
                shaUrl = 'https://api.github.com/repos/' + repo + '/commits/' + sha
                shaDetails, ct = github_auth(shaUrl, lsttokens, ct)
                filesjson = shaDetails['files']

                # Update modification count for each file listed in the commit.
                for filenameObj in filesjson:
                    filename = filenameObj['filename']
                    dictfiles[filename] = dictfiles.get(filename, 0) + 1
                    print(filename)
            ipage += 1
    except:
        print("Error receiving data")
        exit(0)
# GitHub repo
repo = 'scottyab/rootbeer'
# repo = 'Skyscanner/backpack' # This repo is commit heavy. It takes long to finish executing
# repo = 'k9mail/k-9' # This repo is commit heavy. It takes long to finish executing
# repo = 'mendhak/gpslogger'


# put your tokens here
# Remember to empty the list when going to commit to GitHub.
# Otherwise they will all be reverted and you will have to re-create them
# I would advise to create more than one token for repos with heavy commits

if __name__ == '__main__':
    lstTokens = ["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"]

    dictfiles = dict()
    countfiles(dictfiles, lstTokens, repo)
    print('Total number of files: ' + str(len(dictfiles)))

    file = repo.split('/')[1]
    file_output = f'data/file_{file}.csv'
    write_files_to_csv(dictfiles, file_output)
