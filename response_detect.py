from browsermobproxy import Server
from selenium import webdriver
import time
import json
import threading
import os

os.environ["CUDA_VISIBLE_DEVICES"] = "0"

#Get the URLs from dataset
file = './res.json'
data_key = "id"
urlData = open(file, 'r').read()
api_response_url_file = open('json&xml_api_url.txt', 'w')
api_response_url_set = set()
data = json.loads(urlData)
url_list = []
response_data = data["response"]  # {..., "docs":[ { "id":, },{ "id"：, },{"id"}...] }
docs_data = response_data["docs"]  # "doc":[ { "id":, },{ "id"：, },{"id"}...]
for i in docs_data:
    if "http" in i[data_key] and i[data_key][-3:] != "pdf" and i[data_key][-4:] != "file":
        url_list.append(i[data_key])
        # url_file.write(i[data_key])
        # url_file.write('\n')


class ProxyManger:

    __BMP = "C:/Users/liuyu/Downloads/browsermob-proxy-2.1.4/bin/browsermob-proxy.bat"

    def __init__(self):

        self.__server = Server(ProxyManger.__BMP)
        self.__client = None

    def start_server(self):
        self.__server.start()
        return self.__server

    def start_client(self):

        self.__client = self.__server.create_proxy(params={"trustAllServers": "true"})
        return self.__client

    @property
    def client(self):
        return self.__client

    @property
    def server(self):
        return self.__server


if __name__=="__main__":
    # Start Proxy
    proxy = ProxyManger()
    server = proxy.start_server()
    client = proxy.start_client()

    # Configure proxy to start webdriver
    options = webdriver.ChromeOptions()
    options.add_argument("--proxy-server={}".format(client.proxy))
    options.add_argument('--ignore-certificate-errors')
    chromePath = r'C:\Users\liuyu\Downloads\chromedriver.exe'
    driver = webdriver.Chrome(executable_path=chromePath, chrome_options=options)
    webdriver.DesiredCapabilities.CHROME['acceptSslCerts'] = True

    # Get the returned content
    har_name = 1
    for url in url_list:
        print('Checking url-->' + str(har_name))
        print(url)
        try:
            client.new_har(har_name)
            driver.get(url)
            time.sleep(3)
            har_name += 1

            newHar = client.har
            for entry in newHar['log']['entries']:
                request = entry['request']
                response = entry['response']
                content = response['content']
                if 'application/json' or 'application/xml' in content['mimeType']:
                    api_response_url_set.add(request['url'] + '\n')
            server.stop()
        except Exception as e:
            print(e)
        print(len(api_response_url_set))

    api_response_url_file.writelines(api_response_url_set)







