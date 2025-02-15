# /// script
# requires-python = ">=3.13"
# dependencies = [
#        "fastapi",
#        "uvicorn",
#        "requests",
# ]
# ///

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
import os

app = FastAPI()

# Enable CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"]
)

# Define tools (Fixed Incorrect JSON Structure)
tools = [
    {
        "type": "function",
        "function": {
            "name": "script_runner",
            "description": "Install a package and run a script from a URL with provided arguments",
            "parameters": {
                "type": "object",
                "properties": {
                    "package_name": {
                        "type": "string",
                        "description": "The name of the package to install. Leave empty if installation is not required"
                    }
                }
            }
        }
    }
]

# Fetch API Proxy Token from Environment Variable
AIPROXY_TOKEN = os.getenv("AIPROXY_TOKEN")

@app.get("/")
def home():
    return {"message": "Yay TDS is awesome!"}

@app.get("/read")
def read_file(path: str):
    try:
        with open(path, "r") as f:
            return f.read()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File does not exist")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/run")
def task_runner(task: str):
    """Processes plain-English tasks using AI Proxy."""
    
    url = "https://aiproxy.sanand.workers.dev/openai/v1/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {AIPROXY_TOKEN}"
    }

    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": task
            },
            {
                "role": "system",
                "content": """
You are an assistant who has to do a variety of tasks.
If your task involves running a script, you can use the script_runner tool.
If your task involves writing code, you can use the task_runner tool.
"""
            }
        ]
    }

    try:
        response = requests.post(url=url, headers=headers, json=data)
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"API request failed: {str(e)}")

# Run the FastAPI app with Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


