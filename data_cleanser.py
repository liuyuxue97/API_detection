# API url patterns:
# 1. URLs should include nouns, not verbs
# 2. Use plural nouns only for consistency(no singular nouns)
# 3. Could contain a version number, if not then it could refer to the latest version
# 4. URL allows users to request formats like JSON or XML (eg: ends with  xxx.json/xxx.xml)
# 5. resource/identifier/resource

import re
import requests
import json
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import io
import os
import sys
from bs4 import BeautifulSoup
from urllib.request import urlopen
import time
import datetime


starttime = datetime.datetime.now()


sys.stdout = io.TextIOWrapper(sys.stdout.buffer)
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

api_dir = './json_xml_text_api/'
if not os.path.exists(api_dir):
    os.mkdir(api_dir)

headers = {
    'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36",
    }

# url is not deeper than resource/identifier/resource
# eg: http://xxx.com/resource/identifier/resource (maximum 5 slash)
def slash_number_check(url):
    url_list = []
    sub = "/"
    number = url.count(sub)
    if number >= 5:
        index = url.find(sub)
        index2 = url.find(sub, index + 1)
        index3 = url.find(sub, index2 + 1)
        index4 = url.find(sub, index3 + 1)
        index5 = url.find(sub, index4 + 1)
        url = url[0:index5]
        url_list.append(url)
    else:
        url_list.append(url)
    return url_list

def text_extract(url):
    response = requests.request('GET', url, headers=headers)
    response.encoding = response.apparent_encoding
    soup = BeautifulSoup(response.text, 'html.parser')
    script = str(soup)
    return script


def detect_status_200(url):
    try:
        resp = urlopen(url)
        code = resp.getcode()
        if code == 200:
            return True
    except:
        return False

def save_file(data, url):
    number = 1
    with open(api_dir + url[8,10] + "result_{}.json".format(number), "w") as f:
        number += 1
        json.dump(data, f)
        f.close()


def remove_re(str):
    new_str = re.findall(r"(.*)\/", str)
    return new_str


def successful_state():
    current = int(time.time())
    interval = current + int(sys.argv[2])
    file = open('/tmp/check_http_status_%s.txt'%sys.argv[1],'w')
    file.write(str(current)+'|'+str(interval)+'|'+'0\n')
    file.close()


def status_json(url):
    r = requests.get(url)
    # status = r.status_code
    try:
        r.json()
        return True   #('OK: The current return status %s, Data as JSON format.'%status)
    except:
        file = open('/tmp/check_http_status_%s.txt'%sys.argv[1],'r')
        read_file = file.read()
        file.close()
        read_file_three = read_file.split('|')[2]
        read_file_three = int(read_file_three) + 1
        if read_file_three > 3:
            successful_state()
            return True  #('OK: The current return status %s, Data as JSON format.'%status)
        else:
            current = int(time.time())
            interval = current + int(sys.argv[2])
            file = open('/tmp/check_http_status_%s.txt'%sys.argv[1],'w')
            file.write(str(current)+'|'+str(interval)+'|'+str(read_file_three))
            file.close()
            return False  #('WARNING: The current return status %s, The data is not a JSON format.'%status)



#url ends with 'api-docs' would be api page
# api.endswith('api-docs'):
# api_url_candidate_set.add(api)
# html_end = requests.get(api)
# save_file(html_end,api)

#Get API dataset
with open('json&xml_api_url.txt', 'r') as f:
    api_response_urls = f.readlines()

api_url_candidate_list = []


print('-----clean urls------')
#clean the queryString and repeated urls
for url in api_response_urls:
    if '?' not in url and url not in api_url_candidate_list:
        api_url_candidate_list.append(url)
    elif '?' in url:
        first_cleaned_url = re.findall(r"(.*)\?", url)
        for first_cleaned_url in first_cleaned_url:
            if first_cleaned_url not in api_url_candidate_list:
                api_url_candidate_list.append(first_cleaned_url)

print('-----clean resource------')
#Remove one layer of resource for url
for url in api_url_candidate_list:
    try:
        new_url = remove_re(url)
        api_url_candidate_list.append(new_url)
    except:
        pass

print(len(api_url_candidate_list))
print('-----check urls------')
number = 1
for url in api_url_candidate_list:
    # url is not deeper than resource/identifier/resource
    url_list = slash_number_check(url)
    for i in url_list:
        # detect if url can open
        detect_status_200(i)
        if True:
            # detect if it is html page or json page
            try:
                status_json(i)
                if True:
                    text = text_extract(i)
                    with open(api_dir + "result_{}.json".format(number), "w") as f:
                        number += 1
                        json.dump(text, f)
                        f.close()
            except:
                pass


endtime = datetime.datetime.now()
print ((endtime - starttime).seconds)






