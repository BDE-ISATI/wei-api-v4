import boto3, json, os, jwt


def lambda_handler(event, context):
    try:
        token = jwt.decode(event['headers']['Authorization'].replace('Bearer ', ''), algorithms=['RS256'],
                           options={"verify_signature": False})

        if 'cognito:groups' not in token or 'Admin' not in token['cognito:groups']:
            return {
                'statusCode': 401,
                'body': json.dumps({"message": 'Unauthorized'})
            }

        body = json.loads(event['body'])

        dynamodb = boto3.resource('dynamodb')

        teams_table = dynamodb.Table(os.environ['TEAMS_TABLE'])
        team_name = event['pathParameters']['team']

        # Get the team and check if user is in pending
        response = teams_table.get_item(
            Key={
                'team': team_name
            }
        )

        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            return {
                'statusCode': 500,
                'body': json.dumps({"message": 'Error getting team'})
            }

        if 'Item' not in response:
            return {
                'statusCode': 404,
                'body': json.dumps({"message": 'Team not found'})
            }

        if body['username'] not in response['Item']['pending']:
            return {
                'statusCode': 400,
                'body': json.dumps({"message": 'Player not in pending'})
            }

        index = response['Item']['pending'].index(body['username'])

        response = teams_table.update_item(
            Key={
                'team': team_name
            },
            UpdateExpression=f'SET members = list_append(members, :player) REMOVE pending[{index}]',
            ExpressionAttributeValues={
                ':player': [body['username']]
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
