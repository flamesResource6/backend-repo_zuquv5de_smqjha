import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Artist, Artwork

app = FastAPI(title="Art Commerce API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Art Commerce Backend Running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = getattr(db, 'name', "✅ Connected")
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    return response

# Helper to convert Mongo _id to string

def serialize_doc(doc: dict):
    if not doc:
        return doc
    doc = dict(doc)
    _id = doc.get("_id")
    if isinstance(_id, ObjectId):
        doc["id"] = str(_id)
        del doc["_id"]
    return doc

# Schemas for creation

class ArtistCreate(Artist):
    pass

class ArtworkCreate(Artwork):
    pass

# Public Endpoints

@app.get("/artists", response_model=List[dict])
def list_artists(limit: int = 50):
    docs = get_documents("artist", {}, limit)
    return [serialize_doc(d) for d in docs]

@app.post("/artists", response_model=dict)
def create_artist(artist: ArtistCreate):
    inserted_id = create_document("artist", artist)
    doc = db["artist"].find_one({"_id": ObjectId(inserted_id)})
    return serialize_doc(doc)

@app.get("/artworks", response_model=List[dict])
def list_artworks(category: Optional[str] = None, limit: int = 100):
    query = {}
    if category:
        query = {"categories": {"$in": [category]}}
    docs = get_documents("artwork", query, limit)
    return [serialize_doc(d) for d in docs]

@app.post("/artworks", response_model=dict)
def create_artwork(artwork: ArtworkCreate):
    # If artist_id provided, try to store a display name snapshot
    data = artwork.model_dump()
    artist_id = data.get("artist_id")
    if artist_id:
        try:
            artist_doc = db["artist"].find_one({"_id": ObjectId(artist_id)})
            if artist_doc:
                data["artist_name"] = artist_doc.get("name")
        except Exception:
            pass
    inserted_id = create_document("artwork", data)
    doc = db["artwork"].find_one({"_id": ObjectId(inserted_id)})
    return serialize_doc(doc)

@app.get("/artworks/featured", response_model=List[dict])
def featured_artworks(limit: int = 8):
    docs = db["artwork"].find({"available": True}).sort("created_at", -1).limit(limit)
    return [serialize_doc(d) for d in docs]

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
