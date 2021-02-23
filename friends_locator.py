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
    return render_template("index.html")


@app.route("/friends_map")
def read_item():
    username = request.args.get('username')
    print(username)
    generate_map(username)
    return render_template("friends_map.html")


def generate_map(username: str):
    id = username_to_id(username)
    locations = get_locations_by_id(id)
    coords = locations_to_coords(locations)
    create_html_map(coords)


def username_to_id(username: str) -> int:
    url = "https://api.twitter.com/2/users/by"
    headers = {'Authorization': 'Bearer ' + twitter_bearer_token}
    params = {
        'usernames': username,
    }

    resp = requests.get(url, headers=headers, params=params)

    return resp.json()['data'][0]['id']


def get_locations_by_id(id: int) -> list:
    url = f"https://api.twitter.com/2/users/{id}/following"
    headers = {'Authorization': 'Bearer ' + twitter_bearer_token}
    params = {
        'user.fields': 'location,username',
    }

    resp = requests.get(url, headers=headers, params=params)

    locations = [(user['location'], user['username'])
                 for user in resp.json()['data']
                 if 'location' in user]

    return locations


def locations_to_coords(locations: list) -> list:
    url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
    params = {"input": "UCU", "inputtype": "textquery",
              "fields": "formatted_address,geometry",
              "key": google_key}

    # limit locations for the test
    # locations = locations[:5]

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


def create_html_map(coordinates: list):
    mp = folium.Map()

    fg = folium.FeatureGroup(name="Friends locations")
    for (lt, ln), username in coordinates:
        fg.add_child(folium.Marker(location=[float(lt), float(ln)],
                                   popup=username, icon=folium.Icon()))
    mp.add_child(fg)

    mp.add_child(folium.LayerControl())

    mp.save('templates/friends_map.html')


if __name__ == '__main__':
    app.run()
