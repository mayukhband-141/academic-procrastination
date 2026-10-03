from langchain.agents import create_agent
from .tool import get_score
import os

MODEL_NAME = os.getenv("AI_MODEL_NAME", "gpt-4o")
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
try:
    agent = create_agent(
        model=MODEL_NAME,
        tools=[get_score],
        system_prompt=SYSYTEM_PROMPT,
    )
except Exception:
    class FallbackAgent:
        def invoke(self, *args, **kwargs):
            raise NotImplementedError("AI Agent model not configured. Using fallback calculation.")
    agent = FallbackAgent()

