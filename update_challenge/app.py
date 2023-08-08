import boto3, json, os, jwt


def lambda_handler(event, context):
    try:
        token = jwt.decode(event['headers']['Authorization'].replace('Bearer ', ''), algorithms=['RS256'],
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

        if user['role'] != 'admin' and user['role'] != 'leader':
            return {
                'statusCode': 401,
                'body': json.dumps({"message": 'Unauthorized'})
            }

        challenge_table = dynamodb.Table(os.environ['CHALLENGES_TABLE'])
        challenge_id = event['pathParameters']['challenge']

        response = challenge_table.get_item(Key={'challenge': challenge_id})
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'body': json.dumps({"message": 'Challenge not found'})
            }

        name = body['name'] if 'name' in body else ''
        description = body['description'] if 'description' in body else ''
        points = body['points'] if 'points' in body else 0
        if points < 0:
            return {
                'statusCode': 400,
                'body': json.dumps({"message": 'points must be greater than 0'})
            }
        start = body['start'] if 'start' in body else ''
        end = body['end'] if 'end' in body else ''
        max_count = body['max_count'] if 'max_count' in body else 0
        if max_count < 0:
            return {
                'statusCode': 400,
                'body': json.dumps({"message": 'max_count must be greater than 0'})
            }

        success = True
        status = {}
        if name != '':
            response = challenge_table.update_item(
                Key={
                    'challenge': challenge_id
                },
                UpdateExpression="set #n=:n",  # Name is a reserved word in DynamoDB
                ExpressionAttributeNames={
                    '#n': 'name'
                },
                ExpressionAttributeValues={
                    ':n': name
                },
                ReturnValues="UPDATED_NEW"
            )
            success = success and response['ResponseMetadata']['HTTPStatusCode'] == 200
            if not success:
                status['name'] = 'Failed to update name'
            else:
                status['name'] = 'Name updated successfully'

        if description != '':
            response = challenge_table.update_item(
                Key={
                    'challenge': challenge_id
                },
                UpdateExpression="set description=:d",
                ExpressionAttributeValues={
                    ':d': description
                },
                ReturnValues="UPDATED_NEW"
            )
            success = success and response['ResponseMetadata']['HTTPStatusCode'] == 200
            if not success:
                status['description'] = 'Failed to update description'
            else:
                status['description'] = 'Description updated successfully'

        if points != 0:
            response = challenge_table.update_item(
                Key={
                    'challenge': challenge_id
                },
                UpdateExpression="set points=:p",
                ExpressionAttributeValues={
                    ':p': points
                },
                ReturnValues="UPDATED_NEW"
            )
            success = success and response['ResponseMetadata']['HTTPStatusCode'] == 200
            if not success:
                status['points'] = 'Failed to update points'
            else:
                status['points'] = 'Points updated successfully'

        if start != '':
            response = challenge_table.update_item(
                Key={
                    'challenge': challenge_id
                },
                UpdateExpression="set start=:s",
                ExpressionAttributeValues={
                    ':s': start
                },
                ReturnValues="UPDATED_NEW"
            )
            success = success and response['ResponseMetadata']['HTTPStatusCode'] == 200
            if not success:
                status['start'] = 'Failed to update start'
            else:
                status['start'] = 'Start updated successfully'

        if end != '':
            response = challenge_table.update_item(
                Key={
                    'challenge': challenge_id
                },
                UpdateExpression="set end=:e",
                ExpressionAttributeValues={
                    ':e': end
                },
                ReturnValues="UPDATED_NEW"
            )
            success = success and response['ResponseMetadata']['HTTPStatusCode'] == 200
            if not success:
                status['end'] = 'Failed to update end'
            else:
                status['end'] = 'End updated successfully'

        if max_count != 0:
            response = challenge_table.update_item(
                Key={
                    'challenge': challenge_id
                },
                UpdateExpression="set max_count=:m",
                ExpressionAttributeValues={
                    ':m': max_count
                },
                ReturnValues="UPDATED_NEW"
            )
            success = success and response['ResponseMetadata']['HTTPStatusCode'] == 200
            if not success:
                status['max_count'] = 'Failed to update max_count'
            else:
                status['max_count'] = 'Max count updated successfully'

        if not success:
            return {
                'statusCode': 500,
                'body': json.dumps({"message": 'Error updating challenge', "status": status})
            }

        return {
            'statusCode': 200,
            'body': json.dumps({"message": 'Challenge updated successfully'})
        }
    except Exception as error:
        return {
            "statusCode": 500,
            "body": json.dumps({"message": str(error)})
        }
