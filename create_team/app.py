import boto3
import json
import os
import jwt
from urllib import parse
import re

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

        team_name = parse.unquote(event['pathParameters']['team'])
        if not re.match(r'^[A-Za-z_\-0-9.]+$', team_name):
            return {
                'statusCode': 400,
                'body': json.dumps({"message": 'Invalid challenge id', "err": "invalidValue", "field": "team_name"}),
                'headers': {
                    'Access-Control-Allow-Origin': '*'
                }
            }

        display_name = body['display_name']
        picture_id = body['picture_id']

        response = teams_table.put_item(
            Item={
                'team': team_name,
                'display_name': display_name,
                'picture_id': picture_id,
                'members': [],
                'pending': []
            },
            ConditionExpression='attribute_not_exists(team)'
        )

        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            return {
                'statusCode': 500,
                'body': json.dumps({"message": 'Error creating team', "err": "dynamodbError"}),
                'headers': {
                    'Access-Control-Allow-Origin': '*'
                }
            }

        return {
            'statusCode': 200,
            'body': json.dumps({"message": 'Team created successfully'}),
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
