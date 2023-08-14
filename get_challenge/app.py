import boto3
from os import environ as os_environ
from json import dumps as json_dumps
from time import time

cache = {}
cache_time = {}

def lambda_handler(event, context):
    global cache
    global cache_time

    challenge_id = event['pathParameters']['challenge']
    if challenge_id in cache and time() < cache_time[challenge_id] + int(os_environ['CACHE_TIME']):
        return cache[challenge_id]

    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(os_environ['CHALLENGES_TABLE'])

        # Get user from event.pathParameters.username
        response = table.get_item(
            Key={
                'challenge': challenge_id
            }
        )

        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            return {
                'statusCode': 500,
                'body': json_dumps({"message": 'Error retrieving challenge', "err": "dynamodbError"})
            }

        # Create response, if empty return 404
        if 'Item' not in response:
            return {
                "statusCode": 404,
                "body": json_dumps({"message": "Challenge not found", "err": "notFound"})
            }

        cache[challenge_id] = {
            "statusCode": 200,
            "body": json_dumps(response['Item'], default=int)
        }
        cache_time[challenge_id] = time()
        return cache[challenge_id]
    except Exception as error:
        return {
            'statusCode': 500,
            'body': json_dumps({"message": str(error), "err": "internalError"})
        }
