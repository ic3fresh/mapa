#!/usr/bin/env python3
"""
Script to get data from paciak and geocode it.
"""
import urllib.request
import urllib.parse
import json
import time

DEBUG = True 

API_URL = "URL"
API_KEY = "APIKEY"
API_USER = "APIUSER"
API_SLEEP = 1

def debug(text):
    """Debug messages"""
    if DEBUG:
        print(text)

def discourse_api_url(req):
    """Prepare discourse api call url"""
    return "{0}{1}&api_key={2}&api_username={3}".format(API_URL, req, API_KEY, API_USER)

def discourse_api(url):
    """Make API call to discourse"""
    try:
        debug("In dicourse_api: {0}".format(url))
        response = urllib.request.urlopen(url)
    except urllib.error.HTTPError as e:
        print("Oppss, HTTP returned: {0} with: {1}".format(e.code, e.reason))
        print("Check API settings")
        exit(1)
    except urllib.error.URLError as e:
        print("Oppss, URL error: {0}".format(e.reason))
        exit(2)

    return response

def get_users():
    """Get list of all users"""
    next_page = "directory_items.json?period=all&order=post_count"
    total_users = 1
    non_active = 0
    users = list()

    while len(users) < total_users - non_active:
        url = discourse_api_url(next_page.replace("directory_items?", "directory_items.json?"))
        debug("In get_users: {0}".format(url))
        response = discourse_api(url).read().decode('utf-8')
        response = json.loads(response)
        total_users = response["total_rows_directory_items"]
        next_page = response["load_more_directory_items"]
        debug("In get_users, next page: {0}".format(next_page))

        for user in response["directory_items"]:
            count = user["likes_received"] + user["likes_given"] + user["topics_entered"] +\
                    user["topic_count"] + user["post_count"] + user["posts_read"] +\
                    user["days_visited"]
            if count > 0:
                users.append(user["user"]["username"])
            else:
                non_active = non_active + 1
                debug(json.dumps(user, indent=2))

    return users

def get_latlon(location):
    """Geocode location"""
    url = "https://nominatim.openstreetmap.org/search/?q={0}&format=json&limit=1".format(
        urllib.parse.quote(location))
    debug("In get_latlon: {0}".format(url))

    try:
        response = urllib.request.urlopen(url)
    except urllib.error.HTTPError as e:
        print("Geocoding HTTP error {0} with: {1}".format(e.code, e.reason))
        exit(3)
    except urllib.error.URLError as e:
        print("Geocoding URL error: {0}".format(e.reason))
        exit(4)

    response = json.loads(response.read().decode('utf-8'))

    return response

def get_data(users):
    """Get data about users, omit users without location"""
    users_data = list()

    for user in users:
        debug("Processing in get_data: {0}".format(user))

        data = dict()
        url = discourse_api_url("users/{0}.json?".format(user))
        user_data = discourse_api(url).read().decode('utf-8')
        user_data = json.loads(user_data)

        if "location" in user_data["user"]:
            data["username"] = user
            data["avatar"] = user_data["user"]["avatar_template"].replace("{size}", "32")
            data["location"] = dict()

            location = get_latlon(user_data["user"]["location"])
            if location:
                data["location"]["name"] = user_data["user"]["location"]
                data["location"]["lat"] = location[0]["lat"]
                data["location"]["lon"] = location[0]["lon"]

                debug("In get_data, location: {0}".format(location))

                users_data.append(data)
            else:
                debug("In get_data, no location for {0}".format(user))

        time.sleep(API_SLEEP)

    return users_data

if __name__ == "__main__":
    paciak_users = get_users()
    usersdata = get_data(paciak_users)
    print(json.dumps(usersdata, indent=2))
