from langchain.agents import create_agent
from .tool import get_score
import os
from dotenv import load_dotenv
load_dotenv()
MODEL_NAME = os.getenv("AI_MODEL_NAME", "gemini-1.5-flash")
if not os.getenv("GOOGLE_API_KEY") and os.getenv("GEMINI_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY")

SYSYTEM_PROMPT = """"
    You are a dedicated agent for the  Detecting Academic Procrastination Patterns.
    description: a system that analyses a sequence of a student's academic activities 
    and identifies patterns of procrastination. The system should identify when 
    repeated postponement or last-minute activity begins to appear and provide a simple explanation based on the student's activity history.
    You would get the inputs as:
    [
  {"task_id":"subj1","course":"Math","assigned":"2026-09-01T09:00","due":"2026-09-10T23:59","first_activity":"2026-09-02T18:00","submitted":"2026-09-09T21:00","reschedules":0},
  {"task_id":"subj2","course":"Physics","assigned":"2026-09-05T09:00","due":"2026-09-12T23:59","first_activity":"2026-09-12T20:00","submitted":"2026-09-13T00:20","reschedules":2}
]
and your output will be like this :
{"label":"emerging","onset_index":4,"onset_task":"A5","baseline":0.18,"tasks":[{"task_id":"subj1","course":"Math","score":0.71,"start_lag":0.95,"late":1,"reschedules":2}]}
use the get_score tool to get the details of all
"""
import json
import urllib.request
import urllib.error

class GeminiAgent:
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):
        self.api_key = api_key
        self.model_name = model_name

    def invoke(self, input_data: dict):
        messages = input_data.get("messages", [])
        prompt_text = messages[-1]["content"] if messages else ""
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
        payload = {
            "contents": [{
                "parts": [{"text": SYSYTEM_PROMPT + "\n\n" + prompt_text}]
            }]
        }
        
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        
        with urllib.request.urlopen(req, timeout=15) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            candidate_text = res_data["candidates"][0]["content"]["parts"][0]["text"]
            return candidate_text

api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
if api_key and api_key != "your_gemini_api_key_here":
    agent = GeminiAgent(api_key=api_key, model_name=MODEL_NAME)
else:
    class FallbackAgent:
        def invoke(self, *args, **kwargs):
            raise NotImplementedError("AI Agent API key not configured.")
    agent = FallbackAgent()

