import json
import boto3
import secrets
import urllib3
from datetime import datetime
import requests

http = urllib3.PoolManager()
client_id = 'MjY3NTMxNzF8MTY1MTEwOTY4OS40MDg2MzU0'
url = 'https://api.seatgeek.com/2'
opensearch_host = 'https://search-teams-bps6hvuuhcemd7ndync2hptxrm.us-east-1.es.amazonaws.com/'

dynamodb = boto3.resource('dynamodb')


def process_datetime(datetime_original):
    datetime_obj = datetime.strptime(datetime_original, "%Y-%m-%dT%H:%M:%S")
    return datetime_obj.strftime("%B %d, %Y at %I:%M %p")


def process_date(datetime_original):
    datetime_obj = datetime.strptime(datetime_original, "%Y-%m-%dT%H:%M:%S")
    return datetime_obj.strftime("%Y-%m-%d")


def update_profile(team_id, user_id):
    # get user info by a specific user-id
    users = dynamodb.Table("users")
    userInfo = users.get_item(Key={'userId': user_id})['Item']
    try:
        teams = userInfo["teams"]
        teams.append(team_id)
    except:
        teams = [team_id]
    finally:
        response = users.update_item(
            Key={'userId': user_id},
            UpdateExpression="SET teams = :t",
            ExpressionAttributeValues={':t': teams},
            ReturnValues="UPDATED_NEW"
        )
        print(response['Attributes'])


def update_opensearch(team_id, team_name, event_id):
    data = {
        'doc': {
            'team_id': team_id,
            'team_name': team_name,
            'event_id': event_id
        },
        'doc_as_upsert': True
    }
    data = json.dumps(data)
    url = opensearch_host + 'teams/_update/' + team_id
    headers = {"Content-Type": "application/json"}
    response = requests.post(url=url, auth=('wangzihao0214', 'Wzh19980214!'), headers=headers, data=data)
    print(response)


def join_team(user_id, team_id):
    # get team info by a specific team-id
    teams = dynamodb.Table("teams")
    members = teams.get_item(Key={'team-id': team_id})['Item']['members']
    members.append(user_id)

    response = teams.update_item(
        Key={'team-id': team_id},
        UpdateExpression="SET members = :m",
        ExpressionAttributeValues={':m': members},
        ReturnValues="UPDATED_NEW"
    )
    print(response['Attributes'])


def create_team(user_id, team_name, event_id):
    # generate team id
    team_id = secrets.token_urlsafe(20)
    print(team_id)
    # create item in teams table
    teams = dynamodb.Table("teams")
    response1 = teams.put_item(
        Item={
            "team-id":team_id,
             "event-id": event_id,
             "members": [user_id],
             "team name": team_name,
             "description": 'NA'
        },
        ReturnValues = "ALL_OLD"
    )
    update_opensearch(team_id, team_name, event_id)
    # update the event table if the corresponding event exists
    event_ = dynamodb.Table("events")
    eventInfo = event_.get_item(Key={'event-id': event_id})
    if 'Item' in eventInfo:
        print("event exists")
        try:
            teams = eventInfo['Item']["teams"]
            print("event has team feature")
            teams.append(team_id)
        except:
            print("event doesn't has team feature")
            teams = [team_id]
        finally:
            response = event_.update_item(
                Key={'event-id': event_id},
                UpdateExpression="SET teams = :t",
                ExpressionAttributeValues={':t': teams},
                ReturnValues="UPDATED_NEW"
            )
    else:
        print("event NOT exists")
        # if the event does not exist in the event table, create a new event
        # first, get the event image
        image_url = ""
        name = ""
        event_url = ""
        datetime_str = ""
        date_str = ""
        loc_str = ""

        try:
            resp = http.request("GET", url + '/events/' + event_id + '?client_id=' + client_id)
            resp_json = json.loads(resp.data)

            name = resp_json["title"]
            image_url = resp_json["performers"][0]["image"]
            event_url = resp_json["url"]
            datetime_str = process_datetime(resp_json["datetime_local"])
            date_str = process_date(resp_json["datetime_local"])
            loc_str = resp_json["venue"]["display_location"]
        except:
            pass

        # finally, create the event
        event_.put_item(
            Item={
                "event-id": event_id,
                "teams": [team_id],
                "image": image_url,
                "name": name,
                "url": event_url,
                "datetime": datetime_str,
                "date": date_str,
                "location": loc_str
            },
            ReturnValues="ALL_OLD"
        )
        # update user profile
    update_profile(team_id, user_id)


def lambda_handler(event, context):
    operation = event['queryStringParameters']['operation']
    event_id = event['queryStringParameters']["event-id"]
    user_id = event['queryStringParameters']["user-id"]

    if operation == 'join':
        team_id = event['queryStringParameters']["team-id"]
        join_team(user_id, team_id)
        update_profile(team_id, user_id)
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Headers': '*',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,GET'
            },
            'body': 'Team Joined'
        }
    if operation == 'create':
        team_name = event['queryStringParameters']["team-name"]
        create_team(user_id, team_name, event_id)
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Headers': '*',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,GET'
            },
            'body': 'Team Created'
        }