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
images = pathlib.Path(__file__).parent.resolve() / "images"
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
def add_item(name: str = Form(...), category: str = Form(...), image: str = Form(...)):
    logger.info(f"Receive item: {name}, {category}, {image}")
    cur.execute("INSERT INTO items (name, category, image) VALUES (?,?,?)", (name, category, image))
    conn.commit()
    return {"message": f"item received: {name}"}

@app.get("/items")
def get_item():
    logger.info(f"Get a list of items")
    cur.execute("SELECT id, name, category, image FROM items")
    showcase = {"items": [{"id": id,  "name": name, "category": category, "image": image} for (id, name, category, image) in cur] }
    return showcase

@app.get("/items/{id}")
def get_item(id:str):
    print("Item id is " + id)
    logger.info(f"Get a list of items by id")
    cur.execute("SELECT * FROM items WHERE id IS " + id)
    showcase = {"items": [{"id": id,  "name": name, "category": category, "image": image} for (id, name, category, image) in cur] }
    return showcase

@app.get("/search")
def search_item(keyword: str):
    print(keyword)
    logger.info(f"Search in the list of items")
    cur.execute("SELECT * FROM items WHERE name LIKE (?)", (f'%{keyword}%',))
    showcase = {"items": [{"name": name, "category": category, "image": image} for (id, name, category, image) in cur] }
    return showcase


@app.get("/image/{image_filename}")
async def get_image(image_filename):
    # Create image path
    image = images / image_filename

    if not image_filename.endswith(".jpg"):
        raise HTTPException(status_code=400, detail="Image path does not end with .jpg")

    if not image.exists():
        logger.info(f"Image not found: {image}")
        image = images / "default.jpg"

    return FileResponse(image)
