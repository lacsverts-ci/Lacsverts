from fastapi import FastAPI, APIRouter, HTTPException, Depends, File, UploadFile, Header, Form
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime
import base64
import httpx
import json

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Data Models
class Lake(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    latitude: float
    longitude: float
    status: str = "propre"  # "propre", "à surveiller", "pollué"
    description: str = ""
    region: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class LakeCreate(BaseModel):
    name: str
    latitude: float
    longitude: float
    status: str = "propre"
    description: str = ""
    region: str = ""

class Report(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    lake_id: str
    user_id: str
    user_name: str
    description: str
    image_base64: Optional[str] = None
    video_base64: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "pending"  # "pending", "reviewed", "resolved"

class ReportCreate(BaseModel):
    lake_id: str
    description: str
    image_base64: Optional[str] = None
    video_base64: Optional[str] = None

class AwarenessPost(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    content: str
    image_base64: Optional[str] = None
    video_base64: Optional[str] = None
    author_id: str
    author_name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_published: bool = True

class AwarenessPostCreate(BaseModel):
    title: str
    content: str
    image_base64: Optional[str] = None
    video_base64: Optional[str] = None

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    name: str
    picture: str = ""
    session_token: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_admin: bool = False

# Authentication helper
async def get_current_user(x_session_id: str = Header(None)):
    if not x_session_id:
        raise HTTPException(status_code=401, detail="Session ID required")
    
    user = await db.users.find_one({"session_token": x_session_id})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    return User(**user)

async def get_admin_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

# Initialize with sample data
@api_router.on_event("startup")
async def startup_event():
    # Check if lakes collection is empty and add sample data
    lake_count = await db.lakes.count_documents({})
    if lake_count == 0:
        sample_lakes = [
            {
                "id": str(uuid.uuid4()),
                "name": "Lac de Kossou",
                "latitude": 7.0,
                "longitude": -5.5,
                "status": "propre",
                "description": "Plus grand lac artificiel de Côte d'Ivoire",
                "region": "Région de Yamoussoukro",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Lac Buyo",
                "latitude": 6.5,
                "longitude": -7.0,
                "status": "à surveiller",
                "description": "Lac de barrage important pour l'électricité",
                "region": "Région de San-Pédro",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Lac de Taabo",
                "latitude": 6.2,
                "longitude": -5.2,
                "status": "propre",
                "description": "Lac artificiel sur le fleuve Bandama",
                "region": "Région de Dimbokro",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Lac de Ayamé",
                "latitude": 5.5,
                "longitude": -3.2,
                "status": "pollué",
                "description": "Lac nécessitant une attention particulière",
                "region": "Région d'Aboisso",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        ]
        await db.lakes.insert_many(sample_lakes)

# Authentication routes
@api_router.post("/auth/profile")
async def authenticate_user(x_session_id: str = Header(None)):
    if not x_session_id:
        raise HTTPException(status_code=400, detail="Session ID required")
    
    # Call Emergent auth API
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data",
                headers={"X-Session-ID": x_session_id}
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=401, detail="Invalid session")
            
            user_data = response.json()
            
            # Save or update user in database
            existing_user = await db.users.find_one({"email": user_data["email"]})
            if existing_user:
                # Update session token
                await db.users.update_one(
                    {"email": user_data["email"]},
                    {"$set": {"session_token": user_data["session_token"]}}
                )
                user = User(**existing_user)
                user.session_token = user_data["session_token"]
            else:
                # Create new user
                user = User(
                    email=user_data["email"],
                    name=user_data["name"],
                    picture=user_data["picture"],
                    session_token=user_data["session_token"]
                )
                await db.users.insert_one(user.dict())
            
            return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authentication error: {str(e)}")

# Lake routes
@api_router.get("/lakes", response_model=List[Lake])
async def get_lakes():
    lakes = await db.lakes.find().to_list(1000)
    return [Lake(**lake) for lake in lakes]

@api_router.get("/lakes/{lake_id}", response_model=Lake)
async def get_lake(lake_id: str):
    lake = await db.lakes.find_one({"id": lake_id})
    if not lake:
        raise HTTPException(status_code=404, detail="Lake not found")
    return Lake(**lake)

@api_router.put("/lakes/{lake_id}/status")
async def update_lake_status(lake_id: str, status: str, current_user: User = Depends(get_admin_user)):
    if status not in ["propre", "à surveiller", "pollué"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    result = await db.lakes.update_one(
        {"id": lake_id},
        {"$set": {"status": status, "updated_at": datetime.utcnow()}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Lake not found")
    
    return {"message": "Status updated successfully"}

# Report routes
@api_router.post("/reports", response_model=Report)
async def create_report(report: ReportCreate, current_user: User = Depends(get_current_user)):
    report_dict = report.dict()
    report_obj = Report(
        **report_dict,
        user_id=current_user.id,
        user_name=current_user.name
    )
    await db.reports.insert_one(report_obj.dict())
    return report_obj

@api_router.get("/reports", response_model=List[Report])
async def get_reports(current_user: User = Depends(get_current_user)):
    reports = await db.reports.find().sort("created_at", -1).to_list(1000)
    return [Report(**report) for report in reports]

@api_router.get("/reports/lake/{lake_id}", response_model=List[Report])
async def get_reports_by_lake(lake_id: str):
    reports = await db.reports.find({"lake_id": lake_id}).sort("created_at", -1).to_list(1000)
    return [Report(**report) for report in reports]

# Awareness routes
@api_router.post("/awareness", response_model=AwarenessPost)
async def create_awareness_post(post: AwarenessPostCreate, current_user: User = Depends(get_admin_user)):
    post_dict = post.dict()
    awareness_obj = AwarenessPost(
        **post_dict,
        author_id=current_user.id,
        author_name=current_user.name
    )
    await db.awareness_posts.insert_one(awareness_obj.dict())
    return awareness_obj

@api_router.get("/awareness", response_model=List[AwarenessPost])
async def get_awareness_posts():
    posts = await db.awareness_posts.find({"is_published": True}).sort("created_at", -1).to_list(1000)
    return [AwarenessPost(**post) for post in posts]

@api_router.delete("/awareness/{post_id}")
async def delete_awareness_post(post_id: str, current_user: User = Depends(get_admin_user)):
    result = await db.awareness_posts.delete_one({"id": post_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"message": "Post deleted successfully"}

# Root route
@api_router.get("/")
async def root():
    return {"message": "Lacs Verts API"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()