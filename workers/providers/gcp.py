import csv
from pymongo import MongoClient
import time
from datetime import datetime
from bs4 import BeautifulSoup
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import requests
import configparser
config = configparser.ConfigParser()
config.read("../../config.ini")

import sys
sys.path.insert(2,config["DB"]["crawlers"])

class GCP:
    def __init__(self):
        self.client = MongoClient(config["DB"]["ConnectionString"])
        self.instances_database = self.client['instances']
        self.gcp_collection = self.instances_database['gcp']

    def read_csv(self):
        csv_file_path = "{}providers/gcp.csv".format(sys.path[2])
        reader = csv.reader(open(csv_file_path),delimiter=',',quoting=csv.QUOTE_ALL,skipinitialspace=True)
        return list(reader)

    def get_metadata(self, cpu_type, gpu_support):
        processor = cpu_type.split('@')
        if len(processor) == 2:
            metadata = {
                "processor": processor[0],
                "clockSpeed": processor[1],
                "gpuSupport": gpu_support
            }
        else:
            metadata = {
                "processor": cpu_type,
                "clockSpeed": "NA",
                "gpuSupport": gpu_support
            }
        return metadata

    def get_instance_category(self, instance_type):
        instance_category = ""
        categories = ['General purpose','Compute optimized','Memory optimized','GPU instance']
        value = instance_type.split('-')[1]
        if value == "highcpu":
            instance_category = categories[1]
        elif value == "highmem" or value == "megamem" or value == "ultramem":
            instance_category = categories[2]
        elif value == "highgpu" or value == "megagpu":
            instance_category = categories[3]
        else:
            instance_category = categories[1]
        return instance_category
        
    def format_item(self, item):
        if item == "shared":
            return float(1)
        if item == "Unavailable":
            return float(40)
        new_item = item.split(' ')[0]
        result = new_item.replace("$","")
        return float(result)

    def get_csv_rows_count(self):
        rows = self.read_csv()
        return len(rows)

    def get_new_document(self, counter):
        document = {}
        rows = self.read_csv()
        document["instanceType"] = rows[counter][0]
        document["region"] = "us-east-1"
        document["cpu"] = self.format_item(rows[counter][1])
        document["ram"] = self.format_item(rows[counter][2])
        document["provider"] = "GCP"
        document["pricePerHr"] = self.format_item(rows[counter][10])
        if rows[counter][3] == "Supported":
            document["localStorageSupported"] = True
            document["localStorage"] = float(375)
        else:
            document["localStorageSupported"] = False
            document["localStorage"] = float(0)
        document["operatingSystem"] = "Linux"
        document["instanceCategory"] = self.get_instance_category(rows[counter][0])
        cpu_type = rows[counter][5]
        gpu_support = rows[counter][6]
        document["metadata"] = self.get_metadata(cpu_type, gpu_support)
        document["releasedAt"] = "NA"
        document["_id"] = "{}/{}/{}/{}".format(document["provider"],document["region"],document["operatingSystem"],document["instanceType"])
        return document

    def getCSV(self) :
        #To pass options while setting up chrome webdriver
        options = Options()
        # For not opening the browser
        options.add_argument('headless')
        #Path to chromedriver exe
        ser = Service("/<path-to-chromdriver>/chromedriver")
        #Setting up chrome driver
        driver = webdriver.Chrome(service=ser ,options=options)
        #Fetching the webpage
        driver.get("https://gcpinstances.doit-intl.com/")
        #Downloading the CSV
        driver.find_element(by=By.XPATH, value="/html/body/div[3]/div/a").click()
        #waitig for CSV to get download
        time.sleep(5)
        if os.path.exists("gcp.csv"):
            os.remove("gcp.csv")  
        else:
            print("File not found in the directory")
        os.rename("GCPinstances.info - GCP Compute Engine Instance Comparison (by DoiT International).csv", "gcp.csv")

    def get_latest_fetched_data(self):
        url = "https://gcpinstances.doit-intl.com/"
        payload={}
        headers = {}
        response = requests.request("GET", url, headers=headers, data=payload)
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        content = soup.find('div', {"class": "page-header"})
        utcDateStr = content.find("p").text[13:32]
        utc = datetime.strptime(utcDateStr, '%Y-%m-%d %H:%M:%S')
        epoch_time = (utc - datetime(1970, 1, 1)).total_seconds()
        return epoch_time

    def get_new_data(self):
        count = self.get_csv_rows_count()
        for i in range(1,count):
            new_document = self.get_new_document(i)
            self.gcp_collection.insert_one(new_document)
        return "Done"

    def update_new_data(self):
        count = self.get_csv_rows_count()
        for i in range(1,count):
            new_document = self.get_new_document(i)
            instance_uid = "{}/{}/{}/{}".format(new_document['provider'],new_document['region'],new_document['operatingSystem'],new_document['instanceType'])
            filter = { 'uid': instance_uid }
            newvalues = { "$set": new_document }
            self.gcp_collection.update_one(filter, newvalues)
    
    def update_data(self):
        metadata_collection = self.instances_database['metadata']

        last_fetched_cursor = metadata_collection.find({},{ "_id": 0, "gcp_last_fetched": 1})
        for doc in last_fetched_cursor:
            last_fetched_value = doc['gcp_last_fetched']

        last_refreshed_cursor = metadata_collection.find({},{ "_id": 0, "gcp_last_refreshed": 1})
        for doc in last_refreshed_cursor:
            last_refreshed_value = doc['gcp_last_refreshed']
            
        gcp_last_fetched_value = self.get_latest_fetched_data()

        lr_myquery = { "gcp_last_refreshed": "{}".format(last_refreshed_value) }
        lr_newvalues = { "$set": { "gcp_last_refreshed": "{}".format(time.time()) } }
        metadata_collection.update_one(lr_myquery, lr_newvalues)

        if str(gcp_last_fetched_value) != str(last_fetched_value):
            lf_myquery = { "gcp_last_fetched": "{}".format(last_fetched_value) }
            lf_newvalues = { "$set": { "gcp_last_fetched": "{}".format(gcp_last_fetched_value)} }
            metadata_collection.update_one(lf_myquery, lf_newvalues)
            return True
        return False

    def refresh_data(self):
        if self.update_data() == False:
            return "Data is already up-to-date!"
        self.getCSV()
        self.update_new_data()
        return "Updated to latest data!"
        