import os
import sqlite3
import logging
import pathlib
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
logger = logging.getLogger("uvicorn")
logger.level = logging.INFO
origins = [ os.environ.get('FRONT_URL', 'http://localhost:3000') ]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET","POST"],
    allow_headers=["*"],
)

dbname = "mercari.sqlite3"
conn = sqlite3.connect(dbname, check_same_thread=False)
cur = conn.cursor()

@app.get("/")
def root():
    return {"message": "Hello, my first API!"}
    
@app.post("/items")
def add_item(name: str = Form(...), category: str = Form(...)):
    logger.info(f"Receive item: {name}, {category}")
    cur.execute("INSERT INTO items (name, category) VALUES (?,?)", (name, category))
    conn.commit()
    conn.close()
    return {"message": f"item received: {name}"}

@app.get("/items")
def get_item():
    logger.info(f"Get a list of items")
    cur.execute("SELECT id, name, category FROM items")
    showcase = {"items": [{"id": item_id,  "name": name, "category": category} for (item_id, name, category) in cur] }
    conn.close()
    return showcase

@app.get("/search")
def search_item(keyword: str):
    print(keyword)
    logger.info(f"Search in the list of items")
    cur.execute("SELECT * FROM items WHERE name LIKE (?)", (f'%{keyword}%',))
    showcase = {"items": [{"name": name, "category": category} for (item_id, name, category) in cur] }
    conn.close()
    return showcase
