from fastapi import APIRouter, status
import sys
import configparser
config = configparser.ConfigParser()
config.read("../../config.ini")
sys.path.insert(1,config["DB"]["crawlers"])
from providers import aws

router = APIRouter()
aws = aws.AWS()

@router.get('/compute/fetch',status_code=status.HTTP_202_ACCEPTED)
def fetch_new_aws_data():
    result = aws.get_new_data()
    return result

@router.get('/compute/refresh',status_code=status.HTTP_202_ACCEPTED)
def refresh_aws_data():
    result = aws.refresh_data()
    return result