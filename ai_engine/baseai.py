from langchain.agents import create_agent


SYSYTEM_PROMPT = """"
    You are a dedicated agent for the  Detecting Academic Procrastination Patterns.
    description: a system that analyses a sequence of a student's academic activities 
    and identifies patterns of procrastination. The system should identify when 
    repeated postponement or last-minute activity begins to appear and provide a simple explanation based on the student's activity history.
    You would get the inputs as the 
"""

agent = create_agent(
    model="",
    tools=[],
    system_prompt=SYSYTEM_PROMPT
)


