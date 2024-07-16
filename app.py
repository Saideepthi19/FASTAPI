from urllib import request
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from jwtsign import sign, decode


from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import inspect

DATABASE_URL = "sqlite:///./sql_app.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread" : False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base=declarative_base()

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

class User(Base):
    __tablename__ = "users"
    firstname = Column(String, index=True)
    lastname = Column(String, index=True)
    email = Column(String, index=True, primary_key=True)
    password = Column(String, index=True)


app=FastAPI()

userlist=[]

class SignUpSchema(BaseModel):
    firstname: str = "someoneidk"
    lastname: str = "someoneidk"
    email: str = "someone@something.com"
    password: str = "somethingidk"

class SignInSchema(BaseModel):
    email: str = "someone@something.com"
    password: str = "somethingidk"


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)




@app.post("/signup")
def sign_up(request: SignUpSchema, db: Session = Depends(get_db)):
    user_in_db = db.query(User).filter(User.email == request.email).first()
    if user_in_db:
        raise HTTPException(status_code=400, detail="Email already registered.")

    new_user = User(firstname=request.firstname, lastname = request.lastname, email=request.email, password=request.password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token=sign(request.email)
    return token




@app.post("/signin")
def sign_in(request: SignInSchema, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if user and user.password == request.password:
        token = sign(user.email)
        return token
    else:
        raise HTTPException(status_code=400, detail="Incorrect Email or Password.")



@app.post("/authtest")
def auth_test(decoded: str = Depends(decode)):
    return decoded


@app.get("/check-table")
def check_table():
    inspector = inspect(engine)
    table=inspector.get_table_names()
    if table:
        return {"status" : "Table exists", "table" : table}
    else:
        return {"status" : "No table found"}