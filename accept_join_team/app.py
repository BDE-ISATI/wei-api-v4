import boto3
import json
import os
import jwt
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

        body = json.loads(event['body'])

        dynamodb = boto3.resource('dynamodb')

        teams_table = dynamodb.Table(os.environ['TEAMS_TABLE'])
        team_id = parse.unquote(event['pathParameters']['team'])

        # Get the team and check if user is in pending
        team = teams_table.get_item(
            Key={
                'team': team_id
            }
        )

        if team['ResponseMetadata']['HTTPStatusCode'] != 200:
            return {
                'statusCode': 500,
                'body': json.dumps({"message": 'Error getting team', "err": "dynamodbError"}),
                'headers': {
                    'Access-Control-Allow-Origin': '*'
                }
            }

        if 'Item' not in team:
            return {
                'statusCode': 404,
                'body': json.dumps({"message": 'Team not found', "err": "notFound"}),
                'headers': {
                    'Access-Control-Allow-Origin': '*'
                }
            }

        team = team['Item']
        username = body['username']

        if username not in team['pending']:
            return {
                'statusCode': 400,
                'body': json.dumps({"message": 'Player not in pending', "err": "notInPending"}),
                'headers': {
                    'Access-Control-Allow-Origin': '*'
                }
            }

        index = team['pending'].index(username)

        response = teams_table.update_item(
            Key={
                'team': team_id
            },
            UpdateExpression=f'SET members = list_append(members, :player) REMOVE pending[{index}]',
            ExpressionAttributeValues={
                ':player': [username]
            },
            ReturnValues="UPDATED_NEW"
        )

        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            return {
                'statusCode': 500,
                'body': json.dumps({"message": 'Error joining team', "err": "dynamodbError"}),
                'headers': {
                    'Access-Control-Allow-Origin': '*'
                }
            }

        return {
            'statusCode': 200,
            'body': json.dumps({"message": 'Team joined successfully'}),
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
