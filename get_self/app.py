import json
import boto3
import os
import tools_layer

def lambda_handler(event, context):
    try:
        token = tools_layer.Token(event['headers']['Authorization'].replace('Bearer ', ''))
        token.decode()

        if not token.is_valid():
            raise Exception('Invalid token.')

        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(os.environ['USER_TABLE'])

        # Get user from event.pathParameters.username
        response = table.get_item(
            Key={
                'username': token.decoded['username']
            }
        )

        # Create response, if empty return 404
        if 'Item' not in response:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "User not found"})
            }

        return {
            "statusCode": 200,
            "body": json.dumps(response['Item'])
        }
    except Exception as error:
        return {
            "statusCode": 404,
            "body": json.dumps({"error": str(error)})
        }

