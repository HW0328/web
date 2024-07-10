import sqlite3
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse

app = FastAPI()
templates = Jinja2Templates(directory="html")
navbar = """
<div class="navbar">
    <a class="active" href="/">Home</a>
    <a href="">News</a>
    <a href="">Contact</a>
    <a href="">About</a>
</div>"""

def getDBConnect():
    con = sqlite3.connect("posts.db")
    con.row_factory = sqlite3.Row
    return con

@app.get("/", response_class=HTMLResponse)
async def index(req: Request):
    global navbar
    return templates.TemplateResponse("index.html", {"request":req, "navbar":navbar})