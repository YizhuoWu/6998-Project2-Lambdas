import json
import requests
import boto3
import inflect



def search(item, allurl):
    headers = { "Content-Type": "application/json" }
    ENDPOINT = "https://search-photos-fntfv7yrgxc4zptmna5agsqkqe.us-west-2.es.amazonaws.com"
    url = ENDPOINT + '/_search?q=' + item
    response = requests.get(url, headers=headers, auth=("AdminMaster", "Admin@98")).json()
    print(response["hits"]["hits"])
    
    for pic in response["hits"]["hits"]:
        allurl.append("https://photostorage-hw2.s3.amazonaws.com/" + pic["_id"])
    
    
def connectwithlex(userinput):
    lex_client = boto3.client('lex-runtime') 
    
    response = lex_client.post_text(
        botName='PhotoSearch',
        botAlias='Final',
        userId='test',
        inputText=userinput
    )
    try:
        print(response)
        slots = response['slots']
        print(slots)
        if (slots["AnswerTwo"] == None):
            lex_client.post_text(
                botName='PhotoSearch',
                botAlias='Final',
                userId='test',
                inputText="cat"
            )
            return [slots['Answer']]
        else:
            return[slots['Answer'], slots['AnswerTwo']]
    except:
        return []
 
def lambda_handler(event, context):
    # TODO implement
    p = inflect.engine()
    try:
        print(event["queryStringParameters"]['q'])
        userinput = event["queryStringParameters"]['q']
        
        searchitem = connectwithlex(userinput)
        allurl = []
 
        for item in searchitem:
            search(item, allurl)
            #item = p.singular_noun(item)
            
    
        return {
            "isBase64Encoded": False,
            "statusCode": 200,
            "headers": {"Access-Control-Allow-Origin" : "*","Access-Control-Allow-Credentials" : True},
            'body': json.dumps({
                'images':allurl}
                )
        }
        
    except:
        return {
            "isBase64Encoded": False,
            "statusCode": 200,
            "headers": {"Access-Control-Allow-Origin" : "*","Access-Control-Allow-Credentials" : True},
            'body': json.dumps({
                'images':[]}
                )
        }       
