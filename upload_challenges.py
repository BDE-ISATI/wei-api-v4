import boto3
import pandas as pd
import uuid
import time
import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('wei_app_db_challenges')

challenges = pd.read_csv('defis.csv')
for chall in challenges.values:
    print(chall)

    if (chall[4] == 'Défi Permanent' or chall[4] == 'Défi permanent'):
        # Start is 11/09/2023 at 12:00:00
        s = '08/09/2025 12:00:00'
        # End is 07/10/2023 at 00:00:00
        e = '05/09/2025 00:00:00'
    elif (chall[4] == 'semaine 1'):
        s = '08/09/2025 12:00:00'
        e = '14/09/2025 23:59:59'
    elif (chall[4] == 'semaine 1,2'):
        s = '08/09/2025 12:00:00'
        e = '21/09/2025 23:59:59'
    elif (chall[4] == 'semaine 2'):
        s = '15/09/2025 00:00:00'
        e = '21/09/2025 23:59:59'
    elif (chall[4] == 'semaine 2,3'):
        s = '15/09/2025 00:00:00'
        e = '24/09/2025 23:59:59'
    elif (chall[4] == 'semaine 3'):
        s = '22/09/2025 00:00:00'
        e = '28/09/2025 23:59:59'
    elif (chall[4] == 'semaine 3,4'):
        s = '22/09/2025 00:00:00'
        e = '05/10/2025 23:59:59'
    elif (chall[4] == 'semaine 4'):
        s = '29/09/2025 00:00:00'
        e = '05/10/2025 23:59:59'
    else:
        s = '08/09/2025 12:00:00'
        e = '05/10/2025 00:00:00'

    start = int(time.mktime(datetime.datetime.strptime(s, "%d/%m/%Y %H:%M:%S").timetuple()))
    end = int(time.mktime(datetime.datetime.strptime(e, "%d/%m/%Y %H:%M:%S").timetuple()))

    response = table.put_item(
        Item={
            'challenge': str(uuid.uuid1()),
            'name': chall[0],
            'description': chall[1],
            'picture_id': '',
            'points': int(chall[2]),
            'start': int(start),
            'end': int(end),
            'max_count': 1
        }
    )

    print(response)
