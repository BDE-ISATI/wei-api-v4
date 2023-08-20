import boto3
from os import environ as os_environ
from json import dumps as json_dumps
from time import time

cache = None
cache_time = 0


def lambda_handler(event, context):
    global cache
    global cache_time

    if cache is not None and time() < cache_time + int(os_environ['CACHE_TIME']):
        return cache

    try:
        dynamodb = boto3.resource('dynamodb')
        challenge_table = dynamodb.Table(os_environ['CHALLENGES_TABLE'])
        user_table = dynamodb.Table(os_environ['USER_TABLE'])

        challenges = challenge_table.scan()

        if challenges['ResponseMetadata']['HTTPStatusCode'] != 200 or 'Items' not in challenges:
            return {
                'statusCode': 500,
                'body': json_dumps({"message": 'Error retrieving challenges', "err": "dynamodbError"})
            }

        challenges = challenges['Items']

        users = user_table.scan()

        if users['ResponseMetadata']['HTTPStatusCode'] != 200 or 'Items' not in users:
            return {
                'statusCode': 500,
                'body': json_dumps({"message": 'Error retrieving users', "err": "dynamodbError"})
            }

        users = users['Items']

        for challenge in challenges:
            t = list(filter(lambda x: challenge['challenge'] in x['challenges_done'], users))
            challenge['users'] = [{"username": x['username'], 'display_name': x['display_name'], "picture_id": x["picture_id"] if 'picture_id' in x else ''} for x in t]

        cache = {
            "statusCode": 200,
            "body": json_dumps(challenges, default=int)
        }
        cache_time = time()
        return cache
    except Exception as error:
        return {
            'statusCode': 500,
            'body': json_dumps({"message": str(error), "err": "internalError"})
        }
