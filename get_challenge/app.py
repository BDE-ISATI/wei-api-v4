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
        challenge_table = dynamodb.Table(os_environ['CHALLENGES_TABLE'])
        user_table = dynamodb.Table(os_environ['USER_TABLE'])

        # Get user from event.pathParameters.username
        challenge = challenge_table.get_item(
            Key={
                'challenge': challenge_id
            }
        )

        if challenge['ResponseMetadata']['HTTPStatusCode'] != 200:
            return {
                'statusCode': 500,
                'body': json_dumps({"message": 'Error retrieving challenge', "err": "dynamodbError"})
            }

        if 'Item' not in challenge:
            return {
                "statusCode": 404,
                "body": json_dumps({"message": "Challenge not found", "err": "notFound"})
            }

        users = user_table.scan()

        if users['ResponseMetadata']['HTTPStatusCode'] != 200:
            return {
                'statusCode': 500,
                'body': json_dumps({"message": 'Error retrieving users', "err": "dynamodbError"})
            }

        t = list(filter(lambda x: challenge['Item']['challenge'] in x['challenges_done'], users['Items']))
        challenge['Item']['users'] = [{ 'username': x['username'], 'picture_id': x['picture_id'] if 'picture_id' in x else ''} for x in t]

        cache[challenge_id] = {
            "statusCode": 200,
            "body": json_dumps(challenge['Item'], default=int)
        }
        cache_time[challenge_id] = time()
        return cache[challenge_id]
    except Exception as error:
        return {
            'statusCode': 500,
            'body': json_dumps({"message": str(error), "err": "internalError"})
        }
