from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import sys
import configparser
config = configparser.ConfigParser()
config.read("../../config.ini")
sys.path.insert(1,config["DB"]["crawlers"])
from api.v1 import aws, azure, gcp, all

app = FastAPI(title="X-Cloud Compute Workload Analysis", version="0.0")

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(all.router, prefix="/api/v1", tags=["X-Cloud APIs"])
app.include_router(aws.router, prefix="/api/v1/aws", tags=["AWS APIs"])
app.include_router(azure.router, prefix="/api/v1/azure", tags=["Azure APIs"])
app.include_router(gcp.router, prefix="/api/v1/gcp", tags=["GCP APIs"])

if __name__ == "__main__":  
    uvicorn.run(
        'gateway:app',
        host='0.0.0.0',
        port=8000,
        reload=True,
        debug=True)
