import json
import boto3

dynamodb = boto3.resource('dynamodb')
user_table = dynamodb.Table("users")
artist_table = dynamodb.Table("artists")
team_table = dynamodb.Table("teams")
event_table = dynamodb.Table("events")
base_url = 'http://teamup-frontend.s3-website-us-east-1.amazonaws.com/team.html?id='

def get_user(id):
    
    user = user_table.get_item(
        Key={'userId': id}  
    )
    user = user['Item']
    print(user)
    
    artists = []
    if 'topArtists' in user:
        for artist_id in user['topArtists']:
            artist = artist_table.get_item(
                Key={'artistId': artist_id}    
            )
            artist = artist['Item']
            temp = {}
            temp["name"] = artist['artistName']
            temp["image"] = artist['imageUrl']
            try:
                temp["info"] = artist['genres'][0].capitalize()
            except:
                temp["info"] = "NA"
            temp["url"] = artist['artistUrl']
            artists.append(temp)
    user['topArtists'] = artists
    
    teams = []
    if 'teams' in user:
        for team_id in user['teams']:
            team = team_table.get_item(
                Key={'team-id': team_id}
            )
            if 'Item' not in team.keys():
                continue
            team = team['Item']
            temp = {}
            temp['name'] = team['team name']
            temp['team_id'] = team['team-id']
            temp['event_id'] = team['event-id']
            event = event_table.get_item(
                Key={'event-id': team['event-id']}    
            )
            if 'Item' not in event.keys():
                continue
            event = event['Item']
            print(event)
            try:
                temp['image'] = event['image']
            except:
                temp['image'] = ''
            temp['info'] = event['name']
            temp['url'] = base_url + temp['team_id']
            teams.append(temp)
        print(teams)
    user['teams'] = teams[::-1]

    return user

def lambda_handler(event, context):
    user_id = event['pathParameters']['user-id']
    result = get_user(user_id)
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,GET'
        },
        'body': json.dumps(result)
    }
