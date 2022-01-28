from fastapi import Depends, FastAPI, HTTPException, status, WebSocket, Response, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import Optional, List
from fastapi.logger import logger
import asyncio
import re
import logging
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates



import uvicorn


templates = Jinja2Templates(directory="templts")
app = FastAPI()

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "fakehashedsecret",
        "disabled": False,
    },
    "alice": {
        "username": "alice",
        "full_name": "Alice Wonderson",
        "email": "alice@example.com",
        "hashed_password": "fakehashedsecret2",
        "disabled": False,
    },
	"peter": {
        "username": "peter",
        "full_name": "Spiderman Parker",
        "email": "spider@example.com",
        "hashed_password": "fakehashedspider",
        "disabled": False,
    },
}

class ActiveUser:
    username = []


def fake_hash_password(password: str):
    return "fakehashed" + password


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class ConnectionManager:
    def __init__(self):
        self.connections: List[WebSocket] = []

    def disconnect(self, websocket: WebSocket):
        self.connections.remove(websocket)

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.append(websocket)

    async def broadcast(self, data: str):
        for connection in self.connections:
            await connection.send_text(data)


manager = ConnectionManager()


class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None


class UserInDB(User):
    hashed_password: str


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def fake_decode_token(token):
    # This doesn't provide any security at all
    # Check the next version
    user = get_user(fake_users_db, token)
    return user


async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token")
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    print("this is me")
    user_dict = fake_users_db.get(form_data.username)
    if form_data.username in ActiveUser.username:
        return HTMLResponse(logdestroy)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user = UserInDB(**user_dict)
    hashed_password = fake_hash_password(form_data.password)
    print(">>>>>>>",ActiveUser.username)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    ActiveUser.username.append(form_data.username)
    return templates.TemplateResponse("item.html", {"request": request,"user": str(form_data.username)})
    #return HTMLResponse(html)

# @app.websocket("/logout/{user}")
# async def websocket_deadpoint(user: str, websocket: WebSocket):
#     print("Current Active users: ", ActiveUser.username)
#     print("Removing user: ",[re.findall(r'(\w+?)(\d+)', user)[0]][0][0])
#     closer=await websocket.
#     await manager.disconnect(closer)
#     ActiveUser.username.remove([re.findall(r'(\w+?)(\d+)', user)[0]][0][0])
#     print("new active users>>>",ActiveUser.username)
#     return HTMLResponse(login)


@app.get("/logout/{user}")
async def websocket_logout(user: str):
    print("140")
    print("Current Active users: ", ActiveUser.username)
    print("Removing user: ", user)
    ActiveUser.username.remove(user)
    print("new active users>>>", ActiveUser.username)
    app.get("/")


@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


