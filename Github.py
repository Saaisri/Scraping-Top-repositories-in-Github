from multiprocessing import reduction
from re import U
from tkinter import PAGES
import requests
import os
import pandas as pd

from bs4 import BeautifulSoup

base_url =  'https://github.com'
topics_url = 'https://github.com/topics'

response = requests.get(topics_url)

page_contents = response.text

doc = BeautifulSoup(page_contents,'html.parser')
    

def parse_star_count(stars_str):
    stars_str = stars_str.strip()
    if stars_str[-1] == 'k':
        return int(float(stars_str[:-1])*1000)
    return int(stars_str)

def get_topic_page(topic_url):
    #Download the page

    response = requests.get(topic_url)

    #Check successful response
    if response.status_code!=200:
        raise Exception("Failed to load page {}".format(topic_url))
    
    #Parse using bs4
    topic_doc = BeautifulSoup(response.text,'html.parser')

    return topic_doc

def get_repo_info(h1_tag, star_tag):
    #returns all the required information about repo
    a_tags = h1_tag.find_all('a')
    username = a_tags[0].text.strip()
    repo_name = a_tags[1].text.strip()
    repo_url = base_url + a_tags[1]['href']
    stars = parse_star_count(star_tag.text.strip())
    return username, repo_name, stars, repo_url



# get_repo_info(repo_tags[0],star_tags[0])

def get_topic_repos(topic_doc):


    #get the h3 tags containing repo title , repo URL and username
    h1_selection_class = 'f3 color-fg-muted text-normal lh-condensed'

    repo_tags = topic_doc.find_all('h3',{'class':h1_selection_class})

    #Get star tags
    star_tags = topic_doc.find_all('span', {'class': 'Counter js-social-count'})

    topic_repos_dict = {
    'username':[],
    'repo_name':[],
    'stars':[],
    'repo_url':[]
    }
    #get repo info
    for i in range(len(repo_tags)):
        repo_info = get_repo_info(repo_tags[i],star_tags[i])
        topic_repos_dict['username'].append(repo_info[0])
        topic_repos_dict['repo_name'].append(repo_info[1])
        topic_repos_dict['stars'].append(repo_info[2])
        topic_repos_dict['repo_url'].append(repo_info[3])

    return pd.DataFrame(topic_repos_dict)

def scrape_topic(topic_url, path):
    # fname = topic_name + '.csv'
    if os.path.exists(path):
        print("The file {} already exists. Skipping...".format(path))
        return
    topic_df = get_topic_repos(get_topic_page(topic_url))
    topic_df.to_csv(path, index=None)

def get_topic_titles(doc):
    selection_class = "f3 lh-condensed mb-0 mt-1 Link--primary"
    title_tags = doc.find_all('p',{'class': selection_class})
    topic_titles = []
    for tag in title_tags:
        topic_titles.append(tag.text)

    return topic_titles

def get_topic_desc(doc):
    topic_desc = doc.find_all('p',{'class':'f5 color-fg-muted mb-0 mt-1'})
    topic_description = []
    for tag in topic_desc:
        topic_description.append(tag.text.strip())

    return topic_description

def get_topic_urls(doc):
    topic_links_tags = doc.find_all('a',{'class':'no-underline flex-grow-0'})
    topic_urls = []
    base_url =  'https://github.com'

    for tag in topic_links_tags:
        topic_urls.append(base_url + tag['href'])

    return topic_urls



def scrape_topics():
    topics_url = 'https://github.com/topics'
    response = requests.get(topics_url)

    if response.status_code!=200:
        raise Exception("Failed to load page {}".format(topics_url))

    topics_dict ={
        'title': get_topic_titles(doc),
        'description':get_topic_desc(doc),
        'url': get_topic_urls(doc)
    }

    return pd.DataFrame(topics_dict)

# print(scrape_topics())

def scrape_topics_repo():
    print("Scraping List of Topics")
    topics_df = scrape_topics()

    #Create a folder

    os.makedirs('data',exist_ok=True)

    for index,row in topics_df.iterrows():
        # print(row['title'], row['url'])
        print('Scraping top repositories of "{}"'.format(row['title']))
        scrape_topic(row['url'], 'data/'+ row['title']+'.csv')
 
print(scrape_topics_repo())