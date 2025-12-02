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

# Indian cattle and buffalo breeds database with detailed identification features
BREED_DATABASE = {
    "cattle": {
        "gir": {
            "name": "Gir",
            "origin": "Gujarat, India",
            "utility": "Milch - High milk yield (1400-2500 kg/lactation)",
            "traits": "Distinctive convex forehead bulge, large pendulous ears, lyre-shaped horns",
            "color": "Reddish-brown to white, sometimes with white patches",
            "horn_shape": "Lyre-shaped, curved backward and upward",
            "size": "Medium to large"
        },
        "sahiwal": {
            "name": "Sahiwal",
            "origin": "Punjab, India/Pakistan",
            "utility": "Milch - High milk yield (1400-2500 kg/lactation)",
            "traits": "Loose skin with prominent dewlap, drooping ears, lyre-shaped horns",
            "color": "Reddish dun to pale red",
            "horn_shape": "Lyre-shaped, medium length",
            "size": "Medium"
        },
        "red sindhi": {
            "name": "Red Sindhi",
            "origin": "Sindh, Pakistan (now in Indian farms)",
            "utility": "Milch - High milk fat and protein content",
            "traits": "Compact body, heat tolerant, red coat, medium build",
            "color": "Reddish to red",
            "horn_shape": "Short, thick horns",
            "size": "Medium"
        },
        "tharparkar": {
            "name": "Tharparkar",
            "origin": "Rajasthan (Thar Desert), India",
            "utility": "Dual purpose - Milk (1800-2600 kg/lactation) and draught",
            "traits": "Lyre-shaped horns, medium to large body, adapted to arid climate",
            "color": "White to light grey",
            "horn_shape": "Lyre-shaped, medium length",
            "size": "Medium to large"
        },
        "rathi": {
            "name": "Rathi",
            "origin": "Rajasthan, India",
            "utility": "Milch - Disease resistant, high milk fat",
            "traits": "Medium-sized, adapted to arid conditions, good body conformation",
            "color": "Reddish coat",
            "horn_shape": "Short to medium",
            "size": "Medium"
        },
        "kankrej": {
            "name": "Kankrej",
            "origin": "Gujarat-Rajasthan border, India",
            "utility": "Dual purpose - Draught and milk",
            "traits": "Large powerful body, lyrate horns, strong draught ability",
            "color": "Silver grey to iron grey or steel black",
            "horn_shape": "Lyre-shaped, long and curved",
            "size": "Large"
        },
        "ongole": {
            "name": "Ongole",
            "origin": "Andhra Pradesh, India",
            "utility": "Dual purpose - Draught and beef, good milk yield",
            "traits": "Large size, prominent hump, white coat, strong and sturdy",
            "color": "White to light grey",
            "horn_shape": "Short, thick horns",
            "size": "Large"
        },
        "hariana": {
            "name": "Hariana",
            "origin": "Haryana, Uttar Pradesh, India",
            "utility": "Dual purpose - Milk and draught",
            "traits": "White to grey coat, medium size, adaptable, good temperament",
            "color": "White to light grey",
            "horn_shape": "Small to medium, upward curved",
            "size": "Medium"
        },
        "kangayam": {
            "name": "Kangayam",
            "origin": "Tamil Nadu, India",
            "utility": "Draught and beef - powerful work animal",
            "traits": "Red color, compact powerful body, grey-black hooves",
            "color": "Red to dark red",
            "horn_shape": "Medium, curved backward",
            "size": "Medium"
        },
        "malvi": {
            "name": "Malvi",
            "origin": "Madhya Pradesh, India",
            "utility": "Draught - Strong work capacity",
            "traits": "White to grey coat, large body, strong build",
            "color": "White to grey",
            "horn_shape": "Medium, curved",
            "size": "Large"
        },
        "nagori": {
            "name": "Nagori",
            "origin": "Rajasthan, India",
            "utility": "Draught - Fast moving draught breed",
            "traits": "White coat, large size, long legs, strong",
            "color": "White",
            "horn_shape": "Medium to long, curved",
            "size": "Large"
        },
        "red kandhari": {
            "name": "Red Kandhari",
            "origin": "Maharashtra, India",
            "utility": "Milch - Good milk yield",
            "traits": "Red coat, strong build, good milk producer",
            "color": "Red",
            "horn_shape": "Medium, curved",
            "size": "Medium"
        },
        "khillari": {
            "name": "Khillari",
            "origin": "Maharashtra-Karnataka border, India",
            "utility": "Draught - Fast and powerful",
            "traits": "Grey-white body, black horns, athletic build",
            "color": "Grey-white",
            "horn_shape": "Long, sharp, black horns",
            "size": "Medium to large"
        },
        "hallikar": {
            "name": "Hallikar",
            "origin": "Karnataka, India",
            "utility": "Draught - Agricultural work",
            "traits": "Grey-white body, black horns, active temperament",
            "color": "Grey-white",
            "horn_shape": "Long, sharp, black horns",
            "size": "Medium"
        },
        "amrit mahal": {
            "name": "Amrit Mahal",
            "origin": "Karnataka, India",
            "utility": "Draught - Military transport (historical)",
            "traits": "White coat, strong and active, good endurance",
            "color": "White to grey",
            "horn_shape": "Long, sharp horns",
            "size": "Medium to large"
        }
    },
    "buffalo": {
        "murrah": {
            "name": "Murrah",
            "origin": "Haryana, Punjab, Delhi, India",
            "utility": "Premier dairy breed - 2000-2500 kg/lactation",
            "traits": "Jet black coat, tightly coiled horns, massive body, broad hips, well-developed udder",
            "color": "Jet black, sometimes white markings on face or tail",
            "horn_shape": "Short, tightly curled/coiled horns",
            "size": "Large (Bulls 550-600 kg, Females 450-550 kg)"
        },
        "mehsana": {
            "name": "Mehsana",
            "origin": "Gujarat (Mehsana district), India",
            "utility": "High milk yield - good dairy buffalo",
            "traits": "Black coat, medium-sized, wall-eyed appearance, good udder",
            "color": "Black",
            "horn_shape": "Medium, curved backward",
            "size": "Medium"
        },
        "jaffarabadi": {
            "name": "Jaffarabadi",
            "origin": "Gujarat (Coastal, Gulf of Khambhat), India",
            "utility": "Dual purpose - Milk (1500-2000 kg/lactation) and draught",
            "traits": "Very large massive body, massive dewlap, bulging forehead, broad semi-circular horns",
            "color": "Black",
            "horn_shape": "Thick, curved backward and upward forming semi-circle",
            "size": "Very large (heaviest Indian buffalo breed)"
        },
        "surti": {
            "name": "Surti",
            "origin": "Gujarat (Kaira and Baroda districts), India",
            "utility": "Rich milk - High fat content (8-12%), 1000-1300 kg/lactation",
            "traits": "Medium-sized, sickle-shaped horns, moderately long flat horns",
            "color": "Silver grey to rusty brown",
            "horn_shape": "Sickle-shaped, curved like a sickle",
            "size": "Medium"
        },
        "nagpuri": {
            "name": "Nagpuri",
            "origin": "Maharashtra (Nagpur region), India",
            "utility": "Dual purpose - Milk and draught",
            "traits": "Copper colored coat, medium-sized body, good for farm work",
            "color": "Copper to black",
            "horn_shape": "Medium, curved",
            "size": "Medium"
        },
        "banni": {
            "name": "Banni",
            "origin": "Gujarat (Banni grasslands, Kutch), India",
            "utility": "High milk in harsh conditions - Hardy breed",
            "traits": "Adapted to arid saline regions, medium-sized, good heat tolerance",
            "color": "Black to grey",
            "horn_shape": "Medium, curved",
            "size": "Medium"
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
    horn_shape: Optional[str] = None
    size: Optional[str] = None

class BreedSuggestion(BaseModel):
    breed: str
    confidence: str
    reasoning: str
    breed_info: Optional[BreedInfo] = None

class BreedRecognitionResponse(BaseModel):
    success: bool
    breed: Optional[str] = None
    animal_type: Optional[str] = None
    confidence: Optional[str] = None
    breed_info: Optional[BreedInfo] = None
    alternative_breeds: Optional[List[BreedSuggestion]] = None
    image_quality: Optional[str] = None
    error: Optional[str] = None

@api_router.get("/")
async def root():
    return {"message": "Cattle & Buffalo Breed Recognition API"}

@api_router.post("/recognize-breed", response_model=BreedRecognitionResponse)
async def recognize_breed(request: BreedRecognitionRequest):
    """
    Recognize cattle or buffalo breed from an image using Gemini AI with enhanced identification
    """
    try:
        # Get API key from environment
        api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not api_key:
            raise HTTPException(status_code=500, detail="API key not configured")
        
        # Create a unique session ID for this request
        session_id = str(uuid.uuid4())
        
        # Build detailed breed characteristics for AI
        breed_details = []
        for animal_type, breeds in BREED_DATABASE.items():
            for breed_key, info in breeds.items():
                breed_details.append(
                    f"{info['name']} ({animal_type}): {info['color']}, "
                    f"{info.get('horn_shape', 'N/A')} horns, {info.get('size', 'medium')} size, "
                    f"Key traits: {info['traits']}"
                )
        
        # Prepare enhanced system message with detailed breed characteristics
        system_message = f"""
You are an expert livestock veterinarian specializing in Indian cattle and buffalo breeds with deep knowledge of breed identification.

IDENTIFICATION GUIDELINES:
1. First assess IMAGE QUALITY - Is the animal clearly visible? Is lighting adequate? Rate as Good/Fair/Poor
2. Identify if it's CATTLE or BUFFALO based on body structure, horn shape, and facial features
3. Look for KEY IDENTIFICATION FEATURES:
   - COAT COLOR: Red, white, grey, black, brown, copper, silver
   - HORN SHAPE: Lyre-shaped, curved, straight, coiled, sickle-shaped, long/short
   - BODY SIZE: Large, medium, small
   - DISTINCTIVE FEATURES: Forehead bulge, pendulous ears, dewlap, hump, body build
   
BREED DATABASE WITH IDENTIFICATION FEATURES:
{chr(10).join(breed_details)}

RESPONSE FORMAT (MANDATORY):
Image Quality: [Good/Fair/Poor with brief explanation]
Animal Type: [cattle or buffalo]
Primary Breed: [exact breed name]
Confidence: [High/Medium/Low]
Reasoning: [specific visible features that led to identification - mention color, horn shape, size, distinctive traits]
Alternative Possibilities: [If confidence is not High, list 2-3 other possible breeds with brief reasoning]

IMPORTANT:
- If confidence is not High, you MUST provide alternative breed possibilities
- Be specific about visible features in your reasoning
- If image quality is poor, state it clearly and explain impact on identification
- For cross-breeds, mention possible parent breeds
- If the animal is not clearly visible or not cattle/buffalo, state so clearly
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
            text="Analyze this image carefully and identify the breed. Follow the response format exactly and provide alternative breeds if your confidence is not High.",
            file_contents=[image_content]
        )
        
        # Send message and get response
        logger.info(f"Sending breed recognition request for session {session_id}")
        response_text = await chat.send_message(user_message)
        logger.info(f"Received response: {response_text[:300]}...")
        
        # Parse the response
        animal_type = None
        breed = None
        confidence = None
        image_quality = "Good"
        alternative_text = ""
        
        lines = response_text.split('\n')
        for line in lines:
            line = line.strip()
            if 'Image Quality:' in line:
                image_quality = line.split(':', 1)[1].strip()
            elif 'Animal Type:' in line:
                animal_type = line.split(':', 1)[1].strip().lower()
            elif 'Primary Breed:' in line or 'Breed:' in line:
                breed = line.split(':', 1)[1].strip()
            elif 'Confidence:' in line:
                confidence = line.split(':', 1)[1].strip()
            elif 'Alternative Possibilities:' in line or 'Alternative Breeds:' in line:
                alternative_text = line.split(':', 1)[1].strip()
        
        # Get primary breed information from database
        breed_info = None
        if animal_type and breed:
            breed_lower = breed.lower()
            if animal_type in BREED_DATABASE:
                for key, info in BREED_DATABASE[animal_type].items():
                    if key in breed_lower or breed_lower in key or key.replace(' ', '') in breed_lower.replace(' ', ''):
                        breed_info = BreedInfo(**info)
                        breed = info['name']
                        break
        
        # Parse alternative breeds
        alternative_breeds = []
        if alternative_text and alternative_text.lower() not in ['none', 'n/a', 'not applicable']:
            # Try to extract breed names from alternative text
            alt_parts = alternative_text.split(',')
            for alt_part in alt_parts[:3]:  # Max 3 alternatives
                alt_part = alt_part.strip()
                if alt_part and len(alt_part) > 2:
                    # Try to find breed in database
                    alt_breed_info = None
                    alt_breed_name = None
                    if animal_type and animal_type in BREED_DATABASE:
                        for key, info in BREED_DATABASE[animal_type].items():
                            if key in alt_part.lower() or info['name'].lower() in alt_part.lower():
                                alt_breed_info = BreedInfo(**info)
                                alt_breed_name = info['name']
                                break
                    
                    if alt_breed_name:
                        alternative_breeds.append(BreedSuggestion(
                            breed=alt_breed_name,
                            confidence="Low to Medium",
                            reasoning=alt_part,
                            breed_info=alt_breed_info
                        ))
        
        return BreedRecognitionResponse(
            success=True,
            breed=breed or "Unknown",
            animal_type=animal_type or "unknown",
            confidence=confidence or "Medium",
            breed_info=breed_info,
            alternative_breeds=alternative_breeds if alternative_breeds else None,
            image_quality=image_quality
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
