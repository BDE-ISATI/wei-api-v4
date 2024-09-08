import boto3
import json
import os
import jwt

def lambda_handler(event, context):
    try:
        token = jwt.decode(event['headers']['Authorization'].replace('Bearer ', ''), algorithms=['RS256'],
                       options={"verify_signature": False})

        body = json.loads(event['body'])

        if 'show' not in body and 'picture_id' not in body and 'display_name' not in body and 'anecdote' not in body and "scoreAnecdote" not in body:
            return {
                'statusCode': 400,
                'body': json.dumps({"message": 'No body provided', "err": "emptyBody"}),
                'headers': {
                    'Access-Control-Allow-Origin': '*'
                }
            }

        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(os.environ['USER_TABLE'])

        username = token['cognito:username']

        show = body['show'] if 'show' in body else None
        picture_id = body['picture_id'] if 'picture_id' in body else None
        display_name = body['display_name'] if 'display_name' in body else None
        anecdote = body['anecdote'] if 'anecdote' in body else None
        scoreAnecdote = body['scoreAnecdote'] if 'scoreAnecdote' in body else None

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

        if anecdote != None:
            if len(values) > 0:
                update_expression += ", "
            update_expression += "anecdote = :anecdote"
            values[":anecdote"] = anecdote

        if scoreAnecdote != None:
            if len(values) > 0:
                update_expression += ", "
            update_expression += "scoreAnecdote = :scoreAnecdote"
            values[":scoreAnecdote"] = scoreAnecdote

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
                'body': json.dumps({"message": 'Error updating user', "err": "dynamodbError"}),
                'headers': {
                    'Access-Control-Allow-Origin': '*'
                }
            }

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "User updated"}),
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
