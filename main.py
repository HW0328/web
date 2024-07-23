import re
import uuid
import json
import sqlite3
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI, Request, Form, Response
from fastapi.responses import RedirectResponse, HTMLResponse

meal_url = 'https://donong-m.goegn.kr/donong-m/main.do'

app = FastAPI()
templates = Jinja2Templates(directory="html")
navbar = """
<link
  rel="stylesheet"
  href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css"
/>
<style>
        body{
            margin: 0;
            padding: 0;
        }
        .navbar {
            overflow: hidden;
            background-color: #333;
        }
        .navbar a {
            float: left;
            display: block;
            color: white;
            text-align: center;
            padding: 14px 16px;
            text-decoration: none;
        }
        .navbar a:hover {
            background-color: #ddd;
            color: black;
        }
        .navbar a.active {
            background-color: #04AA6D;
            color: white;
        }
        .main {
            padding : 50px
        }
    </style>
<div class="navbar">
    <a class="active" href="/">Home</a>
    <a href="/board">Board</a>
    <a href="/new">New post</a>
    <a href="/random">Random</a>
    <a href="/weather">Weather</a>
    <a href="/avoid">Avoiding Game</a>
    <a href="/mealinfo">Meal infomation</a>
    <a href="/about">About</a>
</div>
"""



def getWeatherInfo(city):
    api = f"""http://api.openweathermap.org/data/2.5/weather?q={city}&appid=cd58458f4e6be574662e03941558856e&lang=en&units=metric"""
    result = requests.get(api)

    data = json.loads(result.text)
    return data

def getDBConnect():
    con = sqlite3.connect("db.db")
    con.row_factory = sqlite3.Row
    return con

def route(req, html, script="", data=""):
    global navbar
    return templates.TemplateResponse(html, {"request":req, "navbar":navbar, "script":script, "data":data})

def getLunch():
    global meal_url
    response = requests.get(meal_url, verify=False)

    soup = BeautifulSoup(response.text, 'html.parser')

    target_element = soup.select_one('#container > div.MC_wrap3 > div > div.con_wrap > div.MC_box7.widgEdit > div > div.inner > ul > li:nth-child(1) > dl > dd')

    if target_element:
        cleaned_text = re.sub(r'\([^()]*\)', '\n', target_element.text.strip())

        return cleaned_text
    else:
        print("해당 요소를 찾을 수 없습니다.")

# route
@app.get("/", response_class=HTMLResponse)
async def index(req: Request):
    return route(req, "index.html")

@app.get("/board", response_class=HTMLResponse)
async def board(req : Request):
    con = getDBConnect()
    cur = con.cursor()
    cur.execute("SELECT * FROM board")
    board = cur.fetchall()

    return route(req, "board.html", data=board)

@app.get("/board/{board_id}", response_class=HTMLResponse)
async def boardread(req:Request, board_id: int):
    con = getDBConnect()
    cur = con.cursor()
    cur.execute("SELECT * FROM board WHERE id = ?", (board_id, ))
    board = cur.fetchone()
    print(board[0]) # id    
    print(board[1]) # writer
    print(board[2]) # title
    print(board[3]) # content
    print(board[4]) # date
    board = {
        "id" : board[0],
        "writer" : board[1],
        "title" : board[2],
        "content" : board[3],
        "date" : board[4]
    }
    return route(req, "boardread.html", data=board)

@app.get("/new", response_class=HTMLResponse)
async def new(req:Request):
    return route(req, "boardnew.html")

@app.get("/about", response_class=HTMLResponse)
async def about(req : Request):
    return route(req, "about.html")

@app.get("/weather", response_class=HTMLResponse)
async def weather(req : Request):
    weather_data = getWeatherInfo('Seoul')
    weather_info = {
    'main': weather_data['weather'][0]['main'],  # 날씨 상태 이름 (Clear, Clouds, 등등)
    'description': weather_data['weather'][0]['description'],  # 날씨 설명 (맑음, 구름 많음, 등등)
    'temperature': weather_data['main']['temp'],  # 온도 (섭씨)
    'humidity': weather_data['main']['humidity'],  # 습도 (%)
    'wind_speed': weather_data['wind']['speed']  # 풍속 (m/s)
    }

    return route(req, "weather.html", data=weather_info)

@app.get('/mealinfo', response_class=HTMLResponse)
async def mealinfo(req : Request):
    meal = getLunch()
    print(meal)
    if meal == None:
        meal = 'There is no meal today.'
    return route(req, 'mealinfo.html', data=meal)

@app.get("/random")
async def rand(req : Request):
    return route(req, 'random.html')

@app.get("/avoid")
async def avoiding_game(req : Request):
    return route(req, 'avoiding_game.html')

# api
@app.post("/newboard")
async def boardnew(req:Request, id:str=Form(...), title:str=Form(...), content:str=Form(...)):
    con = getDBConnect()
    cur = con.cursor()
    current_datetime = datetime.now()
    formatted_date = current_datetime.strftime("%Y년 %m월 %d일 %H시 %M분")
    cur.execute("INSERT INTO board (writer, title, content, date) VALUES (?, ?, ?, ?)", (id, title, content, formatted_date))
    con.commit()

    return route(req, "index.html")
     


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port = 8000)