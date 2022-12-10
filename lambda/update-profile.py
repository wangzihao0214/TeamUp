import json
import boto3

def update_profile(user_id, data):
    data = json.loads(data)
    update_expression = 'set {}'.format(','.join(f'{key}=:{key[0]}' for key in data))
    expression_attribute_values = {f':{key[0]}': val for key, val in data.items()}
    print(update_expression)
    print(expression_attribute_values)
    # Update users table
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table("users")
    table.update_item(
        Key={'userId':user_id},
        UpdateExpression=update_expression,
        ExpressionAttributeValues=expression_attribute_values,
        ReturnValues="UPDATED_NEW"
    )

def lambda_handler(event, context):
    user_id = event['queryStringParameters']['user-id']
    data = event['queryStringParameters']['data']
    update_profile(user_id, data)
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,GET'
        },
        'body': 'Profile updated'
    }
