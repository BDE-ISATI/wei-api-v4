import boto3
from jwt import decode
from json import dumps as json_dumps
from json import loads as json_loads
from os import environ as os_environ
from urllib import parse

def lambda_handler(event, context):
    try:
        token = decode(event['headers']['Authorization'].replace('Bearer ', ''), algorithms=['RS256'],
                       options={"verify_signature": False})

        if 'cognito:groups' in token and 'Admin' in token['cognito:groups']:
            return {
                'statusCode': 401,
                'body': json_dumps({"message": 'You must be a player', "err": "unauthorized"}),
                'headers': {
                    'Access-Control-Allow-Origin': '*'
                }
            }

        if 'body' not in event:
            return {
                'statusCode': 400,
                'body': json_dumps({"message": 'Missing body', "err": "emptyBody"}),
                'headers': {
                    'Access-Control-Allow-Origin': '*'
                }
            }

        dynamodb = boto3.resource('dynamodb')

        user_table = dynamodb.Table(os_environ['USER_TABLE'])

        username = token['cognito:username']
        challenge_id = parse.unquote(event['pathParameters']['challenge'])

        # Get the team and check if user is in pending
        user = user_table.get_item(
            Key={
                'username': username
            }
        )

        if user['ResponseMetadata']['HTTPStatusCode'] != 200:
            return {
                'statusCode': 500,
                'body': json_dumps({"message": 'Error getting user', "err": "dynamodbError"}),
                'headers': {
                    'Access-Control-Allow-Origin': '*'
                }
            }

        if 'Item' not in user:
            return {
                'statusCode': 404,
                'body': json_dumps({"message": 'User not found', "err": "notFound"}),
                'headers': {
                    'Access-Control-Allow-Origin': '*'
                }
            }

        if challenge_id not in user['Item']['challenges_to_do']:
            return {
                'statusCode': 400,
                'body': json_dumps({"message": 'Challenge not in todo', "err": "notInTodo"}),
                'headers': {
                    'Access-Control-Allow-Origin': '*'
                }
            }

        index = user['Item']['challenges_to_do'].index(challenge_id)

        response = user_table.update_item(
            Key={
                'username': username
            },
            UpdateExpression=f'REMOVE challenges_to_do[{index}]',
            ReturnValues="UPDATED_NEW"
        )

        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            return {
                'statusCode': 500,
                'body': json_dumps({"message": 'Error removing todo challenge', "err": "dynamodbError"}),
                'headers': {
                    'Access-Control-Allow-Origin': '*'
                }
            }

        return {
            'statusCode': 200,
            'body': json_dumps({"message": 'Challenge removed from todo'}),
            'headers': {
                'Access-Control-Allow-Origin': '*'
            }
        }
    except Exception as error:
        return {
            "statusCode": 500,
            "body": json_dumps({"message": str(error), "err": "internalError"}),
            'headers': {
                'Access-Control-Allow-Origin': '*'
            }
        }
