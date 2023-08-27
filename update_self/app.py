import boto3
from os import environ as os_environ
from jwt import decode
from json import loads as json_loads
from json import dumps as json_dumps

def lambda_handler(event, context):
    try:
        token = decode(event['headers']['Authorization'].replace('Bearer ', ''), algorithms=['RS256'],
                       options={"verify_signature": False})

        body = json_loads(event['body'])

        if 'show' not in body and 'picture_id' not in body and 'display_name' not in body:
            return {
                'statusCode': 400,
                'body': json_dumps({"message": 'No body provided', "err": "emptyBody"}),
                'headers': {
                    'Access-Control-Allow-Origin': '*'
                }
            }

        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(os_environ['USER_TABLE'])

        username = token['cognito:username']

        show = body['show'] if 'show' in body else None
        picture_id = body['picture_id'] if 'picture_id' in body else None
        display_name = body['display_name'] if 'display_name' in body else None

        names = {}
        update_expression = "set "
        values = {}
        if show != None:
            names = {"#s": "show"}
            update_expression += "#s = :s"
            values[":s"] = show

        if picture_id != None:
            if len(values) > 0:
                update_expression += ", "
            update_expression += "picture_id = :picture_id"
            values[":picture_id"] = picture_id

        if display_name != None:
            if len(values) > 0:
                update_expression += ", "
            update_expression += "display_name = :display_name"
            values[":display_name"] = display_name

        if names != {}:
            response = table.update_item(
                Key={
                    'username': username
                },
                ExpressionAttributeNames=names,
                UpdateExpression=update_expression,
                ExpressionAttributeValues=values,
                ReturnValues="UPDATED_NEW"
            )
        else:
            response = table.update_item(
                Key={
                    'username': username
                },
                UpdateExpression=update_expression,
                ExpressionAttributeValues=values,
                ReturnValues="UPDATED_NEW"
            )

        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            return {
                'statusCode': 500,
                'body': json_dumps({"message": 'Error updating user', "err": "dynamodbError"}),
                'headers': {
                    'Access-Control-Allow-Origin': '*'
                }
            }

        return {
            "statusCode": 200,
            "body": json_dumps({"message": "User updated"}),
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
