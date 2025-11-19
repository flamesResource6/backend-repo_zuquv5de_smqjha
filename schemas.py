"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List

class Artist(BaseModel):
    """
    Artists collection schema
    Collection name: "artist"
    """
    name: str = Field(..., description="Artist display name")
    email: str = Field(..., description="Contact email")
    bio: Optional[str] = Field(None, description="Short bio")
    avatar_url: Optional[HttpUrl] = Field(None, description="Profile image URL")
    website: Optional[str] = Field(None, description="Personal site or portfolio")
    instagram: Optional[str] = Field(None, description="Instagram handle or URL")

class Artwork(BaseModel):
    """
    Artworks collection schema
    Collection name: "artwork"
    """
    title: str = Field(..., description="Artwork title")
    description: Optional[str] = Field(None, description="Artwork description")
    price: float = Field(..., ge=0, description="Price in USD")
    image_url: HttpUrl = Field(..., description="Primary image URL")
    artist_id: Optional[str] = Field(None, description="Reference to artist _id as string")
    artist_name: Optional[str] = Field(None, description="Display name of the artist")
    categories: List[str] = Field(default_factory=list, description="Tags/Categories")
    available: bool = Field(True, description="Is this available for purchase")
