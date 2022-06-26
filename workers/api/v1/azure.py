from fastapi import APIRouter, status
import sys
import configparser
config = configparser.ConfigParser()
config.read("../../config.ini")
sys.path.insert(1,config["DB"]["crawlers"])
from providers import azure

router = APIRouter()
azure = azure.Azure()

@router.get('/compute/fetch',status_code=status.HTTP_202_ACCEPTED)
def fetch_new_azure_data():
    result = azure.get_new_data()
    return result

@router.get('/compute/refresh',status_code=status.HTTP_202_ACCEPTED)
def refresh_azure_data():
    result = azure.refresh_data()
    return result
