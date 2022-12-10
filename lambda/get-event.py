import json
import boto3
import urllib3
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
events_table = dynamodb.Table("events")
teams_table = dynamodb.Table("teams")

http = urllib3.PoolManager()
client_id = 'MjY3NTMxNzF8MTY1MTEwOTY4OS40MDg2MzU0'
url = 'https://api.seatgeek.com/2'

def process_datetime(datetime_original):
    datetime_obj = datetime.strptime(datetime_original, "%Y-%m-%dT%H:%M:%S")
    return datetime_obj.strftime("%B %d, %Y at %I:%M %p")

def get_event(event_id):
    event = {"event-id": event_id}
    teams = []
    name = event_url = datetime_str = location = image_url = ""
    
    # attempt to get teams from the event table, if it's in there
    try:
        events_table_result = events_table.get_item(Key={'event-id': event_id})
        team_ids = events_table_result['Item']["teams"]
        for team_id in team_ids:
            team_result = teams_table.get_item(Key={'team-id': team_id})
            if 'Item' not in team_result.keys():
                continue
            teams.append(team_result['Item'])
    except:
        pass
    event["teams"] = teams
    
    try:
        resp = http.request("GET", url + '/events/' + event_id + '?client_id=' + client_id)
        resp_json = json.loads(resp.data)
        
        name = resp_json["title"]
        event_url = resp_json["url"]
        location = resp_json["venue"]["display_location"]
        datetime_str = process_datetime(resp_json["datetime_local"])
        image_url = resp_json["performers"][0]["image"] # ["performers"][0]["images"]["large/huge/small/medium"]
    except:
        pass
    event["name"] = name
    event["url"] = event_url
    event["location"] = location
    event["datetime"] = datetime_str
    event["image_url"] = image_url

    return event

def lambda_handler(event, context):
    event_id = event['pathParameters']['event-id']
    event = get_event(event_id)
    
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,GET'
        },
        'body': json.dumps(event)
    }
