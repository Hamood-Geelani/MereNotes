from fastapi import APIRouter, Request, Form, Depends, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from models.note import Note
from config.db import conn
from schemas.note import noteEntity, notesEntity
from typing import Optional
from bson import ObjectId

# Initialize router and templates
note = APIRouter()
templates = Jinja2Templates(directory="templates")

@note.get("/", response_class=HTMLResponse)
async def read_item(request: Request, search: Optional[str] = None):
    # Create query based on search parameter
    query = {}
    if search:
        query = {"$or": [
            {"title": {"$regex": search, "$options": "i"}},
            {"desc": {"$regex": search, "$options": "i"}}
        ]}
    
    # Get documents from the collection based on query
    docs = conn.notes.notes.find(query)
    
    # Convert each document to a dictionary with the needed fields
    newDocs = []
    
    # Check if there are any documents
    for doc in docs:
        try:
            newDoc = {
                "id": str(doc.get("_id", "")),
                "title": doc.get("title", ""),
                "desc": doc.get("desc", ""),
                "important": doc.get("important", False)
            }
            newDocs.append(newDoc)
        except Exception as e:
            print(f"Error processing document: {e}")
    
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "newDocs": newDocs,
        "search": search or ""
    })

@note.post("/", response_class=HTMLResponse)
async def create_item(
    request: Request, 
    title: str = Form(...), 
    desc: str = Form(...), 
    important: Optional[str] = Form(None)
):
    # Create note document
    noteData = {
        "title": title,
        "desc": desc,
        "important": True if important else False
    }
    
    # Insert into database
    conn.notes.notes.insert_one(noteData)
    
        # Instead of calling read_item directly, redirect to the homepage
    return RedirectResponse(url="/", status_code=303)
    # Redirect to get route to display all notes
    return await read_item(request)

@note.get("/delete/{note_id}")
async def delete_note(note_id: str):
    # Delete the note
    conn.notes.notes.delete_one({"_id": ObjectId(note_id)})
    
    # Redirect to the home page
    return RedirectResponse(url="/", status_code=303)

@note.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}

# Add this route to your note.py file
@note.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})