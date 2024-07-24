import re
import uuid
import json
import random
import sqlite3
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI, Request, Form, Response
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse

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
    <a href="/joke">Joke</a>
    <a href="/board">Board</a>
    <a href="/new">New post</a>
    <a href="/random">Random</a>
    <a href="/weather">Weather</a>
    <a href="/avoid">Avoiding Game</a>
    <a href="/mealinfo">Meal infomation</a>
    <a href="/about">About</a>
</div>
"""

funny_jokes = [
    {"que": "Why did the scarecrow win an award?", "ans": "Because he was outstanding in his field!"},
    {"que": "Why don’t skeletons fight each other?", "ans": "They don’t have the guts."},
    {"que": "What do you call fake spaghetti?", "ans": "An impasta!"},
    {"que": "Why did the math book look sad?", "ans": "Because it had too many problems."},
    {"que": "What do you call cheese that isn’t yours?", "ans": "Nacho cheese!"},
    {"que": "Why did the golfer bring two pairs of pants?", "ans": "In case he got a hole in one."},
    {"que": "What do you call a bear with no teeth?", "ans": "A gummy bear."},
    {"que": "Why did the tomato turn red?", "ans": "Because it saw the salad dressing!"},
    {"que": "How does a penguin build its house?", "ans": "Igloos it together."},
    {"que": "Why don’t scientists trust atoms?", "ans": "Because they make up everything."},
    {"que": "What do you get when you cross a snowman and a vampire?", "ans": "Frostbite."},
    {"que": "What do you call a can opener that doesn’t work?", "ans": "A can’t opener."},
    {"que": "Why did the bicycle fall over?", "ans": "Because it was two-tired."},
    {"que": "What do you call a dinosaur with an extensive vocabulary?", "ans": "A thesaurus."},
    {"que": "What does a nosy pepper do?", "ans": "Gets jalapeño business!"},
    {"que": "Why don’t programmers like nature?", "ans": "It has too many bugs."},
    {"que": "How does a scientist freshen her breath?", "ans": "With experi-mints."},
    {"que": "What do you call a pile of cats?", "ans": "A meowtain."},
    {"que": "What do you call an alligator in a vest?", "ans": "An investigator."},
    {"que": "Why did the scarecrow become a successful neurosurgeon?", "ans": "He was outstanding in his field."},
    {"que": "What did the janitor say when he jumped out of the closet?", "ans": "Supplies!"},
    {"que": "What did one ocean say to the other ocean?", "ans": "Nothing, they just waved."},
    {"que": "Why did the golfer bring an extra pair of socks?", "ans": "In case he got a hole in one."},
    {"que": "Why did the student eat his homework?", "ans": "Because the teacher told him it was a piece of cake."},
    {"que": "What do you call a fish with no eyes?", "ans": "Fsh."},
    {"que": "How does a train eat?", "ans": "It goes chew chew."},
    {"que": "Why did the bicycle fall over?", "ans": "Because it was two-tired."},
    {"que": "What do you call a fake noodle?", "ans": "An impasta."},
    {"que": "Why did the math book look sad?", "ans": "Because it had too many problems."},
    {"que": "What did the left eye say to the right eye?", "ans": "Between you and me, something smells."},
    {"que": "Why don’t skeletons fight each other?", "ans": "They don’t have the guts."},
    {"que": "Why did the coffee file a police report?", "ans": "It got mugged."},
    {"que": "What do you call cheese that isn't yours?", "ans": "Nacho cheese."},
    {"que": "Why did the golfer bring two pairs of pants?", "ans": "In case he got a hole in one."},
    {"que": "What do you call a cow with no legs?", "ans": "Ground beef."},
    {"que": "What do you call a bear with no teeth?", "ans": "A gummy bear."},
    {"que": "How does a penguin build its house?", "ans": "Igloos it together."},
    {"que": "What do you call a factory that makes good products?", "ans": "A satisfactory."},
    {"que": "Why did the math book look sad?", "ans": "It had too many problems."},
    {"que": "What do you call a pile of cats?", "ans": "A meowtain."},
    {"que": "Why don’t scientists trust atoms?", "ans": "Because they make up everything."},
    {"que": "What did the ocean say to the beach?", "ans": "Nothing, it just waved."},
    {"que": "Why did the scarecrow become a successful neurosurgeon?", "ans": "He was outstanding in his field."},
    {"que": "What do you call an alligator in a vest?", "ans": "An investigator."},
    {"que": "Why did the chicken go to the seance?", "ans": "To talk to the other side."},
    {"que": "What did the janitor say when he jumped out of the closet?", "ans": "Supplies!"},
    {"que": "What do you call a fish with no eyes?", "ans": "Fsh."},
    {"que": "How does a train eat?", "ans": "It goes chew chew."},
    {"que": "What do you call an alligator in a vest?", "ans": "An investigator."},
    {"que": "Why did the scarecrow win an award?", "ans": "Because he was outstanding in his field!"},
    {"que": "What did the grape do when he got stepped on?", "ans": "Nothing but let out a little wine."},
    {"que": "Why don’t skeletons fight each other?", "ans": "They don’t have the guts."},
    {"que": "What do you call fake spaghetti?", "ans": "An impasta!"},
    {"que": "Why did the bicycle fall over?", "ans": "Because it was two-tired."},
    {"que": "What did one wall say to the other wall?", "ans": "I'll meet you at the corner."},
    {"que": "Why don’t some couples go to the gym?", "ans": "Because some relationships don’t work out."},
    {"que": "Why did the golfer bring an extra pair of pants?", "ans": "In case he got a hole in one."},
    {"que": "What do you call a factory that makes good products?", "ans": "A satisfactory."},
    {"que": "How does a penguin build its house?", "ans": "Igloos it together."},
    {"que": "What do you call cheese that isn't yours?", "ans": "Nacho cheese."},
    {"que": "Why don’t skeletons fight each other?", "ans": "They don’t have the guts."},
    {"que": "Why did the coffee file a police report?", "ans": "It got mugged."},
    {"que": "What do you call a bear with no teeth?", "ans": "A gummy bear."},
    {"que": "What do you call a fish with no eyes?", "ans": "Fsh."},
    {"que": "What do you call a snowman with a six-pack?", "ans": "An abdominal snowman."},
    {"que": "What did the janitor say when he jumped out of the closet?", "ans": "Supplies!"},
    {"que": "Why did the golfer bring two pairs of pants?", "ans": "In case he got a hole in one."},
    {"que": "Why did the scarecrow become a successful neurosurgeon?", "ans": "He was outstanding in his field."},
    {"que": "How does a scientist freshen her breath?", "ans": "With experi-mints."},
    {"que": "What do you call a pile of cats?", "ans": "A meowtain."},
    {"que": "Why did the student eat his homework?", "ans": "Because the teacher told him it was a piece of cake."},
    {"que": "What do you call a cow with no legs?", "ans": "Ground beef."},
    {"que": "Why did the scarecrow win an award?", "ans": "Because he was outstanding in his field!"},
    {"que": "Why did the math book look sad?", "ans": "Because it had too many problems."},
    {"que": "What do you call a fish with no eyes?", "ans": "Fsh."},
    {"que": "What do you call an alligator in a vest?", "ans": "An investigator."},
    {"que": "Why did the bicycle fall over?", "ans": "Because it was two-tired."},
    {"que": "Why don’t programmers like nature?", "ans": "It has too many bugs."},
    {"que": "What did one wall say to the other wall?", "ans": "I'll meet you at the corner."},
    {"que": "What did the grape do when he got stepped on?", "ans": "Nothing but let out a little wine."},
    {"que": "What do you call a factory that makes good products?", "ans": "A satisfactory."},
    {"que": "Why did the golfer bring an extra pair of pants?", "ans": "In case he got a hole in one."},
    {"que": "Why don’t some couples go to the gym?", "ans": "Because some relationships don’t work out."},
    {"que": "How does a penguin build its house?", "ans": "Igloos it together."},
    {"que": "What do you call a snowman with a six-pack?", "ans": "An abdominal snowman."},
    {"que": "Why don’t skeletons fight each other?", "ans": "They don’t have the guts."},
    {"que": "Why did the coffee file a police report?", "ans": "It got mugged."},
    {"que": "What do you call cheese that isn't yours?", "ans": "Nacho cheese."},
    {"que": "Why did the chicken go to the seance?", "ans": "To talk to the other side."},
    {"que": "What did the ocean say to the beach?", "ans": "Nothing, it just waved."},
    {"que": "Why did the golfer bring two pairs of pants?", "ans": "In case he got a hole in one."},
    {"que": "What do you call an alligator in a vest?", "ans": "An investigator."},
    {"que": "How does a scientist freshen her breath?", "ans": "With experi-mints."},
    {"que": "What did one wall say to the other wall?", "ans": "I'll meet you at the corner."},
    {"que": "Why don’t skeletons fight each other?", "ans": "They don’t have the guts."},
    {"que": "Why did the scarecrow become a successful neurosurgeon?", "ans": "He was outstanding in his field."},
    {"que": "What do you call a pile of cats?", "ans": "A meowtain."},
    {"que": "Why did the math book look sad?", "ans": "Because it had too many problems."},
    {"que": "What do you call a snowman with a six-pack?", "ans": "An abdominal snowman."},
    {"que": "Why did the bicycle fall over?", "ans": "Because it was two-tired."},
    {"que": "Why don’t some couples go to the gym?", "ans": "Because some relationships don’t work out."},
    {"que": "How does a penguin build its house?", "ans": "Igloos it together."},
    {"que": "What do you call a fish with no eyes?", "ans": "Fsh."},
    {"que": "What did the grape do when he got stepped on?", "ans": "Nothing but let out a little wine."},
    {"que": "What do you call a factory that makes good products?", "ans": "A satisfactory."},
    {"que": "Why did the coffee file a police report?", "ans": "It got mugged."},
    {"que": "What do you call a snowman with a six-pack?", "ans": "An abdominal snowman."},
    {"que": "What did one ocean say to the other ocean?", "ans": "Nothing, they just waved."},
    {"que": "Why did the golfer bring two pairs of pants?", "ans": "In case he got a hole in one."},
    {"que": "What do you call a cow with no legs?", "ans": "Ground beef."},
    {"que": "Why don’t skeletons fight each other?", "ans": "They don’t have the guts."},
    {"que": "How does a scientist freshen her breath?", "ans": "With experi-mints."},
    {"que": "What do you call an alligator in a vest?", "ans": "An investigator."},
    {"que": "Why did the scarecrow win an award?", "ans": "Because he was outstanding in his field!"}
]




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
@app.get("/", response_class=FileResponse)
async def index(req: Request):
    return route(req, "index.html")

@app.get("/board", response_class=FileResponse)
async def board(req : Request):
    con = getDBConnect()
    cur = con.cursor()
    cur.execute("SELECT * FROM board")
    board = cur.fetchall()

    return route(req, "board.html", data=board)

@app.get("/board/{board_id}", response_class=FileResponse)
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

@app.get("/new", response_class=FileResponse)
async def new(req:Request):
    return route(req, "boardnew.html")

@app.get("/about", response_class=FileResponse)
async def about(req : Request):
    return route(req, "about.html")

@app.get("/weather", response_class=FileResponse)
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

@app.get('/mealinfo', response_class=FileResponse)
async def mealinfo(req : Request):
    meal = getLunch()
    print(meal)
    if meal == None:
        meal = 'There is no meal today.'
    return route(req, 'mealinfo.html', data=meal)

@app.get("/random", response_class=FileResponse)
async def rand(req : Request):
    return route(req, 'random.html')

@app.get("/avoid", response_class=FileResponse)
async def avoiding_game(req : Request):
    return route(req, 'avoiding_game.html')

@app.get("/joke", response_class=FileResponse)
async def jokes(req : Request):
    return route(req, 'joke.html')

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
     
@app.get("/funny_jokes")
async def retjoke():
    global funny_jokes
    rand = random.randint(0, 99)
    print(rand)
    question = funny_jokes[rand]['que']
    answer = funny_jokes[rand]['ans']
    que_html = f"<h2 id='jokeShow'>Joke : {question} </h2>"
    ans_html = f"<h2 id='ansShow' style='opacity: 0%;'>Answer : {answer} </h2>"
    return HTMLResponse(f"{que_html}{ans_html}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port = 8000)