login= """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body {font-family: Arial, Helvetica, sans-serif;}

/* Full-width input fields */
input[type=text], input[type=password] {
  width: 100%;
  padding: 12px 20px;
  margin: 8px 0;
  display: inline-block;
  border: 1px solid #ccc;
  box-sizing: border-box;
}

/* Set a style for all buttons */
button {
  background-color: #04AA6D;
  color: white;
  padding: 14px 20px;
  margin: 8px 0;
  border: none;
  cursor: pointer;
  width: 100%;
}

button:hover {
  opacity: 0.8;
}

/* Extra styles for the cancel button */
.cancelbtn {
  width: auto;
  padding: 10px 18px;
  background-color: #f44336;
}

/* Center the image and position the close button */
.imgcontainer {
  text-align: center;
  margin: 24px 0 12px 0;
  position: relative;
}

img.avatar {
  width: 40%;
  border-radius: 50%;
}

.container {
  padding: 16px;
}

span.password {
  float: right;
  padding-top: 16px;
}

/* The Modal (background) */
.modal {
  display: none; /* Hidden by default */
  position: fixed; /* Stay in place */
  z-index: 1; /* Sit on top */
  left: 0;
  top: 0;
  width: 100%; /* Full width */
  height: 100%; /* Full height */
  overflow: auto; /* Enable scroll if needed */
  background-color: rgb(0,0,0); /* Fallback color */
  background-color: rgba(0,0,0,0.4); /* Black w/ opacity */
  padding-top: 60px;
}

/* Modal Content/Box */
.modal-content {
  background-color: #fefefe;
  margin: 5% auto 15% auto; /* 5% from the top, 15% from the bottom and centered */
  border: 1px solid #888;
  width: 80%; /* Could be more or less, depending on screen size */
}

/* The Close Button (x) */
.close {
  position: absolute;
  right: 25px;
  top: 0;
  color: #000;
  font-size: 35px;
  font-weight: bold;
}

.close:hover,
.close:focus {
  color: red;
  cursor: pointer;
}

/* Add Zoom Animation */
.animate {
  -webkit-animation: animatezoom 0.6s;
  animation: animatezoom 0.6s
}

@-webkit-keyframes animatezoom {
  from {-webkit-transform: scale(0)} 
  to {-webkit-transform: scale(1)}
}
  
@keyframes animatezoom {
  from {transform: scale(0)} 
  to {transform: scale(1)}
}

/* Change styles for span and cancel button on extra small screens */
@media screen and (max-width: 300px) {
  span.password {
     display: block;
     float: none;
  }
  .cancelbtn {
     width: 100%;
  }
}
</style>
</head>
<body>

<h2>Modal Login Form</h2>

<button onclick="document.getElementById('id01').style.display='block'" style="width:auto;">Login</button>

<div id="id01" class="modal">
  
  <form class="modal-content animate" action="/token"  method="post" enctype="application/x-www-form-urlencoded">
    <div class="imgcontainer">
      <span onclick="document.getElementById('id01').style.display='none'" class="close" title="Close Modal">&times;</span>
      <img src="img_avatar2.png" alt="Avatar" class="avatar">
    </div>

    <div class="container">
      <label for="username"><b>Username</b></label>
      <input type="text" placeholder="Enter Username" name="username" required>

      <label for="password"><b>Password</b></label>
      <input type="password" placeholder="Enter Password" name="password" required>
        
      <button type="submit">Login</button>
      <label>
        <input type="checkbox" checked="checked" name="remember"> Remember me
      </label>
    </div>

    <div class="container" style="background-color:#f1f1f1">
      <button type="button" onclick="document.getElementById('id01').style.display='none'" class="cancelbtn">Cancel</button>
      <span class="password">Forgot <a href="#">password?</a></span>
    </div>
  </form>
</div>

<script>
// Get the modal
var modal = document.getElementById('id01');

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
}

</script>

</body>
</html>
"""
html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var uid=Date.now();
            var ws = new WebSocket(`ws://0.0.0.0:5000/ws/${uid}`);
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""
logdestroy="""<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <div class="rendered-form">
    <div class="">
        <p access="false" id="control-8473927">Logout of other computers before proceeding.
            <br>
        </p>
    </div>
    
</div>
</html>
"""


@app.get("/",response_class=HTMLResponse)
async def get():
    return HTMLResponse(login)

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket)
    chk=True
    while chk:
        data = await websocket.receive_text()
        print("CLIENTID>>>",client_id)
        print("Data ",data)
        if data == 'SignalLogout':
            manager.disconnect(websocket)
            print("Current Active users: ", ActiveUser.username)
            print("Removing user: ",[re.findall(r'(\w+?)(\d+)', client_id)[0]][0][0])
            ActiveUser.username.remove([re.findall(r'(\w+?)(\d+)', client_id)[0]][0][0])
            print("new active users>>>",ActiveUser.username)
            chk = False
        else:
            await manager.broadcast(f"Client {client_id}: {data}")
    print("Outside loop")

#if __name__ == "__main__":
#    uvicorn.run(app, host="0.0.0.0", port=8000)

