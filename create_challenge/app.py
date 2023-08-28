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

        # Challenge data
        name = body['name']
        description = body['description']
        picture_id = body['picture_id'] if 'picture_id' in body else ''
        points = body['points']
        if points < 0:
            return {
                'statusCode': 400,
                'body': json.dumps(
                    {"message": 'points must be greater than 0', "err": "invalidValue", "field": "points"}),
                'headers': {
                    'Access-Control-Allow-Origin': '*'
                }
            }
        start = body['start']
        end = body['end']
        max_count = body['max_count'] if 'max_count' in body else 1
        if max_count < 1:
            return {
                'statusCode': 400,
                'body': json.dumps(
                    {"message": 'max_count must be greater than 0', "err": "invalidValue", "field": "max_count"}),
                'headers': {
                    'Access-Control-Allow-Origin': '*'
                }
            }

        challenge_table = dynamodb.Table(os.environ['CHALLENGES_TABLE'])
        challenge_id = parse.unquote(event['pathParameters']['challenge'])
        if not re.match(r'^[A-Za-z_\-0-9.]+$', challenge_id):
            return {
                'statusCode': 400,
                'body': json.dumps({"message": 'Invalid challenge id', "err": "invalidValue", "field": "challenge"}),
                'headers': {
                    'Access-Control-Allow-Origin': '*'
                }
            }

        response = challenge_table.put_item(
            Item={
                'challenge': challenge_id,
                'name': name,
                'description': description,
                'picture_id': picture_id,
                'points': points,
                'start': start,
                'end': end,
                'max_count': max_count
            },
            ConditionExpression='attribute_not_exists(challenge)'
        )

        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            return {
                'statusCode': 500,
                'body': json.dumps({"message": 'Error creating challenge', "err": "dynamodbError"}),
                'headers': {
                    'Access-Control-Allow-Origin': '*'
                }
            }

        return {
            'statusCode': 200,
            'body': json.dumps({"message": 'Challenge created successfully'}),
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
