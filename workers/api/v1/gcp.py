from fastapi import APIRouter, status
import sys
import configparser
config = configparser.ConfigParser()
config.read("../../config.ini")
sys.path.insert(1,config["DB"]["crawlers"])
from providers import gcp

router = APIRouter()
gcp = gcp.GCP()

@router.get('/compute/fetch',status_code=status.HTTP_202_ACCEPTED)
def fetch_new_gcp_data():
    result = gcp.get_new_data()
    return result

@router.get('/compute/refresh',status_code=status.HTTP_202_ACCEPTED)
def refresh_gcp_data():
    result = gcp.refresh_data()
    return result
