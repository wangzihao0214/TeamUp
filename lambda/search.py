import requests
import json
from datetime import datetime
from boto3.dynamodb.conditions import Key, Attr
import boto3
import os

client_id = 'MjY3NTMxNzF8MTY1MTEwOTY4OS40MDg2MzU0'
url = 'https://api.seatgeek.com/2'
gmaps_key = os.environ.get('gmap_key')

# Processes an event returned by SeatGeek to our preferred format.
def process_event(seatgeek_event):
    event = {}
    event["id"] = seatgeek_event["id"]
    event["name"] = seatgeek_event["title"]
    event["url"] = seatgeek_event["url"]
    event["location"] = seatgeek_event["venue"]["display_location"]
    event["image"] = seatgeek_event["performers"][0]["image"]

    # reformat the datetime
    datetime_original = seatgeek_event["datetime_local"]
    datetime_obj = datetime.strptime(datetime_original, "%Y-%m-%dT%H:%M:%S")
    datetime_new = datetime_obj.strftime("%B %d, %Y at %I:%M %p")
    event["datetime"] = datetime_new

    return event
    
# The following code computes recommended events nearby, using a location (latitude and logitude)
# and a list of known preferred artists.
def get_artist_recommended_events(artists, latitude, longitude, max_events):
    # get IDs for our preferred artists
    artist_ids = []
    for artist in artists:
        try:
            resp = requests.get(url + '/performers?slug=' + artist.replace(' ', '-') + '&client_id=' + client_id)
            json_resp = json.loads(resp.text)
            for performer in json_resp["performers"]:
                artist_ids.append(performer["id"])
        except:
            print("Couldn't find artist " + artist)

    #print(artist_ids)

    # for each artist, get recommended events until we hit our max_events
    ids = set()
    recommended_events = []
    now_str = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    fin_searching = False
    for artist_id in artist_ids:
        if fin_searching:
            break
        # rec_url = url + '/recommendations?performers.id=' + str(artist_id) + '&lat=' + str(latitude) + '&lon=' + str(longitude) + '&datetime_local.gt=' + now_str + '&client_id=' + client_id
        rec_url = url + '/recommendations?performers.id=' + str(artist_id) + '&datetime_local.gt=' + now_str + '&client_id=' + client_id
        #print(rec_url)

        try:
            resp = requests.get(rec_url)
            json_resp = json.loads(resp.text)

            for rec in json_resp["recommendations"]:
                event = process_event(rec["event"])
                if event["id"] in ids:
                    continue
                ids.add(event["id"])
                recommended_events.append(event)
                # only get as many events as we requested
                if len(recommended_events) == max_events:
                    fin_searching = True
                    break
        except:
            pass
    return recommended_events

# Get a list of events based purely off of location
def get_location_recommended_events(latitude, longitude, max_events):
    # first, get the city and state based off of latitude and longitude using Google Maps
    city = ''
    state = ''
    gmaps_url = "https://maps.googleapis.com/maps/api/geocode/json?latlng=" + str(latitude) + "," + str(longitude) + '&key=' + gmaps_key

    try:
        resp = requests.get(gmaps_url)
        json_resp = json.loads(resp.text)

        addr_components = json_resp["results"][0]["address_components"]

        for component in addr_components:
            if "locality" in component["types"]:
                city = component["long_name"].lower().replace(' ', '-')
            elif "administrative_area_level_1" in component["types"]:
                state = component["short_name"].lower().replace(' ', '-')
    except:
        print("Could not get city and state.")
        return []
    
    # next, get recommended events from SeatGeek in the future
    now_str = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    recommended_events = []
    ids = set()
    try:
        rec_url = url + '/events?taxonomies.name=concert&venue.city=' + city + '&venue.state=' + state + '&datetime_local.gt=' + now_str + '&client_id=' + client_id
        print(rec_url)
        resp = requests.get(rec_url)
        json_resp = json.loads(resp.text)

        for event in json_resp["events"]:
            processed_event = process_event(event)
            if processed_event["id"] in ids:
                continue
            
            recommended_events.append(processed_event)
            print(processed_event["id"])
            ids.add(id)
            # only get as many events as we requested
            if len(recommended_events) == max_events:
                break        
    except Exception as e:
        print(e)
        print("Could not get location-based events.")

    return recommended_events
    
def process_event_db(e):
    d={}
    d["id"]=e["event-id"]
    d["name"]=e["name"]
    d["url"]=e["url"]
    d["location"]=e["location"]
    d["datetime"]=e["datetime"]
    d["image"]=e["image"]
    return d
    
def get_people_also_attending_events(max_events):
    #recommend events in the future which already have some teams planning to go
    rec=[]
    curr = datetime.now()
    curr_str = curr.strftime("%Y-%m-%d")
    dynamodb = boto3.resource("dynamodb")
    event_ = dynamodb.Table("events")
    
    response = event_.scan(
        FilterExpression = Attr("date").gt(curr_str) 
    )
    for e in response['Items']:
        if len(e['teams']) >= 1:
            rec.append(process_event_db(e))
        if len(rec) == max_events:
            break
    return rec
    
def lambda_handler(event,context):
    print(event)
    body = json.loads(event["body"])
    print(body)
    print(body["artists"])
    print(body["latitude"])
    
    artists = body["artists"]
    lat = body["latitude"]
    lon = body["longitude"]
    #lon = event["queryStringParameters"]["longitude"]
    max_events = 20
    rec={}

    rec["artist_recommendations"]=get_artist_recommended_events(artists, lat, lon, max_events)
    print("Got artist-recommended events.")
    rec["location_recommendations"]=get_location_recommended_events(lat, lon, max_events)
    print("Got location-recommended events.")
    rec["other_recommendations"]=get_people_also_attending_events(max_events)
    print("Got other-recommended events.")
    print(rec)
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,GET'
        },
        'body': json.dumps(rec)
    }