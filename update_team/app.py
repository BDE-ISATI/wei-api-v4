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

        if 'display_name' not in body and 'picture_id' not in body:
            return {
                'statusCode': 400,
                'body': json.dumps({"message": 'Missing body', "err": "emptyBody"}),
                'headers': {
                    'Access-Control-Allow-Origin': '*'
                }
            }

        dynamodb = boto3.resource('dynamodb')

        teams_table = dynamodb.Table(os.environ['TEAMS_TABLE'])
        team_name = parse.unquote(event['pathParameters']['team'])

        display_name = body['display_name'] if 'display_name' in body else ''
        picture_id = body['picture_id'] if 'picture_id' in body else ''

        update_values = {}
        update_expression = "set "
        if display_name != '':
            update_expression += "display_name=:d"
            update_values[':d'] = display_name

        if picture_id != '':
            if len(update_values) > 0:
                update_expression += ", "
            update_expression += "picture_id=:p"
            update_values[':p'] = picture_id

        update_values[':t'] = team_name
        response = teams_table.update_item(
            Key={
                'team': team_name
            },
            UpdateExpression=update_expression,
            ConditionExpression="team=:t",
            ExpressionAttributeValues=update_values,
            ReturnValues="UPDATED_NEW"
        )

        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            return {
                'statusCode': 500,
                'body': json.dumps({"message": 'Error updating team', "err": "dynamodbError"}),
                'headers': {
                    'Access-Control-Allow-Origin': '*'
                }
            }

        return {
            'statusCode': 200,
            'body': json.dumps({"message": 'Team updated successfully'}),
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
