import adal
import json        
import requests
import sys
import time
from pymongo import MongoClient
import configparser
config = configparser.ConfigParser()
config.read("../../config.ini")
secrets = config['DB']

SUBSCRIPTION = secrets["Subscription"]
TENANT_ID = secrets["Tenant_Id"]
CLIENT_ID = secrets["Client_Id"]
CLIENT_SECRET = secrets["Client_Secret"]

AD_ENDPOINT = "https://login.microsoftonline.com"
RESOURCE_MANAGER_ENDPOINT = "https://management.azure.com/"

import sys
sys.path.insert(2, secrets["crawlers"])

class Azure:
    def __init__(self):
        f = open('{}providers/azure_category.json'.format(sys.path[2]))
        self.category = json.load(f)
        self.get_token()
        self.price={}
        self.prices()
        self.client = MongoClient(config["DB"]["ConnectionString"])
        self.instances_database = self.client['instances']
        self.azure_collection = self.instances_database['azure']

    def get_token(self):
        authority_uri = AD_ENDPOINT + "/" + TENANT_ID
        context = adal.AuthenticationContext(authority_uri)
        token_data = context.acquire_token_with_client_credentials(
            RESOURCE_MANAGER_ENDPOINT,
            CLIENT_ID,
            CLIENT_SECRET)
        self.bearer_token = "Bearer " + token_data.get("accessToken")
    
    def get_instances(self,location='eastus'):
        records=[]
        url="https://management.azure.com/subscriptions/{Subscription}/providers/Microsoft.Compute/skus?api-version=2021-07-01&%24filter=location%20eq%20'{location}'".format(Subscription=SUBSCRIPTION,location=location)
        payload={}
        headers = {
        'Authorization': self.bearer_token
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            instance_data = json.loads(response.text)
            for instance in instance_data["value"]:
                if(instance["resourceType"]=="virtualMachines"):
                    record={}
                    record["provider"]="azure"
                    record["instanceType"]=instance["name"]
                    record["region"]="us-east-1"
                    for item in instance["capabilities"]:
                        if(item["name"]=="vCPUs"):
                            record["cpu"]=float(item["value"])
                        if(item["name"]=="MemoryGB"):
                            record["ram"]=float(item["value"])
                        if(item["name"]=="MaxResourceVolumeMB"):
                            record["localStorageSupported"]=False
                            if(item["value"]!=0):
                                record["localStorageSupported"]=True
                                record["localStorage"]=(float(item["value"])/1024)
                    if instance["name"] in self.price:
                        record["pricePerHr"]=self.price[instance["name"]]
                    else:
                        record["pricePerHr"]=None
                    record["operatingSystem"]="Linux"
                    record["instanceCategory"]="Unknown"

                    for data in self.category:
                        temp=instance["family"].replace("standard","")
                        temp=temp.replace("Family","")
                        if data in temp:
                            record["instanceCategory"]=self.category[data]
                    record["metadata"]={
                    "processor":"NA",
                    "clockSpeed":"NA",
                    "gpuSupport":"Not supported"
                    }
                    record["releaseAt"]="NA"
                    record["_id"] = "{}/{}/{}/{}".format(record["provider"],record["region"],record["operatingSystem"],record["instanceType"])
                    records.append(record)
        return records

    def prices(self,location='eastus'):
        skip=0
        while(1):
            url = "https://prices.azure.com/api/retail/prices?$filter=PriceType%20eq%20%27Consumption%27%20AND%20armRegionName%20eq%20%27{location}%27%20AND%20serviceName%20eq%20%27Virtual%20Machines%27&$skip={skip}".format(location=location,skip=skip)
            # print(url)
            payload={}
            headers = {}
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = json.loads(response.text)
                for item in data['Items']:
                    if('Windows' not in item['productName']):
                        self.price[item["armSkuName"]]=item["unitPrice"]
                if(data["NextPageLink"]==None):
                    break
                else:
                    skip+=100
                    
    def get_new_data(self):
        instances = self.get_instances()
        for i in range(1,len(instances)):
            new_document = instances[i]
            self.azure_collection.insert_one(new_document)
        return "Done"

    def update_new_data(self):
        instances = self.get_instances()
        for i in range(1,len(instances)):
            new_document = instances[i]
            instance_uid = "{}/{}/{}/{}".format(new_document['provider'],new_document['region'],new_document['operatingSystem'],new_document['instanceType'])
            filter = { 'uid': instance_uid }
            newvalues = { "$set": new_document }
            self.azure_collection.update_one(filter, newvalues)
    
    def update_data(self):
        #Azure doesn't have any mechanism to check if Data is updated
        #So, for every refresh, we populate the data
        metadata_collection = self.instances_database['metadata']

        last_fetched_cursor = metadata_collection.find({},{ "_id": 0, "azure_last_fetched": 1})
        for doc in last_fetched_cursor:
            last_fetched_value = doc['azure_last_fetched']

        last_refreshed_cursor = metadata_collection.find({},{ "_id": 0, "azure_last_refreshed": 1})
        for doc in last_refreshed_cursor:
            last_refreshed_value = doc['azure_last_refreshed']
        
        current_time = time.time()

        lf_myquery = { "azure_last_fetched": "{}".format(last_fetched_value) }
        lf_newvalues = { "$set": { "azure_last_fetched": "{}".format(current_time)} }
        metadata_collection.update_one(lf_myquery, lf_newvalues)

        lr_myquery = { "azure_last_refreshed": "{}".format(last_refreshed_value) }
        lr_newvalues = { "$set": { "azure_last_refreshed": "{}".format(current_time) } }
        metadata_collection.update_one(lr_myquery, lr_newvalues)
        return True

    def refresh_data(self):
        if self.update_data() == False:
            return "Data is already up-to-date!"
        self.update_new_data()
        return "Updated to latest data!"
            