from openai import OpenAI
import os
from dotenv import load_dotenv
import traceback

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

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
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if context:
        messages.append({"role": "user", "content": f"**Context:**\n{context}"})
    messages.append({"role": "user", "content": query})

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            max_tokens=800
        )
        return response.choices[0].message.content.strip().replace("\n", "\n\n")

    except Exception as e:
        print("🔥 OpenAI exception occurred:")
        traceback.print_exc()
        raise
