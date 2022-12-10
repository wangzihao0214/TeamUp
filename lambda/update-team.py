import json
import boto3

def update_team(team_id, data):
    data = json.loads(data)
    update_expression = 'set {}'.format(','.join(f'{key}=:{key[0]}' for key in data))
    expression_attribute_values = {f':{key[0]}': val for key, val in data.items()}
    print(update_expression)
    print(expression_attribute_values)
    # Update users table
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table("teams")
    table.update_item(
        Key={'team-id': team_id},
        UpdateExpression=update_expression,
        ExpressionAttributeValues=expression_attribute_values,
        ReturnValues="UPDATED_NEW"
    )

def lambda_handler(event, context):
    team_id = event['queryStringParameters']['team-id']
    data = event['queryStringParameters']['data']
    update_team(team_id, data)
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,GET'
        },
        'body': 'Profile updated'
    }
