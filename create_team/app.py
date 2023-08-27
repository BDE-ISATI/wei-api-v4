import boto3
from jwt import decode
from json import loads as json_loads
from json import dumps as json_dumps
from os import environ as os_environ
from urllib import parse

def lambda_handler(event, context):
    try:
        token = decode(event['headers']['Authorization'].replace('Bearer ', ''), algorithms=['RS256'],
                       options={"verify_signature": False})

        if 'cognito:groups' not in token or 'Admin' not in token['cognito:groups']:
            return {
                'statusCode': 401,
                'body': json_dumps({"message": 'Unauthorized', "err": "unauthorized"}),
                'headers': {
                    'Access-Control-Allow-Origin': '*'
                }
            }

        body = json_loads(event['body'])

        dynamodb = boto3.resource('dynamodb')

        teams_table = dynamodb.Table(os_environ['TEAMS_TABLE'])

        team_name = parse.unquote(event['pathParameters']['team'])
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
                'body': json_dumps({"message": 'Error creating team', "err": "dynamodbError"}),
                'headers': {
                    'Access-Control-Allow-Origin': '*'
                }
            }

        return {
            'statusCode': 200,
            'body': json_dumps({"message": 'Team created successfully'}),
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
