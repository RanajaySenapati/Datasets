import requests
import pandas as pd
import numpy as np
import json
import csv
import re
import openai
from csv import DictWriter
from bs4 import BeautifulSoup

def remove_empty_string(str_list):
    """
    Remove all empty strings (' ') from the given str_list.

    Parameters
    ----------
    str_list : List
        A list with strings.

    Returns
    -------
    str_list : List
        A list of strings without empty strings.

    """
    str_list = list(filter(None, str_list))
    return str_list


def WriteToDestination(file_name, information, column_names):
    """
    Add a new row to an existing csv file.

    Parameters
    ----------
    file_name : String
        The name and path of the file we want to write into.
    information : Dictionary
        A dict storing the information we want to write.
    column_names : List
        A list of keys corresponds to elements in information.

    Returns
    -------
    None.

    """
    with open(file_name, 'a+', newline='') as write_object:
        dictwriter_object = DictWriter(write_object, fieldnames=column_names)
        dictwriter_object.writerow(information)
        write_object.close()
    return


def GetTopicFromChatGPT(description):
    """
    Pass a package description to ChatGPT and let it select the most relevant topic

    Parameters
    ----------
    description : String
        A string containing the extracted description from given github link.

    Returns
    -------
    A string containing the most relevant topic ChatGPT returned.

    """
    model_engine = "text-davinci-003"
    prompt = "Read the description below and choose one topic from (model explanability, \
        model monitoring, fairness, synthetic data, conterfactual fairness, \
            causal explainability, sequency synthetic data, and generation)\
        that is most relevant to this description: " + description

    # Generate a response
    completion = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5,
    )

    response = completion.choices[0].text
    print("ChatGPT chosed the following topic: " + response.replace('\n', '') + '\n')
    return response.replace('\n', '')


def GetUrlFromChatGPT(topic):
    """
    Pass a specific AI topic to ChatGPT and let it return the most relevant urls on GitHub.

    Parameters
    ----------
    topic : String
        A String indicating the topic we want to search for.

    Returns
    -------
    A list of urls regarding the given topic.

    """
    with open("BrowsedGithubLinks.txt", "r") as f:
        link_list = f.readlines()
    
    model_engine = "text-davinci-003"
    prompt = "Can you browse on Github and give me 100 open source links about " + topic +\
        " other than those in this list: " + str(link_list)

    # Generate a response
    completion = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5,
    )

    response = completion.choices[0].text
    
    urls = []
    for i in re.split('\n| ', response):
        if 'https' in i:
            if i[0] == '(':
                i = i[1:]
            if i[-1] == ')':
                i = i[:-1]
            urls.append(i)
            
    with open("BrowsedGithubLinks.txt", "a") as f:
        f.writelines(response.replace('\n', ''))
    print("ChatGPT chosed the following urls: " + response + '\n')
    return urls

def ExtractFiles(soup, git_information):
    """
    Extract a list of files from given soup object, append the list of files into the 
    given git_information dictionary.

    Parameters
    ----------
    soup : BeautifulSoup
        A BeautifulSoup object containing information from url(github).
    git_information : Dictionary
        A destination dict to store wanted information.

    Returns
    -------
    None.

    """
    file_list = []
    file_names = soup.find_all('a', {'class': 'js-navigation-open Link--primary'})
    for file_name in file_names:
        file_list.append(file_name.text)
        git_information['files'] = file_list
    return


def ExtractDescription(soup):
    """
    Extract a the description from given soup object and return it as string.

    Parameters
    ----------
    soup : BeautifulSoup
        A BeautifulSoup object containing information from url(github).

    Returns
    -------
    A string containing the extracted description from readme file context.

    """
    description_text = ""
    descriptions = soup.find_all('p', {'dir': 'auto'})
    for description in descriptions:
        description_text += description.text
    return description_text


def ExtractNumContributors(soup, git_information):
    """
    Extract the number of contributors (if any) from given soup object, append the 
    list of files into the given git_information dictionary.

    Parameters
    ----------
    soup : BeautifulSoup
        A BeautifulSoup object containing information from url(github).
    git_information : Dictionary
        A destination dict to store wanted information.

    Returns
    -------
    None.

    """
    contributors = soup.find_all('h2', {'class': 'h4 mb-3'})
    contributor_num = re.split('\n| ', contributors[-2].text)
    if remove_empty_string(contributor_num)[0] == 'Contributors':
        git_information['#Contributors'] = remove_empty_string(contributor_num)[1]
    else:
        git_information['#Contributors'] = 'N/A'
    return
    

