import requests
import json
import boto3

dynamodb = boto3.resource('dynamodb')
user_table = dynamodb.Table("users")
artist_table = dynamodb.Table("artists")

def get_spotify_profile(token):
    # Get spotify profile
    headers = {'Authorization': 'Bearer ' + token}
    rsp = requests.get(url='https://api.spotify.com/v1/me', headers=headers)
    rsp = json.loads(rsp.text)
    dic = {}
    dic['user-id'] = rsp['id']
    dic['user-name'] = rsp['display_name']
    if len(rsp['images']):
        dic['image'] = rsp['images'][0]['url']
    else:
        dic['image'] = ''
    
    # Get top artists
    rsp = requests.get(url='https://api.spotify.com/v1/me/following?type=artist', headers=headers)
    rsp = json.loads(rsp.text)
    dic['top-artists'] = []
    
    # Update artists table
    for item in rsp['artists']['items']:
        id = item['id']
        name = item['name']
        image = item['images'][0]['url']
        genres = item['genres']
        url = item['external_urls']['spotify']
        dic['top-artists'].append(id)
        artist_table.update_item(
            Key={'artistId': id},
            UpdateExpression='set artistName=:n, imageUrl=:i, genres=:g, artistUrl=:u',
            ExpressionAttributeValues={
                ':n': name,
                ':i': image,
                ':g': genres,
                ':u': url
            },
            ReturnValues="UPDATED_NEW"
        )
    
    # Update users table
    user_table.update_item(
        Key={'userId': dic['user-id']},
        UpdateExpression='set userName=:n, imageUrl=:i, topArtists=:a',
        ExpressionAttributeValues={
            ':n': dic['user-name'],
            ':i': dic['image'],
            ':a': dic['top-artists']
        },
        ReturnValues="UPDATED_NEW"
    )
    
    print(dic)
    return {'id': dic['user-id']}


def lambda_handler(event, context):
    try: 
        token = event['queryStringParameters']['token']
    except:
        return {
            'statusCode': 400,
            'headers': {
                'Access-Control-Allow-Headers': '*',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,GET'
            },
            'body': json.dumps('Access token is required')
        }
        
    result = get_spotify_profile(event['queryStringParameters']['token'])
    print(result)
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,GET'
        },
        'body': json.dumps(result)
    }