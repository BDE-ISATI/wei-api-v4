import json, os, boto3, jwt


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
                'body': json.dumps({"message": 'You must be a player to request a challenge!'})
            }

        # Get challenge
        challenge_table = dynamodb.Table(os.environ['CHALLENGES_TABLE'])
        challenge = challenge_table.get_item(Key={'challenge': event['pathParameters']['challenge']})['Item']

        if not challenge:
            return {
                'statusCode': 404,
                'body': json.dumps({"message": 'Challenge not found'})
            }

        if user['challenges_done'].count(challenge['challenge']) + user['challenges_pending'].count(challenge['challenge']) >= challenge['max_count']:
            return {
                'statusCode': 400,
                'body': json.dumps({"message": 'You have already completed this challenge the maximum number of times'})
            }

        # Add the challenge to the user's pending challenges
        user_table.update_item(
            Key={
                'username': user['username']
            },
            UpdateExpression='SET challenges_pending = list_append(challenges_pending, :challenge)',
            ExpressionAttributeValues={
                ':challenge': [challenge['challenge']]
            }
        )

        return {
            'statusCode': 200,
            'body': json.dumps({"message": 'Challenge requested'})
        }

    except Exception as error:
        return {
            "statusCode": 500,
            "body": json.dumps({"message": str(error)})
        }
