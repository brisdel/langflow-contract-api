from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Langflow Contract API",
    description="API for processing chat inputs through Langflow",
    version="1.0.0"
)

class ChatInput(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

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
        
        return ChatResponse(response=response.text)

    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error communicating with Langflow API: {str(e)}"
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