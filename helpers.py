from collections import Counter
import sys
import csv
from google import google
from concurrent.futures import ThreadPoolExecutor
import csv
import json
from multiprocessing import Pool
from sortedcontainers import SortedSet
import difflib 
from urllib.request import urlopen
from  urllib.parse import quote_plus
import json
import re
from threading import Thread
import matplotlib.pyplot as plt
import numpy as np
import os
import time
from google import google
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
import requests
from tornado_fetcher import Fetcher
from bs4 import BeautifulSoup
import re

pattern = re.compile("[\w]+")
columns=['google_categories','partner_categories']
cities = ['', 'Sydney, Australia', 'Toronto, Canada', 'London, England', 'Bengaluru, India', 'Auckland, New Zealand', 'Florida, United States']

fetcher = initialize_fetcher()

def get_data(filepath):
    with open(filepath, "r", encoding="utf-8") as file:
        return SortedSet(file.read().lower().splitlines())


def write_result(google_categories, partner_categories):
    with open(csv_filename, 'a+') as csv_file:
        writer = csv.writer(csv_file)
        for g_cat, p_cat in zip(google_categories, partner_categories):
            writer.writerow([g_cat, p_cat])


def clear_csv():
    csv_file.close()
    open(csv_filename, 'w').close()


def get_close_matches(difference, partner_categories_1, cutoff=0.96):
    matches_list = []

    for category in difference:
        matches = difflib.get_close_matches(str(category), partner_categories_1, n=3, cutoff=cutoff)
        if len(matches):
#             print(category, matches)
            matches_list.append((category, matches))
    return pd.DataFrame(matches_list, columns=columns)


def get_synonyms(category):
    #     category = category.translate(translationTable)
    category = quote_plus(re.sub(r'[^\x00-\x7f]', '', category))

    url = 'http://api.datamuse.com/words?ml={}'.format(category)
#     print(url)
    r = urlopen(url)
    data = json.loads(r.read().decode('utf-8'))
    return [d['word'] for d in data][:5]


def initialize_fetcher():
    return Fetcher(
        user_agent='Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',  # user agent
        phantomjs_proxy='http://localhost:1234',  # phantomjs url
        pool_size=10,  # max httpclient num
        async=False
    )


def restart_phantomjs():
    time.sleep(5)
    os.system("sudo pkill -9 phantomjs")
    os.system("nohup phantomjs phantomjs_fetcher.js 1234 &")
    time.sleep(10)


def get_random_cities(count):
    restart_phantomjs()
    url = "https://www.randomlists.com/random-world-cities?qty={}#".format(count)
    response = fetcher.phantomjs_fetch(url)
    soup = BeautifulSoup(response['content'])
    cities = soup.select(".rand_medium")
    countries = soup.select(".rand_small")
    return ["{}, {}".format(city.get_text(), country.get_text()) for city, country in zip(cities, countries)]


def fetch_businesses(category):
    fetcher = initialize_fetcher()
    biz_list = []
    category = quote_plus(re.sub(r'[^\x00-\x7f]', '', category))
    for city in cities:
        url = 'https://www.google.com/search?tbm=lcl&q={} {}'.format(category, city)
#         print(url)
        response = fetcher.phantomjs_fetch(url)
        soup = BeautifulSoup(response['content'], 'html.parser')
        biz = [element.get_text() for element in soup.select("div[role=heading]")]
    biz_list += biz
    return biz_list


# map those categories to businesses

def fetch_businesses_from_list(matches):
    global cities
    mapping = {}
    cities = get_random_cities(10)
    for i, category in enumerate(matches):
        if i % 8 == 0:
            restart_phantomjs()
        business_list = fetch_businesses(category)
        mapping.update({category: business_list})
        print(i, category)
    return mapping


def find_word_in_list(word, categories):
    matches = []
    for category in categories:
        if word in category:
            #             print(category)
            matches.append(category)
    return matches


def save_businesses_to_file(categories, filename):
    mappings = fetch_businesses_from_list(categories)
    with open(filename, "w") as json_file:
        json.dump(mappings, json_file, indent=4)
        print("################## STORED ##############")


def load_categories(filename):
    with open(filename) as f:
        return json.loads(f.read())


