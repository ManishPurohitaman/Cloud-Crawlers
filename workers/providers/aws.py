import json
from urllib.request import urlopen
from pymongo import MongoClient
import re
from dateutil import parser
import time
import configparser
config = configparser.ConfigParser()
config.read("../../config.ini")

class AWS:
    def __init__(self):
        self.client = MongoClient(config["DB"]["ConnectionString"])
        self.instances_database = self.client['instances']
        self.aws_collection = self.instances_database['aws']

    def get_instances(self):

        baseUrl = "https://pricing.us-east-1.amazonaws.com"
        offerUrl = "/offers/v1.0/aws/AmazonEC2/current/{regionCode}/index.json"
        allRegionOfferUrl = "/offers/v1.0/aws/AmazonEC2/current/index.json"
        usEast1RegionCode = "us-east-1"
        ec2OfferCode = "AmazonEC2"
        records = []

    #   For all regions
    #   offerResponse = urlopen(baseUrl + allRegionOfferUrl)
        
        offerResponse = urlopen(baseUrl + offerUrl.format(offerCode=ec2OfferCode, regionCode=usEast1RegionCode))
        offerJson = json.loads(offerResponse.read())
        pricesJson = offerJson["terms"]["OnDemand"]

        for product in offerJson["products"]:
            productJson = offerJson["products"][product]
            if (productJson["productFamily"] != "Compute Instance") and (productJson["productFamily"] != "Compute Instance (bare metal)"):
                continue
            if productJson["attributes"]["operatingSystem"] != "Linux":
                continue
            if productJson["attributes"]["operation"] != "RunInstances":
                continue
            if productJson["attributes"]["tenancy"] != "Shared":
                continue
            if re.match('^BoxUsage', productJson["attributes"]["usagetype"]) == None:
                continue

            def createObj(productJson):
                productAttr = productJson["attributes"]

                offerDict = {
                    "instanceType": productAttr["instanceType"],
                    "region": productAttr["regionCode"],
                    "cpu": float(productAttr["vcpu"]),
                    "ram": float(productAttr["memory"].split()[0]),
                    "provider": "AWS",
                    "operatingSystem": productAttr["operatingSystem"],
                    "instanceCategory": productAttr["instanceFamily"],
                    "metadata": {"gpuSupport": "NA"},
                    "releaseAt": "NA"
                }

                try:
                    offerDict["metadata"]["processor"] = productAttr["physicalProcessor"]
                except KeyError:
                    pass

                try:
                    offerDict["metadata"]["clockSpeed"] = productAttr["clockSpeed"]
                except KeyError:
                    pass

                if productAttr["storage"] == "EBS only":
                    offerDict["localStorageSupported"] = False
                    offerDict["localStorage"] = float(0)
                else:
                    offerDict["localStorageSupported"] = True
                    values = productAttr["storage"].split()
                    if(values[1] == "x"):
                        offerDict["localStorage"] = float(
                            values[0]) * float(values[2])
                    else:
                        offerDict["localStorage"] = float(values[0])

                currentPriceKey = list(list(pricesJson[productJson["sku"]].values())[0]["priceDimensions"].values())[0]
                offerDict["pricePerHr"] = float(currentPriceKey["pricePerUnit"]["USD"])

                offerDict["_id"] = "{}/{}/{}/{}".format(offerDict["provider"],offerDict["region"],offerDict["operatingSystem"],offerDict["instanceType"])

                return offerDict

            records.append(createObj(productJson))

        return records

    def awsLastFetched(self):
        baseUrl = "https://pricing.us-east-1.amazonaws.com"
        offerUrl = "/offers/v1.0/aws/AmazonEC2/current/{regionCode}/index.json"
        allRegionOfferUrl = "/offers/v1.0/aws/AmazonEC2/current/index.json"
        usEast1RegionCode = "us-east-1"
        offerResponse = urlopen(baseUrl + offerUrl.format(regionCode=usEast1RegionCode))
        offerJson = json.loads(offerResponse.read())
        return parser.parse(offerJson["publicationDate"]).timestamp()

    def get_new_data(self):
        instances = self.get_instances()
        for i in range(1,len(instances)):
            new_document = instances[i]
            self.aws_collection.insert_one(new_document)
        return "Done"
    
    def update_new_data(self):
        instances = self.get_instances()
        for i in range(1,len(instances)):
            new_document = instances[i]
            instance_uid = "{}/{}/{}/{}".format(new_document['provider'],new_document['region'],new_document['operatingSystem'],new_document['instanceType'])
            filter = { 'uid': instance_uid }
            newvalues = { "$set": new_document }
            self.aws_collection.update_one(filter, newvalues)

    def update_data(self):

        metadata_collection = self.instances_database['metadata']

        last_fetched_cursor = metadata_collection.find({},{ "_id": 0, "aws_last_fetched": 1})
        for doc in last_fetched_cursor:
            last_fetched_value = doc['aws_last_fetched']

        last_refreshed_cursor = metadata_collection.find({},{ "_id": 0, "aws_last_refreshed": 1})
        for doc in last_refreshed_cursor:
            last_refreshed_value = doc['aws_last_refreshed']
            
        aws_last_fetched_value = self.awsLastFetched()

        lr_myquery = { "aws_last_refreshed": "{}".format(last_refreshed_value) }
        lr_newvalues = { "$set": { "aws_last_refreshed": "{}".format(time.time()) } }
        metadata_collection.update_one(lr_myquery, lr_newvalues)

        if str(aws_last_fetched_value) != str(last_fetched_value):
            lf_myquery = { "aws_last_fetched": "{}".format(last_fetched_value) }
            lf_newvalues = { "$set": { "aws_last_fetched": "{}".format(aws_last_fetched_value)} }
            metadata_collection.update_one(lf_myquery, lf_newvalues)
            return True
        return False


    def refresh_data(self):
        if self.update_data() == False:
            return "Data is already up-to-date!"
        self.update_new_data()
        return "Updated to latest data!"
