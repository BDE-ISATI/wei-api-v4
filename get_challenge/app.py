import boto3
from os import environ as os_environ
from json import dumps as json_dumps
from time import time

cache = {}
cache_time = {}


def format_user(user, challenge_id):
    v = {"username": user['username'], 'display_name': user['display_name'],
         "picture_id": user["picture_id"] if 'picture_id' in user else '', 'time': -1}

    if 'challenges_times' in user and challenge_id in user['challenges_times']:
        v['time'] = user['challenges_times'][challenge_id]

    return v

def lambda_handler(event, context):
    global cache
    global cache_time

    challenge_id = event['pathParameters']['challenge']
    if challenge_id in cache and time() < cache_time[challenge_id] + int(os_environ['CACHE_TIME']):
        return cache[challenge_id]

    try:
        dynamodb = boto3.resource('dynamodb')

        challenge_table = dynamodb.Table(os_environ['CHALLENGES_TABLE'])
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

        challenge = challenge['Item']

        user_table = dynamodb.Table(os_environ['USER_TABLE'])
        users = user_table.scan()
        if users['ResponseMetadata']['HTTPStatusCode'] != 200 or 'Items' not in users:
            return {
                'statusCode': 500,
                'body': json_dumps({"message": 'Error retrieving users', "err": "dynamodbError"})
            }
        users = users['Items']

        t = list(filter(lambda x: challenge['challenge'] in x['challenges_done'], users))
        challenge['users'] = [format_user(x, challenge_id) for x in t]

        cache[challenge_id] = {
            "statusCode": 200,
            "body": json_dumps(challenge, default=int)
        }
        cache_time[challenge_id] = time()
        return cache[challenge_id]
    except Exception as error:
        return {
            'statusCode': 500,
            'body': json_dumps({"message": str(error), "err": "internalError"})
        }