def fetch_business_categories(category):
    fetcher = initialize_fetcher()
    category_list = []
    formatted_category = quote_plus(re.sub(r'[^\x00-\x7f]', '', category))
    for city in cities:
        url = 'https://www.google.co.in/search?tbm=lcl&q={} {}'.format(formatted_category, city)
    #         url = "https://www.google.com/search?tbm=lcl&q=zoo"
        #         print(url)
        response = fetcher.phantomjs_fetch(url)
        soup = BeautifulSoup(response['content'])

        try:
            categories = [element.select("div:nth-of-type(1)")[0].get_text().split('·')[-1].strip().lower() for element in soup.find_all("span", class_="rllt__details")]
        except:
            categories = []

        category_list += categories
    return (category, category_list)





def get_parent_category(category_map):
    #     category_list = fetch_business_categories(category)
    category, category_list = category_map
    if not category_list:
        return ''
    counter = Counter(category_list)
    if len(counter) > 1:
        sored_counter = sorted(counter, key=counter.get)
        if sorted(counter.values())[-2] > 2:
            candidate = sored_counter[-2].lower()
        else:
            return max(counter, key=counter.get).lower()
        return max(counter, key=counter.get).lower() if category == candidate else candidate
    else:
        max_cat = max(counter, key=counter.get).lower()
        return max_cat




def fetch_categories_from_list(difference, file):
    parent_categories = []
    for i, category in enumerate(difference):
        if i % 3 == 0:
            restart_phantomjs()
        category_list = fetch_business_categories(category)
        parent_categories.append(category_list)
        print("{}".format(category))
    with open(file, 'w') as file:
        file.write(json.dumps(parent_categories))


import csv


def load_results(filename):
    results = []
    with open(filename, "r", encoding='utf-8') as f:
        csvreader = csv.reader(f, delimiter=",")
        for row in csvreader:
            results.append(row)
    return results


def get_facebook_category(category, biz_name):
    results = google.search("{} facebook".format(entry))
    if not results:
        return []

    for result in results:
        if result.link and 'facebook' in result.link:
            link = result.link
            link.replace('www', 'm')
            response = requests.get(link)
            soup = BeautifulSoup(response.text)
            try:
                return [span.get_text() for span in soup.select('._1j-g span')]
            except:
                return []


def get_matching_categories(google_mapping, partner_mapping):
    matches = []
    max_length = 4

    for g_key, g_value in google_mapping.items():
        g_value_set = set(g_value)
        category_matches = []
        for p_key, p_value in partner_mapping.items():
            length = len(g_value_set.intersection(set(p_value)))
            if length >= max_length:
                category_matches.append(p_key)

        if len(category_matches):
            matches.append((g_key, category_matches))

    return pd.DataFrame(matches, columns=columns)


def get_synonym_matches(difference, partner_categories_1):
    matches_list = []
    
    for category in difference:
        if len(category.split()) == 1:
            synonyms = get_synonyms(category)
            partner_matches = []
            for synonym in synonyms:
                matches = difflib.get_close_matches(synonym, partner_categories_1, n=3, cutoff=0.96)
                if len(matches):
    #                 print(category, "--", synonym, matches)
                    partner_matches += matches
            if len(partner_matches):
                matches_list.append((category, partner_matches))
    
    return pd.DataFrame(matches_list, columns=columns)

def get_facebook_df(facebook_mapping):
    facebook_dict = []

    for category_dict in facebook_mapping:
        for key, value in category_dict.items():
            if not value: continue
            counter = Counter([v.lower() for v in value])
            
            max_cat = max(counter, key=counter.get).lower()
            facebook_dict.append((key.lower(), max_cat.lower()))
                       
    return pd.DataFrame(facebook_dict, columns = ['google_categories', 'facebook_categories'])


def invalid(value):
    return not bool(pattern.match(value))

def get_most_occuring_categories(category_map):
    category, category_list = category_map
    if not category_list:
        return ''
    counter = Counter(category_list)
    most_common =  list(filter(lambda item: item[1] > 2, counter.items()))
    return list(map(lambda x: x[0], sorted(most_common, key = lambda x: x[1], reverse=True)))