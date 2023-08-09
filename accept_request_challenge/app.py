import boto3, json, os, time
from jwt import decode

def lambda_handler(event, context):
    try:
        token = decode(event['headers']['Authorization'].replace('Bearer ', ''), algorithms=['RS256'],
                           options={"verify_signature": False})

        if 'body' not in event:
            return {
                'statusCode': 400,
                'body': json.dumps({"message": 'Missing body'})
            }
        body = json.loads(event['body'])

        dynamodb = boto3.resource('dynamodb')

        user_table = dynamodb.Table(os.environ['USER_TABLE'])
        user = user_table.get_item(Key={'username': token['cognito:username']})['Item']

        if user['role'] != 'leader' and user['role'] != 'admin':
            return {
                'statusCode': 401,
                'body': json.dumps({"message": 'Unauthorized'})
            }

        username = event['pathParameters']['username']
        # Get the team and check if user is in pending
        response = user_table.get_item(
            Key={
                'username': username
            }
        )

        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            return {
                'statusCode': 500,
                'body': json.dumps({"message": 'Error getting user'})
            }

        if 'Item' not in response:
            return {
                'statusCode': 404,
                'body': json.dumps({"message": 'User not found'})
            }

        if body['challenge'] not in response['Item']['challenges_pending']:
            return {
                'statusCode': 400,
                'body': json.dumps({"message": 'Player didn\'t request this challenge'})
            }

        index = response['Item']['challenges_pending'].index(body['challenge'])

        response = user_table.update_item(
            Key={
                'username': username
            },
            UpdateExpression=f'SET challenges_done = list_append(challenges_done, :challenge) REMOVE challenges_pending[{index}]',
            ExpressionAttributeValues={
                ':challenge': [body['challenge']]
            },
            ReturnValues="UPDATED_NEW"
        )

        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            return {
                'statusCode': 500,
                'body': json.dumps({"message": 'Error accepting challenge'})
            }

        return {
            'statusCode': 200,
            'body': json.dumps({"message": 'Challenge accepted'})
        }
    except Exception as error:
        return {
            "statusCode": 500,
            "body": json.dumps({"message": str(error)})
        }
