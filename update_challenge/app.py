import boto3
from json import loads as json_loads
from json import dumps as json_dumps
from jwt import decode
from os import environ as os_environ


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

        if 'name' not in body and 'description' not in body and 'picture_id' not in body and 'points' not in body and 'start' not in body and 'end' not in body and 'max_count' not in body:
            return {
                'statusCode': 400,
                'body': json_dumps({"message": 'Missing parameters', "err": "emptyBody"}),
                'headers': {
                    'Access-Control-Allow-Origin': '*'
                }
            }

        dynamodb = boto3.resource('dynamodb')

        challenge_table = dynamodb.Table(os_environ['CHALLENGES_TABLE'])
        challenge_id = event['pathParameters']['challenge']

        name = body['name'] if 'name' in body else ''
        description = body['description'] if 'description' in body else ''
        picture_id = body['picture_id'] if 'picture_id' in body else ''
        points = body['points'] if 'points' in body else 0
        if points < 0:
            return {
                'statusCode': 400,
                'body': json_dumps(
                    {"message": 'points must be greater than 0', "err": "invalidValue", "field": "points"}),
                'headers': {
                    'Access-Control-Allow-Origin': '*'
                }
            }

        start = body['start'] if 'start' in body else ''
        end = body['end'] if 'end' in body else ''

        max_count = body['max_count'] if 'max_count' in body else 0
        if max_count < 0:
            return {
                'statusCode': 400,
                'body': json_dumps(
                    {"message": 'max_count must be greater than 0', "err": "invalidValue", "field": "max_count"}),
                'headers': {
                    'Access-Control-Allow-Origin': '*'
                }
            }

        names = {}
        update_expression = "set "
        values = {}
        if name != '':
            update_expression += "#n=:n"
            names['#n'] = 'name'
            values[':n'] = name

        if description != '':
            if len(values) > 0:
                update_expression += ", "
            update_expression += "description=:d"
            values[':d'] = description

        if picture_id != '':
            if len(values) > 0:
                update_expression += ", "
            update_expression += "picture_id=:p"
            values[':p'] = picture_id

        if points != 0:
            if len(values) > 0:
                update_expression += ", "
            update_expression += "points=:p"
            values[':p'] = points

        if start != '':
            if len(values) > 0:
                update_expression += ", "
            names['#s'] = 'start'
            update_expression += "#s=:s"
            values[':s'] = start

        if end != '':
            if len(values) > 0:
                update_expression += ", "
            names['#e'] = 'end'
            update_expression += "#e=:e"
            values[':e'] = end

        if max_count != 0:
            if len(values) > 0:
                update_expression += ", "
            update_expression += "max_count=:m"
            values[':m'] = max_count

        values[':c'] = challenge_id
        if names != {}:
            response = challenge_table.update_item(
                Key={
                    'challenge': challenge_id
                },
                UpdateExpression=update_expression,
                ConditionExpression="challenge = :c",
                ExpressionAttributeNames=names,
                ExpressionAttributeValues=values,
                ReturnValues="UPDATED_NEW"
            )
        else:
            response = challenge_table.update_item(
                Key={
                    'challenge': challenge_id
                },
                UpdateExpression=update_expression,
                ConditionExpression="challenge = :c",
                ExpressionAttributeValues=values,
                ReturnValues="UPDATED_NEW"
            )

        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            return {
                'statusCode': 500,
                'body': json_dumps({"message": 'Error updating challenge', "err": "dynamodbError"}),
                'headers': {
                    'Access-Control-Allow-Origin': '*'
                }
            }

        return {
            'statusCode': 200,
            'body': json_dumps({"message": 'Challenge updated successfully'}),
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
