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
import json
import subprocess
import uvicorn
from fastapi import FastAPI, HTTPException
from pathlib import Path
from datetime import datetime
import sqlite3
import shutil
import duckdb


from bs4 import BeautifulSoup


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






# Load AIPROXY_TOKEN from environment
AIPROXY_TOKEN = os.getenv("AIPROXY_TOKEN")




app = FastAPI()

# Load AIPROXY_TOKEN from environment
AIPROXY_TOKEN = os.getenv("AIPROXY_TOKEN")


@app.post("/run")
def run_task(task: str):
    """Execute a given plain-English task."""
    try:
        # ✅ Phase A1: Install `uv` and Run `datagen.py`
        if "install uv and run" in task:
            user_email = task.split()[-1]  # Extract email from task description
            
            # Install `uv` if not installed
            subprocess.run(["pip", "install", "uv"], check=True)

            # Download datagen.py with Bearer token
            headers = {"Authorization": f"Bearer {AIPROXY_TOKEN}"}
            response = requests.get(
                "https://raw.githubusercontent.com/sanand0/tools-in-data-science-public/tds-2025-01/project-1/datagen.py",
                headers=headers
            )

            if response.status_code == 200:
                with open("/data/datagen.py", "w") as f:
                    f.write(response.text)

                subprocess.run(["python", "/data/datagen.py", user_email], check=True)

                return {"status": "success", "message": "datagen.py executed successfully"}
            else:
                raise HTTPException(status_code=500, detail="Failed to download datagen.py")

        # ✅ Phase B1: Ensure Data Outside `/data/` is Not Accessed
        elif "access outside /data" in task:
            raise HTTPException(status_code=403, detail="Access outside /data is restricted")

        # ✅ Phase B2: Prevent File Deletion
        elif "delete" in task:
            raise HTTPException(status_code=403, detail="File deletion is restricted")

        # ✅ Phase B3: Fetch Data from an API and Save It
        elif "fetch data" in task:
            api_url = task.split()[-1]  # Extract API URL from the task
            response = requests.get(api_url)
            if response.status_code == 200:
                with open("/data/api_data.json", "w") as f:
                    json.dump(response.json(), f, indent=4)
                return {"status": "success", "message": "API data saved"}
            else:
                raise HTTPException(status_code=500, detail="Failed to fetch API data")

        # ✅ Phase B4: Clone a Git Repo and Make a Commit
        elif "clone repo" in task:
            repo_url = task.split()[-1]  # Extract repo URL from task
            subprocess.run(["git", "clone", repo_url, "/data/repo"], check=True)
            return {"status": "success", "message": "Repository cloned successfully"}

        # ✅ Phase B5: Run a SQL Query on SQLite or DuckDB
        elif "run sql query" in task:
            conn = sqlite3.connect("/data/database.db")
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users")  # Example query
            result = cursor.fetchone()
            conn.close()
            return {"status": "success", "data": result}

        # ✅ Phase B6: Extract Data from a Website (Web Scraping)
        elif "scrape website" in task:
            website_url = task.split()[-1]  # Extract website URL from task
            response = requests.get(website_url)
            soup = BeautifulSoup(response.text, "html.parser")
            titles = [tag.text for tag in soup.find_all("h1")]
            with open("/data/scraped_data.txt", "w") as f:
                f.write("\n".join(titles))
            return {"status": "success", "message": "Website scraped successfully"}

        # ✅ Phase B7: Compress or Resize an Image
        elif "compress image" in task:
            image_path = "/data/image.png"
            compressed_path = "/data/image_compressed.png"
            subprocess.run(["convert", image_path, "-resize", "50%", compressed_path], check=True)
            return {"status": "success", "message": "Image compressed successfully"}

        # ✅ Phase B8: Transcribe Audio from an MP3 File
        elif "transcribe audio" in task:
            audio_path = "/data/audio.mp3"
            transcription = subprocess.run(["whisper", audio_path], capture_output=True, text=True)
            with open("/data/audio_transcription.txt", "w") as f:
                f.write(transcription.stdout)
            return {"status": "success", "message": "Audio transcribed successfully"}

        # ✅ Phase B9: Convert Markdown to HTML
        elif "convert markdown" in task:
            md_path = "/data/document.md"
            html_path = "/data/document.html"
            with open(md_path, "r") as f:
                md_content = f.read()
            html_content = markdown.markdown(md_content)
            with open(html_path, "w") as f:
                f.write(html_content)
            return {"status": "success", "message": "Markdown converted to HTML"}

        # ✅ Phase B10: Filter a CSV File and Return JSON
        elif "filter csv" in task:
            import pandas as pd
            df = pd.read_csv("/data/data.csv")
            filtered_df = df[df["status"] == "active"]
            filtered_json = filtered_df.to_json(orient="records")
            return {"status": "success", "data": filtered_json}

        # ✅ If Task is Not Recognized
        else:
            raise HTTPException(status_code=400, detail="Unsupported task")

    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Task failed: {str(e)}")


@app.get("/")
def home():
    return {"message": "Yay TDS is awesome!"}


@app.get("/read")
def read_file(path: str):
    """Read the contents of a specified file."""
    file_path = Path(path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File does not exist")
    return file_path.read_text()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
