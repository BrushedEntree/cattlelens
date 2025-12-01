from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone
import base64
from emergentintegrations.llm.chat import LlmChat, UserMessage, ImageContent

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'test_database')]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Indian cattle and buffalo breeds database
BREED_DATABASE = {
    "cattle": {
        "gir": {
            "name": "Gir",
            "origin": "Gujarat, India",
            "utility": "Milk production (10-12 liters/day)",
            "traits": "Distinctive forehead bulge, long pendulous ears",
            "color": "Red and white or sometimes black and white"
        },
        "sahiwal": {
            "name": "Sahiwal",
            "origin": "Punjab, Pakistan/India",
            "utility": "High milk yield (8-10 liters/day)",
            "traits": "Loose skin, drooping ears, reddish dun color",
            "color": "Reddish dun to red"
        },
        "red sindhi": {
            "name": "Red Sindhi",
            "origin": "Sindh, Pakistan",
            "utility": "Dual purpose - milk and draught",
            "traits": "Compact body, red color, heat tolerant",
            "color": "Red"
        },
        "tharparkar": {
            "name": "Tharparkar",
            "origin": "Rajasthan, India",
            "utility": "Dual purpose - milk and draught",
            "traits": "White or light grey, medium-sized",
            "color": "White to light grey"
        },
        "rathi": {
            "name": "Rathi",
            "origin": "Rajasthan, India",
            "utility": "Dual purpose breed",
            "traits": "Medium-sized, adapted to arid conditions",
            "color": "White with black or brown patches"
        },
        "kankrej": {
            "name": "Kankrej",
            "origin": "Gujarat, India",
            "utility": "Draught and milk production",
            "traits": "Large, powerful, lyrate horns",
            "color": "Silver grey to iron grey or steel black"
        },
        "ongole": {
            "name": "Ongole",
            "origin": "Andhra Pradesh, India",
            "utility": "Draught and beef",
            "traits": "Large size, white or grey color, prominent hump",
            "color": "White or light grey"
        },
        "hariana": {
            "name": "Hariana",
            "origin": "Haryana, India",
            "utility": "Dual purpose - milk and draught",
            "traits": "White or light grey, small horns",
            "color": "White or light grey"
        },
        "kangayam": {
            "name": "Kangayam",
            "origin": "Tamil Nadu, India",
            "utility": "Draught and beef",
            "traits": "Red color, compact body, powerful",
            "color": "Red"
        }
    },
    "buffalo": {
        "murrah": {
            "name": "Murrah",
            "origin": "Haryana, India",
            "utility": "High milk production (12-15 liters/day)",
            "traits": "Jet black, tightly coiled horns, heavy body",
            "color": "Jet black"
        },
        "mehsana": {
            "name": "Mehsana",
            "origin": "Gujarat, India",
            "utility": "High milk yield",
            "traits": "Black coat, medium-sized, wall-eyed",
            "color": "Black"
        },
        "jaffarabadi": {
            "name": "Jaffarabadi",
            "origin": "Gujarat, India",
            "utility": "Heavy milk production",
            "traits": "Massive build, bulging forehead, drooping horns",
            "color": "Black"
        },
        "surti": {
            "name": "Surti",
            "origin": "Gujarat, India",
            "utility": "High butterfat content milk",
            "traits": "Medium-sized, sickle-shaped horns",
            "color": "Black or brown"
        },
        "nagpuri": {
            "name": "Nagpuri",
            "origin": "Maharashtra, India",
            "utility": "Dual purpose - milk and draught",
            "traits": "Copper colored, medium-sized",
            "color": "Copper to black"
        },
        "banni": {
            "name": "Banni",
            "origin": "Gujarat, India",
            "utility": "High milk production in harsh conditions",
            "traits": "Adapted to arid regions, medium-sized",
            "color": "Black or grey"
        }
    }
}

# Define Models
class BreedRecognitionRequest(BaseModel):
    image_base64: str
    animal_type: Optional[str] = None  # "cattle" or "buffalo" - optional hint

