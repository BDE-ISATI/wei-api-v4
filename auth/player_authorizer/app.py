import jwt, time

def lambda_handler(event, context):
    token = event['authorizationToken']
    token = token.replace('Bearer ', '')

    try:
        decoded = jwt.decode(token, algorithms=['RS256'], options={"verify_signature": False})

        if 'Player' not in decoded['cognito:groups']:
            raise Exception('Unauthorized')

        if time.time() > decoded['exp']:
            raise Exception('Token expired')
        
        principalId = decoded['sub']
        policyDocument = {
            'Version': '2012-10-17',
            'Statement': [
                {
                    'Action': 'execute-api:Invoke',
                    'Effect': 'Allow',
                    'Resource': event['methodArn']
                }
            ]
        }
    except Exception as error:
        print(error)
        principalId = 'unauthorized'
        policyDocument = {
            'Version': '2012-10-17',
            'Statement': [
                {
                    'Action': 'execute-api:Invoke',
                    'Effect': 'Deny',
                    'Resource': event['methodArn']
                }
            ]
        }

    return {
        'principalId': principalId,
        'policyDocument': policyDocument
    }