import boto3
from os import environ as os_environ
from json import dumps as json_dumps
from time import time

cache = None
cache_time = 0

def lambda_handler(event, context):
    global cache
    global cache_time

    if cache is not None and time() > cache_time + 10:
        return cache

    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(os_environ['CHALLENGES_TABLE'])

        # Get all users
        response = table.scan()

        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            return {
                'statusCode': 500,
                'body': json_dumps({"message": 'Error retrieving challenges', "err": "dynamodbError"})
            }

        # Create response
        cache = {
            "statusCode": 200,
            "body": json_dumps(response['Items'], default=int)
        }
        cache_time = time()
        return cache
    except Exception as error:
        return {
            'statusCode': 500,
            'body': json_dumps({"message": str(error), "err": "internalError"})
        }
