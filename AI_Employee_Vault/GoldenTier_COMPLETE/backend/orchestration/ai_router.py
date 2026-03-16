import os
from dotenv import load_dotenv
import anthropic

load_dotenv()

client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

def simple_fallback(task):
    task_lower = task.lower()
    if "$" in task or "dollar" in task_lower or "payment" in task_lower:
        return "accounting"
    elif "summary" in task_lower or "report" in task_lower:
        return "executive"
    else:
        return "operations"

def route_task(task_content):
    try:
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=50,
            messages=[
                {
                    "role": "user",
                    "content": f"""
You are a company AI task router.

Choose ONLY one word:
- accounting
- operations
- executive

Task:
{task_content}
"""
                }
            ],
        )

        result = response.content[0].text.strip().lower()

        if result not in ["accounting", "operations", "executive"]:
            return simple_fallback(task_content)

        return result

    except Exception as e:
        print("⚠️ Claude error, using fallback:", e)
        return simple_fallback(task_content)