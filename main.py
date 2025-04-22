from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware  # Added this import
from pydantic import BaseModel
import requests
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Langflow Contract API",
    description="API for processing chat inputs through Langflow",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class ChatInput(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    session_id: str | None = None
    timestamp: str | None = None

# Langflow API configuration
LANGFLOW_API_URL = "https://api.langflow.astra.datastax.com/lf/ed6c45f6-6029-47a5-a6ee-86d7caf24d60/api/v1/run/da053891-67b1-449f-9f2e-6081bb8c6cc6"
APPLICATION_TOKEN = os.getenv("APPLICATION_TOKEN")

@app.get("/health")
async def health_check():
    """Health check endpoint for Railway"""
    return {"status": "healthy"}

@app.post("/chat", response_model=ChatResponse)
async def process_chat(input: ChatInput):
    """
    Process chat input through Langflow API
    """
    if not APPLICATION_TOKEN:
        raise HTTPException(
            status_code=500,
            detail="APPLICATION_TOKEN environment variable is not set"
        )

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {APPLICATION_TOKEN}"
    }

    payload = {
        "input_value": input.message,
        "output_type": "chat",
        "input_type": "chat"
    }

    try:
        response = requests.post(
            LANGFLOW_API_URL,
            json=payload,
            headers=headers
        )
        response.raise_for_status()
        
        # Parse the response JSON
        langflow_response = json.loads(response.text)
        
        # Extract the actual message from the nested structure
        if isinstance(langflow_response, dict):
            try:
                # Parse the outputs section
                outputs = langflow_response.get('outputs', [])[0].get('outputs', [])[0]
                results = outputs.get('results', {}).get('message', {})
                
                return ChatResponse(
                    response=results.get('text', ''),
                    session_id=results.get('session_id'),
                    timestamp=results.get('timestamp')
                )
            except (KeyError, IndexError):
                # If we can't parse the structure, return the raw text
                return ChatResponse(response=response.text)

    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error communicating with Langflow API: {str(e)}"
        )
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error parsing Langflow API response: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )

# Add this at the end of the file
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)