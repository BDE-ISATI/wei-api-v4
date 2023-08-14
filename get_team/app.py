import boto3
from json import dumps as json_dumps
from os import environ as os_environ
from time import time

cache = {}
cache_time = {}

def lambda_handler(event, context):
    global cache
    global cache_time

    team_name = event['pathParameters']['team']
    if team_name in cache and time() < cache_time[team_name] + int(os_environ['CACHE_TIME']):
        return cache[team_name]

    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(os_environ['TEAMS_TABLE'])

        # Get user from event.pathParameters.username
        team = table.get_item(
            Key={
                'team': team_name
            }
        )

        if team['ResponseMetadata']['HTTPStatusCode'] != 200:
            return {
                'statusCode': 500,
                'body': json_dumps({"message": 'Error retrieving team', "err": "dynamodbError"})
            }

        user_table = dynamodb.Table(os_environ['USER_TABLE'])
        challenge_table = dynamodb.Table(os_environ['CHALLENGES_TABLE'])

        # Get all users
        users = user_table.scan()

        if users['ResponseMetadata']['HTTPStatusCode'] != 200:
            return {
                'statusCode': 500,
                'body': json_dumps({"message": 'Error retrieving users', "err": "dynamodbError"})
            }

        # Create response, if empty return 404
        if 'Item' not in team:
            return {
                "statusCode": 404,
                "body": json_dumps({"message": "Team not found", "err": "notFound"})
            }

        team = team['Item']
        challenges = challenge_table.scan()


        if challenges['ResponseMetadata']['HTTPStatusCode'] != 200:
            return {
                'statusCode': 500,
                'body': json_dumps({"message": 'Error retrieving challenges', "err": "dynamodbError"})
            }

        team['points'] = 0
        for user_id in team['members']:
            user = list(filter(lambda x: x['username'] == user_id, users['Items']))[0]
            for challenge_id in user['challenges_done']:
                t = list(filter(lambda x: x['challenge'] == challenge_id, challenges['Items']))
                if len(t) == 0:
                    continue
                challenge = t[0]
                team['points'] += challenge['points']

        cache[team_name] = {
            "statusCode": 200,
            "body": json_dumps(team, default=int)
        }
        cache_time[team_name] = time()
        return cache[team_name]
    except Exception as error:
        return {
            "statusCode": 500,
            "body": json_dumps({"message": str(error), "err": "internalError"})
        }

