import boto3, json, os, jwt


def lambda_handler(event, context):
    try:
        token = jwt.decode(event['headers']['Authorization'].replace('Bearer ', ''), algorithms=['RS256'],
                           options={"verify_signature": False})

        dynamodb = boto3.resource('dynamodb')

        user_table = dynamodb.Table(os.environ['USER_TABLE'])
        user = user_table.get_item(Key={'username': token['cognito:username']})['Item']

        if user['role'] != 'player':
            return {
                'statusCode': 401,
                'body': json.dumps({"message": 'You must be a player to join a team!'})
            }

        teams_table = dynamodb.Table(os.environ['TEAMS_TABLE'])
        team_name = event['pathParameters']['team']

        response = teams_table.scan(
            FilterExpression='contains(members, :player) OR contains(pending, :player)',
            ExpressionAttributeValues={
                ':player': user['username']
            }
        )

        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            return {
                'statusCode': 500,
                'body': json.dumps({"message": 'Error joining team'})
            }

        if len(response['Items']) > 0:
            return {
                'statusCode': 400,
                'body': json.dumps({"message": 'You are already in a team.'})
            }

        response = teams_table.update_item(
            Key={
                'team': team_name
            },
            UpdateExpression='SET pending = list_append(pending, :player)',
            ExpressionAttributeValues={
                ':player': [user['username']]
            },
            ReturnValues="UPDATED_NEW"
        )

        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            return {
                'statusCode': 500,
                'body': json.dumps({"message": 'Error joining team'})
            }

        return {
            'statusCode': 200,
            'body': json.dumps({"message": 'Team joined successfully'})
        }
    except Exception as error:
        return {
            "statusCode": 500,
            "body": json.dumps({"message": str(error)})
        }
