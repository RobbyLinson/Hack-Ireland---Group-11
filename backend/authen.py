from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from service.jwttoken import create_access_token
from service.oauth import get_current_user
from service.hashing import Hash
from database import conn
from schemas import User, UserResponse
from models import Users

auth = APIRouter()

@auth.get("/users", response_model=list[UserResponse])
async def retrieve_all_user():
    users = conn.execute(Users.select()).fetchall()
    return [dict(user._mapping) for user in users]

@auth.get("/user/{id}", response_model=UserResponse)
async def retrieve_one_user(id: int):
    user = conn.execute(Users.select().where(Users.c.id == id)).fetchone()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return dict(user._mapping)

@auth.patch("/user/{id}", response_model=list[UserResponse])
async def update_user_data(id: int, req: User):
    conn.execute(Users.update().values(
        username=req.username,
        email=req.email,
    ).where(Users.c.id == id))
    users = conn.execute(Users.select()).fetchall()
    return [dict(user._mapping) for user in users]

@auth.delete("/user/{id}", response_model=list[UserResponse])
async def delete_user_data(id: int):
    conn.execute(Users.delete().where(Users.c.id == id))
    users = conn.execute(Users.select()).fetchall()
    return [dict(user._mapping) for user in users]

@auth.post('/register', response_model=list[UserResponse])
def create_user(req: User):
    conn.execute(Users.insert().values(
        username=req.username,
        email=req.email,
        is_superuser=req.is_superuser,
        password=Hash.bcrypt(req.password)
    ))
    users = conn.execute(Users.select()).fetchall()
    return [dict(user._mapping) for user in users]

@auth.post('/login')
def login(req: OAuth2PasswordRequestForm = Depends()):
    user = conn.execute(Users.select().where(Users.c.username == req.username)).fetchone()
    if not user:
        raise HTTPException(status_code=404, detail=f"No user found with this {req.username} username")
    if not Hash.verify(user[-1], req.password):
        raise HTTPException(status_code=401, detail="Wrong Username or password")
    access_token = create_access_token(data={"username": user[1], "email": user[2], "is_superuser": user[3]})
    return {"access_token": access_token, "token_type": "bearer", "id": user[0]}

@auth.get("/verify_token", response_model=UserResponse)
def read_root(current_user: User = Depends(get_current_user)):
    return current_user

@auth.patch("/change_superuser/{id}", response_model=list[UserResponse])
def change_superuser(id: int, req: User):
    if req.is_superuser:
        conn.execute(Users.update().values(is_superuser=False).where(Users.c.id == id))
    else:
        conn.execute(Users.update().values(is_superuser=True).where(Users.c.id == id))
    users = conn.execute(Users.select()).fetchall()
    return [dict(user._mapping) for user in users]