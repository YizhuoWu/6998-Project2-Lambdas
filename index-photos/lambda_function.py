import boto3
import os
import sys
import uuid
from urllib.parse import unquote_plus
import time
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import requests

def upload_to_elasticsearch(jsonDocu):

    host = 'search-photos-fntfv7yrgxc4zptmna5agsqkqe.us-west-2.es.amazonaws.com'
    es = Elasticsearch(
        hosts = [{'host': host, 'port': 443}],
        http_auth = ("AdminMaster", "Admin@98"),
        use_ssl = True,
        verify_certs = True,
        connection_class = RequestsHttpConnection
    )
    

    es.index(index="photos", doc_type="_doc", id=jsonDocu["objectKey"], body=jsonDocu)
    
    print(es.get(index="photos", doc_type="_doc", id=jsonDocu["objectKey"]))
    


def lambda_handler(event, context):

        

    s3_client = boto3.client('s3')
    reko_client = boto3.client('rekognition')
    
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = unquote_plus(record['s3']['object']['key'])
        print("here")
        
        headobject = s3_client.head_object(
            Bucket=bucket,
            Key=key
        )
        
        print(headobject)

        if headobject["Metadata"]['x-amz-meta-customlabels'] != "":
            print(headobject["Metadata"]['x-amz-meta-customlabels'])
            headobject = headobject["Metadata"]['x-amz-meta-customlabels'].split(",")
        else:
            headobject = []
            
        response = reko_client.detect_labels(
            Image={
                'S3Object': {
                    'Bucket': bucket,
                    'Name': key
                }
            },
            MaxLabels=10
        )
        
        labeldict = {}
        labeldict["objectKey"] = key
        labeldict["bucket"] = bucket
        labeldict["createdTimestamp"] = local_time = time.ctime(time.time())
        labeldict["labels"] = []
        
        for item in response["Labels"]:
            labeldict["labels"].append(item["Name"])
        for item in headobject:
            labeldict["labels"].append(item.strip())
            
        print(str(labeldict))
        
        upload_to_elasticsearch(labeldict)
    

        
