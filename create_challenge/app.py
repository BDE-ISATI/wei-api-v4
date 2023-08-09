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

        name = body['name']
        description = body['description']
        picture_id = body['picture_id'] if 'picture_id' in body else ''
        points = body['points']
        if points < 0:
            return {
                'statusCode': 400,
                'body': json.dumps({"message": 'points must be greater than 0'})
            }
        start = body['start']
        end = body['end']
        max_count = body['max_count'] if 'max_count' in body else 1
        if max_count < 1:
            return {
                'statusCode': 400,
                'body': json.dumps({"message": 'max_count must be greater than 0'})
            }

        challenge_table = dynamodb.Table(os.environ['CHALLENGES_TABLE'])
        challenge_id = event['pathParameters']['challenge']

        response = challenge_table.put_item(
            Item={
                'challenge': challenge_id,
                'name': name,
                'description': description,
                'picture_id': picture_id,
                'points': points,
                'start': start,
                'end': end,
                'max_count': max_count
            },
            ConditionExpression='attribute_not_exists(challenge)'
        )

        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            return {
                'statusCode': 500,
                'body': json.dumps({"message": 'Error creating challenge'})
            }

        return {
            'statusCode': 200,
            'body': json.dumps({"message": 'Challenge created successfully'})
        }
    except Exception as error:
        return {
            "statusCode": 500,
            "body": json.dumps({"message": str(error)})
        }
