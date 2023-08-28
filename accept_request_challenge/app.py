import boto3
import json
import os
import jwt
import time
from urllib import parse


def lambda_handler(event, context):
    try:
        token = jwt.decode(event['headers']['Authorization'].replace('Bearer ', ''), algorithms=['RS256'],
                       options={"verify_signature": False})

        if 'cognito:groups' not in token or 'Admin' not in token['cognito:groups']:
            return {
                'statusCode': 401,
                'body': json.dumps({"message": 'Unauthorized', "err": "unauthorized"}),
                'headers': {
                    'Access-Control-Allow-Origin': '*'
                }
            }

        if 'body' not in event:
            return {
                'statusCode': 400,
                'body': json.dumps({"message": 'Missing body', "err": "emptyBody"}),
                'headers': {
                    'Access-Control-Allow-Origin': '*'
                }
            }

        body = json.loads(event['body'])

        dynamodb = boto3.resource('dynamodb')

        user_table = dynamodb.Table(os.environ['USER_TABLE'])
        username = parse.unquote(event['pathParameters']['username'])
        # Get the team and check if user is in pending
        user = user_table.get_item(
            Key={
                'username': username
            }
        )

        if user['ResponseMetadata']['HTTPStatusCode'] != 200:
            return {
                'statusCode': 500,
                'body': json.dumps({"message": 'Error getting user', "err": "dynamodbError"}),
                'headers': {
                    'Access-Control-Allow-Origin': '*'
                }
            }

        if 'Item' not in user:
            return {
                'statusCode': 404,
                'body': json.dumps({"message": 'User not found', "err": "notFound"}),
                'headers': {
                    'Access-Control-Allow-Origin': '*'
                }
            }

        user = user['Item']
        challenge_id = body['challenge']

        if challenge_id not in user['challenges_pending']:
            return {
                'statusCode': 400,
                'body': json.dumps({"message": 'Player didn\'t request this challenge', "err": "notInPending"}),
                'headers': {
                    'Access-Control-Allow-Origin': '*'
                }
            }

        index = user['challenges_pending'].index(challenge_id)

        if 'challenges_times' not in user:
            user['challenges_times'] = {}

        if challenge_id not in user['challenges_times']:
            user['challenges_times'][challenge_id] = int(time.time())

        response = user_table.update_item(
            Key={
                'username': username
            },
            UpdateExpression=f'SET challenges_done = list_append(challenges_done, :challenge), challenges_times = :times REMOVE challenges_pending[{index}]',
            ExpressionAttributeValues={
                ':challenge': [challenge_id],
                ':times': user['challenges_times']
            },
            ReturnValues="UPDATED_NEW"
        )

        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            return {
                'statusCode': 500,
                'body': json.dumps({"message": 'Error accepting challenge', "err": "dynamodbError"}),
                'headers': {
                    'Access-Control-Allow-Origin': '*'
                }
            }

        return {
            'statusCode': 200,
            'body': json.dumps({"message": 'Challenge accepted'}),
            'headers': {
                'Access-Control-Allow-Origin': '*'
            }
        }
    except Exception as error:
        return {
            "statusCode": 500,
            "body": json.dumps({"message": str(error), "err": "internalError"}),
            'headers': {
                'Access-Control-Allow-Origin': '*'
            }
        }
