import boto3, json, os, jwt


def lambda_handler(event, context):
    try:
        token = jwt.decode(event['headers']['Authorization'].replace('Bearer ', ''), algorithms=['RS256'],
                           options={"verify_signature": False})

        dynamodb = boto3.resource('dynamodb')
        teams_table = dynamodb.Table(os.environ['TEAMS_TABLE'])
        team_name = event['pathParameters']['team']

        if teams_table.get_item(Key={'team': team_name}).get('Item'):
            return {
                'statusCode': 400,
                'body': json.dumps({"message": 'Team already exists'})
            }

        user_table = dynamodb.Table(os.environ['USER_TABLE'])
        user = user_table.get_item(Key={'username': token['cognito:username']})['Item']

        if user['role'] != 'admin' and user['role'] != 'leader':
            return {
                'statusCode': 401,
                'body': json.dumps({"message": 'Unauthorized'})
            }

        if event['body'] is not None:
            body = json.loads(event['body'])
            display_name = body['display_name'] if 'display_name' in body else ''
            picture_id = body['picture_id'] if 'picture_id' in body else ''
        else:
            display_name = ''
            picture_id = ''

        response = teams_table.put_item(Item={
            'team': team_name,
            'display_name': display_name,
            'picture_id': picture_id,
            'members': [],
            'pending': []
        })

        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            return {
                'statusCode': 500,
                'body': json.dumps({"message": 'Error creating team'})
            }

        return {
            'statusCode': 200,
            'body': json.dumps({"message": 'Team created successfully'})
        }
    except Exception as error:
        return {
            "statusCode": 500,
            "body": json.dumps({"message": str(error)})
        }