class BreedInfo(BaseModel):
    name: str
    origin: str
    utility: str
    traits: str
    color: str

class BreedRecognitionResponse(BaseModel):
    success: bool
    breed: Optional[str] = None
    animal_type: Optional[str] = None
    confidence: Optional[str] = None
    breed_info: Optional[BreedInfo] = None
    error: Optional[str] = None

@api_router.get("/")
async def root():
    return {"message": "Cattle & Buffalo Breed Recognition API"}

@api_router.post("/recognize-breed", response_model=BreedRecognitionResponse)
async def recognize_breed(request: BreedRecognitionRequest):
    """
    Recognize cattle or buffalo breed from an image using Gemini AI
    """
    try:
        # Get API key from environment
        api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not api_key:
            raise HTTPException(status_code=500, detail="API key not configured")
        
        # Create a unique session ID for this request
        session_id = str(uuid.uuid4())
        
        # Prepare the system message with breed database knowledge
        system_message = f"""
You are an expert livestock veterinarian specializing in Indian cattle and buffalo breeds.
Your task is to analyze images and identify the breed accurately.

You have knowledge of these Indian breeds:
CATTLE: {', '.join(BREED_DATABASE['cattle'].keys())}
BUFFALO: {', '.join(BREED_DATABASE['buffalo'].keys())}

Provide your response in this exact format:
Animal Type: [cattle or buffalo]
Breed: [exact breed name from the database]
Confidence: [High/Medium/Low]
Reasoning: [brief explanation of identifying features]

If it's a cross-breed, mention the possible parent breeds.
If the image quality is poor or the animal is not clearly visible, state that.
"""
        
        # Initialize Gemini chat
        chat = LlmChat(
            api_key=api_key,
            session_id=session_id,
            system_message=system_message
        )
        
        # Use Gemini 2.5 Flash for image analysis
        chat.with_model("gemini", "gemini-2.5-flash")
        
        # Create image content from base64
        image_content = ImageContent(image_base64=request.image_base64)
        
        # Create user message with image
        user_message = UserMessage(
            text="Please analyze this image and identify the breed of this animal. Provide the animal type, breed name, confidence level, and key identifying features.",
            file_contents=[image_content]
        )
        
        # Send message and get response
        logger.info(f"Sending breed recognition request for session {session_id}")
        response_text = await chat.send_message(user_message)
        logger.info(f"Received response: {response_text[:200]}...")
        
        # Parse the response
        animal_type = None
        breed = None
        confidence = None
        
        lines = response_text.split('\n')
        for line in lines:
            if 'Animal Type:' in line:
                animal_type = line.split(':')[1].strip().lower()
            elif 'Breed:' in line:
                breed = line.split(':')[1].strip()
            elif 'Confidence:' in line:
                confidence = line.split(':')[1].strip()
        
        # Get breed information from database
        breed_info = None
        if animal_type and breed:
            # Try to match breed name (case-insensitive)
            breed_lower = breed.lower()
            if animal_type in BREED_DATABASE:
                for key, info in BREED_DATABASE[animal_type].items():
                    if key in breed_lower or breed_lower in key:
                        breed_info = BreedInfo(**info)
                        breed = info['name']  # Use standardized name
                        break
        
        return BreedRecognitionResponse(
            success=True,
            breed=breed or "Unknown",
            animal_type=animal_type or "unknown",
            confidence=confidence or "Medium",
            breed_info=breed_info
        )
        
    except Exception as e:
        logger.error(f"Error in breed recognition: {str(e)}")
        return BreedRecognitionResponse(
            success=False,
            error=str(e)
        )

@api_router.get("/breeds")
async def get_breeds():
    """
    Get list of all supported breeds
    """
    return {
        "cattle": list(BREED_DATABASE["cattle"].values()),
        "buffalo": list(BREED_DATABASE["buffalo"].values())
    }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
