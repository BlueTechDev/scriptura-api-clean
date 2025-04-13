from openai import OpenAI
import os
from dotenv import load_dotenv
import traceback

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID")

print(f"🔑 Loaded key prefix: {OPENAI_API_KEY[:10]}")  # DEBUG LINE

client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = (
    "You are a biblical assistant specializing in Christian theology, providing structured, well-formatted responses."
    "\n\n### **Guidelines for Response Formatting:**"
    "\n- **Use headings** (###) to separate topics."
    "\n- **Use bullet points** (-) for key details."
    "\n- **Bold important text** (**bold**) for clarity."
    "\n\n### **Core Theological Guidelines**"
    "- Strictly rely on the Bible and doctrinally sound sources."
    "- Never speculate or fabricate information."
    "- Maintain a warm, conversational, and approachable tone while ensuring doctrinal accuracy."
    "- If a question surpasses human reasoning, direct users to consult their pastor."
    "\n\n### **Handling Non-Biblical Questions**"
    "- If asked about topics unrelated to theology, respond in a **friendly and conversational tone**, while reinforcing the focus on Scripture."
)

def generate_openai_response(query: str, context: str = "") -> str:
    try:
        # Step 1: Create a thread
        thread = client.beta.threads.create()

        # Step 2: Add user message
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=query
        )

        # Step 3: Run the assistant
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=ASSISTANT_ID
        )

        # Step 4: Poll for status
        while True:
            run_status = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            if run_status.status == "completed":
                break
            elif run_status.status == "failed":
                raise RuntimeError("OpenAI Assistant run failed.")
            time.sleep(1)

        # Step 5: Get messages
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        last_message = messages.data[0]

        return last_message.content[0].text.value.strip()

    except Exception as e:
        print(f"🔥 OpenAI Assistants API Error: {e}")
        raise