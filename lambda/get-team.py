import json
import boto3

dynamodb = boto3.resource('dynamodb')
events_table = dynamodb.Table("events")
teams_table = dynamodb.Table("teams")
users_table = dynamodb.Table("users")


def get_team(team_id):
    teams_table_result = teams_table.get_item(Key={'team-id': team_id})['Item']
    
    team = {}
    team["team name"] = teams_table_result["team name"]
    try:
        team["description"] = teams_table_result["description"]
    except:
        team["description"] = "No description yet."
    
    event = {}
    event_id = teams_table_result["event-id"]
    events_table_result = events_table.get_item(Key={'event-id': event_id})['Item']
    event["id"] = event_id
    event["name"] = events_table_result["name"]
    event["date"] = events_table_result["datetime"]
    event["location"] = events_table_result["location"]
    team["event"] = event
    
    member_ids = teams_table_result["members"]
    members = []
    for id in member_ids:
        user = {}
        users_table_result = users_table.get_item(Key={'userId': id})['Item']
        user["id"] = users_table_result["userId"]
        user["name"] = users_table_result["userName"]
        user["image"] = users_table_result["imageUrl"]
        # user["age"] = users_table_result["age"]
        # user["city"] = users_table_result["city"]
        try:
            user["email"] = users_table_result["email"]
        except:
            user["email"] = "No Email"
        members.append(user)
    team["members"] = members
    team["member_ids"] = member_ids
    
    print(team)
    return team

def lambda_handler(event, context):
    team_id = event['pathParameters']['team-id']
    team = get_team(team_id)
    
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,GET'
        },
        'body': json.dumps(team)
    }
