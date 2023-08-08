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

        teams_table = dynamodb.Table(os.environ['TEAMS_TABLE'])
        team_name = event['pathParameters']['team']

        display_name = body['display_name'] if 'display_name' in body else ''
        picture_id = body['picture_id'] if 'picture_id' in body else ''

        success = True
        status = {}
        if display_name != '':
            response = teams_table.update_item(
                Key={
                    'team': team_name
                },
                UpdateExpression="set display_name=:d",
                ExpressionAttributeValues={
                    ':d': display_name
                },
                ReturnValues="UPDATED_NEW"
            )
            success = success and response['ResponseMetadata']['HTTPStatusCode'] == 200
            if not success:
                status['display_name'] = 'Failed to update display name'
            else:
                status['display_name'] = 'Display name updated successfully'


        if picture_id != '':
            response = teams_table.update_item(
                Key={
                    'team': team_name
                },
                UpdateExpression="set picture_id=:p",
                ExpressionAttributeValues={
                    ':p': picture_id
                },
                ReturnValues="UPDATED_NEW"
            )
            success = success and response['ResponseMetadata']['HTTPStatusCode'] == 200
            if not success:
                status['picture_id'] = 'Failed to update picture id'
            else:
                status['picture_id'] = 'Picture id updated successfully'


        if not success:
            return {
                'statusCode': 500,
                'body': json.dumps({"message": 'Error updating team', "status": status})
            }

        return {
            'statusCode': 200,
            'body': json.dumps({"message": 'Team updated successfully'})
        }
    except Exception as error:
        return {
            "statusCode": 500,
            "body": json.dumps({"message": str(error)})
        }