def ExtractNumUsers(soup, git_information):
    """
    Extract the number of users (if any) from given soup object, append the 
    list of files into the given git_information dictionary.

    Parameters
    ----------
    soup : BeautifulSoup
        A BeautifulSoup object containing information from url(github).
    git_information : Dictionary
        A destination dict to store wanted information.

    Returns
    -------
    None.

    """
    users = soup.find_all('h2', {'class': 'h4 mb-3'})
    user_num = re.split('\n| ', users[-3].text)
    if remove_empty_string(user_num)[0] == 'Used':
        git_information['#Users'] = remove_empty_string(user_num)[2]
    else:
        git_information['#Users'] = 'N/A'
    return


def ExtractMainLanguages(soup, git_information):
    """
    Extract the main programming language from given soup object, append the 
    list of files into the given git_information dictionary.

    Parameters
    ----------
    soup : BeautifulSoup
        A BeautifulSoup object containing information from url(github).
    git_information : Dictionary
        A destination dict to store wanted information.

    Returns
    -------
    None.

    """
    #Extract Main Language
    languages = soup.find_all('a', {'class': 'd-inline-flex flex-items-center flex-nowrap Link--secondary no-underline text-small mr-3'})
    git_information['Code Language'] = remove_empty_string(languages[0].text.split('\n'))[0]
    return


def ExtractNumForks(soup, git_information):
    """
    Extract number of forks (if any) from given soup object, append the list of 
    files into the given git_information dictionary.

    Parameters
    ----------
    soup : BeautifulSoup
        A BeautifulSoup object containing information from url(github).
    git_information : Dictionary
        A destination dict to store wanted information.

    Returns
    -------
    None.

    """
    #Extract Forks
    forks = soup.find_all('div', {'class': 'd-flex'})
    fork_exist = False
    for fork in forks:
        temp = remove_empty_string(re.split('\n| ', fork.text))
        if 'Fork' in temp:
            git_information['#Forks'] = temp[temp.index('Fork') + 1]
            fork_exist = True
    if not fork_exist:
        git_information['#Forks'] = 'N/A'
    return


def ExtractNumStars(soup, git_information):
    """
    Extract number of stars (if any) from given soup object, append the list of 
    files into the given git_information dictionary.

    Parameters
    ----------
    soup : BeautifulSoup
        A BeautifulSoup object containing information from url(github).
    git_information : Dictionary
        A destination dict to store wanted information.

    Returns
    -------
    None.

    """
    #Extract Forks
    stars = soup.find_all('li')
    star_exist = False
    for star in stars:
        temp = remove_empty_string(re.split('\n| ', star.text))
        if 'Star' in temp:
            git_information['#Stars'] = temp[temp.index('Star') + 1]
            star_exist = True
    if not star_exist:
        git_information['#Stars'] = 'N/A'
    return
        

def ExtractListContributors(soup, git_information):
    """
    Extract the list of contributors (if any) from given soup object, append the 
    list of files into the given git_information dictionary.

    Parameters
    ----------
    soup : BeautifulSoup
        A BeautifulSoup object containing information from url(github).
    git_information : Dictionary
        A destination dict to store wanted information.

    Returns
    -------
    None.

    """
    #contributors = soup.find_all('h2', {'class': 'h4 mb-3'})
    contributor_links = soup.find_all('a', {'class': 'Link--primary no-underline'}, href=True)
    contributor_list_url = ''
    for link in contributor_links:
        if 'contributors' in link['href']:
            contributor_list_url = 'https://github.com/' + link['href']
            break
    if contributor_list_url == '':
        git_information['Contributor List'] = 'N/A'
        return
    
    contributor_list_data = requests.get(contributor_list_url)
    contributor_list_soup = BeautifulSoup(contributor_list_data.text, 'html.parser')
    contributor_names = contributor_list_soup.find_all('a')#, {'class': 'd-inline-block mr-2 float-left'})
    for name in contributor_names:
        pass
        #print(name)
        #Could not access the user's name
    return


