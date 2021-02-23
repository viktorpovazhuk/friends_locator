from pprint import pprint
import folium as folium
from flask import Flask, render_template, request
import requests

app = Flask(__name__)
twitter_bearer_token = 'AAAAAAAAAAAAAAAAAAAAAG7KMwEAAAAA54JdYkWN17qlqjSHWfSGzR' \
                       'wxzaY%3DDZte5Xdq1mXJkHOsAWyXSBcMiDssP5q8hUZvve7evDXHOIDmFa'
google_key = "AIzaSyCjEEmgflTyKDb8Czyh12P4fICziH_67bY"


@app.route("/")
def read_root():
    """
    Return content of root html file
    """
    return render_template("index.html")


@app.route("/friends_map")
def read_item():
    """
    Return content of html map with user's friends on it
    """
    username = request.args.get('username')

    mp = generate_map(username)

    return mp._repr_html_()


def generate_map(username: str) -> folium.Map:
    """
    Return map object with locations of friends of specified user
    """
    user_id = username_to_id(username)
    locations = get_locations_by_id(user_id)
    coords = locations_to_coords(locations)
    mp = create_html_map(coords)

    return mp


def username_to_id(username: str) -> str:
    """
    Convert user's username to id

    >>> username_to_id("Valsorya2Go")
    '1362368428011569156'
    """
    url = "https://api.twitter.com/2/users/by"
    headers = {'Authorization': 'Bearer ' + twitter_bearer_token}
    params = {
        'usernames': username,
    }

    resp = requests.get(url, headers=headers, params=params)

    return resp.json()['data'][0]['id']


def get_locations_by_id(user_id: str) -> list:
    """
    Return list of addresses of user's friends
    """
    url = f"https://api.twitter.com/2/users/{user_id}/following"
    headers = {'Authorization': 'Bearer ' + twitter_bearer_token}
    params = {
        'user.fields': 'location,username',
    }

    resp = requests.get(url, headers=headers, params=params)

    locations = [(user['location'], user['username'])
                 for user in resp.json().get('data', [])
                 if 'location' in user]

    return locations


def locations_to_coords(locations: list) -> list:
    """
    Return coordinates for the list of addresses
    """
    url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
    params = {"input": "UCU", "inputtype": "textquery",
              "fields": "formatted_address,geometry",
              "key": google_key}

    coords = []
    for loc in locations:
        params["input"] = loc[0]

        resp = requests.get(url, params=params)
        body = resp.json()

        if body['status'] == 'ZERO_RESULTS':
            continue

        geometry = body['candidates'][0]['geometry']['location']
        geometry = (geometry['lat'], geometry['lng'])
        coords.append((geometry, loc[1]))

    return coords


def create_html_map(coordinates: list) -> folium.Map:
    """
    Create map object with markers in coordinates
    """
    mp = folium.Map()

    fg = folium.FeatureGroup(name="Friends locations")
    for (lt, ln), username in coordinates:
        fg.add_child(folium.Marker(location=[float(lt), float(ln)],
                                   popup=username, icon=folium.Icon()))
    mp.add_child(fg)

    mp.add_child(folium.LayerControl())

    return mp


if __name__ == '__main__':
    app.run(debug=True)
