from flask import Flask, request, jsonify
import json
import pandas as pd
import numpy as np
import requests
import urllib

app = Flask(__name__)

@app.route('/', methods = ['GET'])
def test():
    while request:
        return("Test successful!!!")

@app.route('/extract_git', method = ['POST'])
def route():
    while request:
        data = request.get_json()
        source = data["source"]
        search_key = data["keyword"]

        search_key = search_key.replace(" ", "+")

        if(source == "github"):
            status = extract_github(search_key)
            if status == "Success":
                repo_df.to_csv("Repo_result1.csv", index = False)


def extract_github(search_key):
    git_search_url = "https://api.github.com/search/repositories?q={}".format(search_key)
    request_result = api_call(git_search_url, True)

    repo_df = pd.DataFrame(columns=["source", "search_keyword", "git_name", "owner_name", "git_url", "star_count", "forks_count", "contributor_count",
"contributors_list", "code_language", "last_updated_date", "readme_url", "readme_text"])
    
    total_repo = request_result["total_count"]
    print(total_repo)
    item_list = request_result["items"]
    no_of_item_list = len(item_list)


    for item in range(0, no_of_item_list):
        try:
            #Extract git name
            git_name = item_list[item]["full_name"]
            print(git_name)

            #Extract owner name
            owner_name = item_list[item]["owner"]["login"]
            print(owner_name)

            #Extract git URL
            git_url = item_list[item]["url"]
            print(git_url)

            #Extract no of stars
            star_count = item_list[item]["stargazers_count"]
            print(star_count)

            #Extract no of forks
            forks_count = item_list[item]["forks_count"]
            print(forks_count)

            contributor_link = item_list[item]["contributors_url"]
            request_result_contributor = api_call(contributor_link, False)
            

            #Extract total no of contributors
            contributor_count = len(request_result_contributor)
            counter_contributor = 0
            contributors_list = []
            

            print(contributor_count)
            #Extract Top 30 contributors List
            while (counter_contributor<len(request_result_contributor)):
                contributors_list.append(request_result_contributor[counter_contributor]["url"])
                counter_contributor +=1

            print(contributors_list)

            #Extract main coding languages used
            code_language = item_list[item]["language"]
            print(code_language)

            #Extract last activity date
            last_updated_date = item_list[item]["updated_at"]
            print(last_updated_date)

            #Extract Readme data from Readme.md file
            content_url = item_list[item]["contents_url"].replace("{+path}", "")
            content_response = api_call(content_url, False)
            readme_url = next(x for x in content_response if x["name"] == "README.md")

            #Readme URL
            readme_url = readme_url["download_url"]
            readme_data = urllib.request.urlopen(readme_url)
            text = []
            for line in readme_data:
                line = line.decode('utf-8')
                text.append(line)

            #Readme text
            readme_text = text

            #Adding rows to dataframe
            row = ["Github", search_key, git_name, owner_name, git_url, star_count, forks_count, contributor_count,
                contributors_list, code_language, last_updated_date, readme_url, readme_text]
            print("Item #", item, " done!!")
            repo_df.loc[item] = row
        except:
            print("Exceptions")
        return("Success")    



def api_call(url, auth_req):
    token = "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"
    headers = {'Authorization': 'token ' + token}
    if(auth_req == True):
        url = url + "&per_page=50"
        login = requests.get(url, headers=headers)
        request_result = login.json()
        return request_result
    else:
        url = url + "?per_page=30"
        login = requests.get(url)
        request_result = login.json()
        return request_result



if __name__ == "__main__":
    app.run(debug = True, port = 9090)