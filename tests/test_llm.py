import os
from dotenv import load_dotenv
load_dotenv()

try:
    from langgraph_agent_lab.llm import get_llm
    print("Testing LLM API Key...")
    llm = get_llm()
    result = llm.invoke("Hello, say 'API key works!'")
    print("Success! LLM Response:")
    print(result.content)
except Exception as e:
    print(f"Error testing API key: {e}")
