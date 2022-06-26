from fastapi import APIRouter, status
import sys
import requests
import configparser
from pymongo import MongoClient
config = configparser.ConfigParser()
config.read("../../config.ini")
sys.path.insert(1,config["DB"]["crawlers"])

client = MongoClient(config["DB"]["ConnectionString"])
instances_database = client['instances']
metadata_collection = instances_database['metadata']

router = APIRouter()

@router.get('/metadata',status_code=status.HTTP_202_ACCEPTED)
def fetch_last_refreshed_at():
    result = {}
    last_refreshed_cursor = metadata_collection.find({},{
        "_id": 0, 
        "aws_last_refreshed": 1, 
        "azure_last_refreshed": 1, 
        "gcp_last_refreshed": 1})
    for doc in last_refreshed_cursor:
        result.update({"aws_last_refreshed":doc['aws_last_refreshed']})
        result.update({"azure_last_refreshed":doc['azure_last_refreshed']})
        result.update({"gcp_last_refreshed":doc['gcp_last_refreshed']})
    return result

@router.get('/regions',status_code=status.HTTP_202_ACCEPTED)
def get_supported_regions():
    regions = []
    regions_cursor = metadata_collection.find({},{ "_id": 0, "regions": 1})
    for doc in regions_cursor:
        regions = doc['regions']
    return regions

@router.get('/vm/sizer/{cpu}/{ram}',status_code=status.HTTP_202_ACCEPTED)
def get_compute_instances(cpu, ram):    
    url = "http://127.0.0.1:5000/api/v1/vm/sizer?cpu={}&ram={}&region=us-east-1".format(cpu,ram)
    payload={}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    return response.json()

@router.get('/vm/sizer/matching/{provider}/{instance_type}',status_code=status.HTTP_202_ACCEPTED)
def get_matching_instances(provider, instance_type):    
    url = "http://127.0.0.1:5000/api/v1/vm/{}/{}/sizer?sortBy=cost".format(provider,instance_type)
    payload={}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    return response.json()