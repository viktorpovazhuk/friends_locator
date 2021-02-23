from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn


app = FastAPI()

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/friends_map", response_class=HTMLResponse)
def read_item(request: Request, username: str):
    return username

def generate_map(username: str):
    username_to_id()
    get_locations_by_id()
    locations_to_coords()
    create_html_map()

def username_to_id():
    pass

def get_locations_by_id():
    pass

def locations_to_coords():
    pass

def create_html_map():
    pass

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
