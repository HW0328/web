import uuid
import sqlite3
from datetime import datetime
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI, Request, Form, Response
from fastapi.responses import RedirectResponse, HTMLResponse

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
    </style>
<div class="navbar">
    <a class="active" href="/">Home</a>
    <a href="/board">Board</a>
    <a href="/new">New</a>
    <a href="/about">About</a>
</div>
"""





def getDBConnect():
    con = sqlite3.connect("db.db")
    con.row_factory = sqlite3.Row
    return con

def route(req, html, script="", data=""):
    global navbar
    return templates.TemplateResponse(html, {"request":req, "navbar":navbar, "script":script, "data":data})



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


""" LOGIN SERVICE"""
# ifguestnavbar = navbar+"""<a href="/login">Login</a>
# <a href="signup">Sign up</a>
# </div>"""
# ifloginednavbar = lambda user: navbar+f"""<a href="/">{user}</a>
# <a href="/logout">Logout</a>
# </div>
# """
# token = req.cookies.get("logintoken")
# print(f"token : {token}")
# if token:
# con = getDBConnect()
# cur = con.cursor()
# cur.execute("SELECT userid FROM login WHERE loginkey = ?", (token,))
# username = cur.fetchone()
# print(username[0])
# if username != []:
# return templates.TemplateResponse(html, {"request":req, "navbar":ifguestnavbar})

# @app.get("/login/")
# async def login(req: Request):
#     return route(req, "login.html")

# @app.post('/firstlogin/')
# async def firstlogin(req : Request,
#                     res : Response,
#                     userid : str=Form(...),
#                      pw : str=Form(...)):
#     con = getDBConnect()
#     cur = con.cursor()
#     cur.execute("SELECT * FROM user WHERE userid = ? AND pw = ?", (userid, pw))
#     user = cur.fetchone()  # 사용자 정보 가져오기

#     if user:
#         print("OK")
#         login_key = str(uuid.uuid4())
#         print()
#         cur.execute("INSERT INTO login (userid, loginkey) VALUES (?, ?)", (userid, login_key))
#         con.commit()  # 변경사항 커밋

#         expire = datetime.utcnow() + timedelta(days=365*10)  # 10년 후 만료
#         res.set_cookie(
#             key="logintoken",
#             value=login_key,
#             httponly=True,
#             # secure=True,  # HTTPS에서만 전송
#             # samesite="Strict",  # CSRF 방지 
#             expires=expire.strftime("%a, %d-%b-%Y %H:%M:%S GMT")
#         )
#         return route(req, "index.html")
#     else:
#         print("FUCK")
#         return HTMLResponse(content='<script>alert("wrong")</script>')

# @app.get("/signin")
# async def signin(req : Request):
#     return route(req, "signin.html")
    
#     ...

# @app.get("/logout")
# async def logout(req : Request, res : Response):
#     res.delete_cookie(key="logintoken", path="/", domain=None, secure=True, httponly=True)
#     return route(req, "index.html")

