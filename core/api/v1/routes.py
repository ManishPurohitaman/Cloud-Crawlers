from core import app
import pymongo
from pymongo import MongoClient

from flask import request

import configparser

from .response import *

config = configparser.ConfigParser()
config.read("../config.ini")

dbClient = MongoClient(config["DB"]["ConnectionString"])
db = dbClient[config["DB"]["DatabaseName"]]
providersCollection = config["DB"]["ProvidersCollections"].split()


def fetchResponseDocuments(ram=-1,
                           cpu=-1,
                           region="",
                           instanceStorage="",
                           instanceCategory=".*",
                           sortBy="cost"):
    if region != "":
        region = "^" + region + "$"
    if instanceCategory != "":
        instanceCategory = "^" + instanceCategory + "$"

    instanceStorage1, instanceStorage2 = True, False
    if instanceStorage != "":
        instanceStorage1 = instanceStorage2 = (True if instanceStorage
                                               == "true" else False)

    documentsIds = set()
    documents = []

    for collection in providersCollection:
        documentsRamMajor = db[collection].find({
            "ram": {
                "$gte": ram
            },
            "cpu": {
                "$gte": cpu
            },
            "instanceCategory": {
                "$regex": instanceCategory
            },
            "localStorageSupported": {
                "$in": [instanceStorage1, instanceStorage2]
            },
            "region": {
                "$regex": region
            }
        }).sort([("ram", pymongo.ASCENDING),
                 ("cpu", pymongo.ASCENDING)]).limit(1)
        for document in documentsRamMajor:
            if document != None:
                documents += [document]

        documentsCpuMajor = db[collection].find({
            "ram": {
                "$gte": ram
            },
            "cpu": {
                "$gte": cpu
            },
            "instanceCategory": {
                "$regex": instanceCategory
            },
            "localStorageSupported": {
                "$in": [instanceStorage1, instanceStorage2]
            },
            "region": {
                "$regex": region
            }
        }).sort([("cpu", pymongo.ASCENDING),
                 ("ram", pymongo.ASCENDING)]).limit(1)
        for document in documentsCpuMajor:
            if document != None:
                if not documents or documents[0]["cpu"] != document["cpu"]:
                    documents += [document]

    responseDocumentsIds = set()
    responseDocuments = []

    for document in documents:
        ram = document["ram"]
        cpu = document["cpu"]
        provider = document["provider"]

        matchingDocuments = db[provider.lower()].find({
            "ram":
            ram,
            "cpu":
            cpu,
            "instanceCategory": {
                "$regex": instanceCategory
            },
            "localStorageSupported":
            document["localStorageSupported"],
            "region": {
                "$regex": region
            }
        })

        for matchingDocument in matchingDocuments:
            matchingDocument["id"] = str(matchingDocument["_id"])
            del matchingDocument["_id"]

            if matchingDocument["id"] in responseDocumentsIds:
                continue

            if matchingDocument["pricePerHr"] == None:
                matchingDocument["pricePerHr"] = 1e9+7

            responseDocumentsIds.add(matchingDocument["id"])
            responseDocuments += [matchingDocument]

    if sortBy == "cost":
        responseDocuments.sort(key=lambda x: x["pricePerHr"])

    return responseDocuments


# Compute Requirements Route
@app.route("/api/v1/vm/sizer", methods=["GET"])
def computeRequirements():
    ram = request.args.get("ram", default=-1, type=float)
    cpu = request.args.get("cpu", default=-1, type=int)
    region = request.args.get("region", ".*")
    instanceStorage = request.args.get("instanceStorage", default="", type=str)
    instanceCategory = request.args.get("instanceCategory", ".*")
    sortBy = request.args.get("sortBy", "cost")

    if ram == -1 or cpu == -1:
        return {
            "responseCode": RESPONSE_INVALID_ARGS,
            "responseMessage": MESSAGE_INVALID_ARGS,
            "data": []
        }

    responseDocuments = fetchResponseDocuments(ram, cpu, region,
                                               instanceStorage,
                                               instanceCategory, sortBy)

    return {
        "responseCode": RESPONSE_SUCCESS,
        "responseMessage": MESSAGE_SUCCESS,
        "data": responseDocuments
    }


# Matching Instance Route
@app.route("/api/v1/vm/<provider>/<instanceType>/sizer", methods=["GET"])
def matchingInstance(provider=None, instanceType=None):
    matchingDocument = db[provider].find_one({"instanceType": instanceType})

    ram = matchingDocument["ram"]
    cpu = matchingDocument["cpu"]
    region = ".*"
    instanceStorage = ""
    instanceCategory = ".*"
    sortBy = request.args.get("sortBy", "cost")

    responseDocuments = fetchResponseDocuments(ram, cpu, region,
                                               instanceStorage,
                                               instanceCategory, sortBy)
    return {
        "responseCode": RESPONSE_SUCCESS,
        "responseMessage": MESSAGE_SUCCESS,
        "data": responseDocuments
    }