def ExtractActivities(soup, git_information):
    """
    Extract the number of recent activities (if any) from given soup object, append the 
    list of files into the given git_information dictionary.

    Parameters
    ----------
    soup : BeautifulSoup
        A BeautifulSoup object containing information from url(github).
    git_information : Dictionary
        A destination dict to store wanted information.

    Returns
    -------
    None.

    """
    activity_links = soup.find_all('a', {'class': 'UnderlineNav-item no-wrap js-responsive-underlinenav-item js-selected-navigation-item'}, href=True)
    activity_url = ''
    for link in activity_links:
        if 'pulse' in link['href']:
            activity_url = 'https://github.com/' + link['href']
            break
    if activity_url == '':
        git_information['Activities in 1mth'] = 'N/A'
        return
    
    activity_data = requests.get(activity_url)
    activity_soup = BeautifulSoup(activity_data.text, 'html.parser')
    activities = activity_soup.find_all('div', {'class': 'mt-2'})
    total_num_activities = 0
    for activity in activities[:-1]:
        total_num_activities += int(remove_empty_string(re.split('\n| ', activity.text))[0])
    git_information['Activities in 1mth'] = total_num_activities
    return


def ExtractDependency(soup, git_information):
    """
    Extract the dependencies' links (if any) from given soup object, append the 
    list of files into the given git_information dictionary.

    Parameters
    ----------
    soup : BeautifulSoup
        A BeautifulSoup object containing information from url(github).
    git_information : Dictionary
        A destination dict to store wanted information.

    Returns
    -------
    None.

    """
    dependency_url = url + '/network/dependencies'
    dependency_data = requests.get(dependency_url)
    dependency_soup = BeautifulSoup(dependency_data.text, 'html.parser')
    dependencies = dependency_soup.find_all('a', {'class': 'Link--primary text-bold'})
    dependency_list = []
    for dependency in dependencies:
        dependency_list.append('https://github.com/' + dependency['href'])
    git_information['Dependencies'] = dependency_list
    return


def ExtractBasedOnURL(url, git_information_list):
    """
    Extract all information based on given url, perform smart search to determine which AI topic
    this url belongs to.

    Parameters
    ----------
    url : String
        A String containing the website address of the github page we want to search on.
    git_information : Dictionary
        A destination dict to store wanted information.

    Returns
    -------
    None.

    """
    git_information = {}
    RawData = requests.get(url)
    soup = BeautifulSoup(RawData.text, 'html.parser')

    description = ExtractDescription(soup)
    git_information['Topic'] = GetTopicFromChatGPT(description)
    git_information['GitName'] = url.split('/')[-1]
    git_information['GitLink'] = url
    
    #ExtractFiles(soup, git_information)
    ExtractNumContributors(soup, git_information)
    ExtractNumUsers(soup, git_information)
    ExtractMainLanguages(soup, git_information)
    ExtractNumForks(soup, git_information)
    ExtractNumStars(soup, git_information)
    #ExtractListContributors(soup, git_information)
    ExtractActivities(soup, git_information)
    ExtractDependency(soup, git_information)
    
    git_information_list.append(git_information)
    
    return


def ExtractBasedOnTopic(topic, git_information_list):
    """
    Extract all information based on given topic, perform smart search to determine which GitHub
    url is relevant to the topic.

    Parameters
    ----------
    topic : String
        A String containing a specific GitHub topic we want to search for.
    git_information : Dictionary
        A destination dict to store wanted information.

    Returns
    -------
    None.

    """
    urls = GetUrlFromChatGPT(topic)
    for url in urls:
        try:
            RawData = requests.get(url)
            soup = BeautifulSoup(RawData.text, 'html.parser')
            
            git_information = {}
            git_information['Topic'] = topic
            git_information['GitName'] = url.split('/')[-1]
            git_information['GitLink'] = url
            
            #ExtractFiles(soup, git_information)
            ExtractNumContributors(soup, git_information)
            ExtractNumUsers(soup, git_information)
            ExtractMainLanguages(soup, git_information)
            ExtractNumForks(soup, git_information)
            ExtractNumStars(soup, git_information)
            #ExtractListContributors(soup, git_information)
            ExtractActivities(soup, git_information)
            ExtractDependency(soup, git_information)
            
            git_information_list.append(git_information)
            
        except Exception as e:
            print("Invalid url: " + url + ", skipping... error message: ", e)
    
    return
        
    
    

#--------------------------------------Main------------------------------------
if __name__ == "__main__":
    
    git_information_list = []
    openai.api_key = "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"
    #url = "https://github.com/SeldonIO/alibi"
    url = "https://github.com/TeamHG-Memex/eli5"
    destination_file_name = 'GithubScrapper.csv'
    
    ExtractBasedOnTopic("Model Explanability", git_information_list)  
    #ExtractBasedOnURL(url, git_information_list)
    
    for git_information in git_information_list:
        WriteToDestination(destination_file_name, git_information, list(git_information.keys()))
        print("information wrote: \n", git_information, '\n')
    
    
    
    