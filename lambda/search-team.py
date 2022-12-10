import json
import requests
import boto3


opensearch_host = 'https://search-teams-bps6hvuuhcemd7ndync2hptxrm.us-east-1.es.amazonaws.com/'

dynamodb = boto3.resource('dynamodb')
teams_table = dynamodb.Table("teams")


def search_team(team_name, event_id):
    url = opensearch_host + 'teams/_search'
    data = {
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "event_id": event_id
                        }
                    },
                    {
                        "match": {
                            "team_name": {
                                "query": team_name,
                                "fuzziness": 'AUTO'
                            }
                        }
                    }
                ]
            }
        }
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(url=url, auth=('wangzihao0214', 'Wzh19980214!'), headers=headers, json=data)
    response = response.json()
    result = response['hits']['hits']

    team_ids = []
    teams = []
    for item in result:
        team_ids.append(item['_source']['team_id'])
    for team_id in team_ids:
        team_result = teams_table.get_item(Key={'team-id': team_id})
        if 'Item' not in team_result.keys():
            continue
        teams.append(team_result['Item'])
    print(teams)
    return teams


def lambda_handler(event, context):
    event_id = event['queryStringParameters']["event-id"]
    team_name = event['queryStringParameters']["team-name"]
    teams = search_team(team_name, event_id)
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,GET'
        },
        'body': json.dumps(teams)
    }
