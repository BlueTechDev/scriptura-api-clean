from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID")

client = OpenAI(api_key=OPENAI_API_KEY)

def generate_openai_response(query: str, context: str = "") -> str:
    try:
        thread = client.beta.threads.create()
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=ASSISTANT_ID,
            messages=[
                {"role": "user", "content": query}
            ]
        )

        # Poll until run completes (simple version)
        import time
        while run.status != "completed":
            time.sleep(1)
            run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

        messages = client.beta.threads.messages.list(thread_id=thread.id)
        return messages.data[0].content[0].text.value.strip()

    except Exception as e:
        print(f"🔥 OpenAI Assistants API Error: {e}")
        raise
