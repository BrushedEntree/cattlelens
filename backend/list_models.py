import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get('GOOGLE_API_KEY')
if not api_key:
    print("GOOGLE_API_KEY not found in environment.")
else:
    genai.configure(api_key=api_key)
    try:
        with open('models.txt', 'w', encoding='utf-8') as f:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    f.write(m.name + '\n')
        print("Models written to models.txt")
    except Exception as e:
        print(f"Error listing models: {e}")
