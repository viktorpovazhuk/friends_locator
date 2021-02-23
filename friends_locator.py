from pprint import pprint
import folium as folium
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn
import requests

app = FastAPI()
templates = Jinja2Templates(directory="templates")
twitter_bearer_token = 'AAAAAAAAAAAAAAAAAAAAAG7KMwEAAAAA54JdYkWN17qlqjSHWfSGzR' \
                       'wxzaY%3DDZte5Xdq1mXJkHOsAWyXSBcMiDssP5q8hUZvve7evDXHOIDmFa'
google_key = "AIzaSyCjEEmgflTyKDb8Czyh12P4fICziH_67bY"


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/friends_map", response_class=HTMLResponse)
def read_item(request: Request, username: str):
    generate_map(username)
    return templates.TemplateResponse("friends_map.html", {"request": request})


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
    uvicorn.run(app, host="0.0.0.0", port=8000)
