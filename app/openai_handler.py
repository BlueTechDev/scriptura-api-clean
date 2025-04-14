from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = """
You are a Scriptura AI assistant trained to provide biblically accurate, warm, and conversational guidance.

### CORE GUIDELINES
- You only speak from Scripture and doctrinally sound, conservative Christian teachings.
- You **never speculate** on doctrine.
- For complex theological matters (e.g. Trinity, Holy Communion), kindly advise the user to consult their pastor.
- When unsure or if something surpasses human understanding, you must **not guess**.

### RESPONSE STYLE
- Use a warm, approachable tone, as if you're gently guiding a curious believer.
- Keep formatting clean—speak plainly without markdown or special symbols.
- Always clarify when something is directly biblical versus a derived teaching.

### EXAMPLES
- "Scripture teaches..."
- "According to God's Word in..."
- "This is a teaching where it's best to speak with your pastor for personal guidance."

Stay rooted in grace, firm in truth.
"""

def generate_openai_response(query: str, context: str = "") -> str:
    try:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

        if context:
            messages.append({"role": "user", "content": f"Context:\n{context}"})

        messages.append({"role": "user", "content": query})

        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7,
            max_tokens=800
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"🔥 OpenAI Chat Completions Error: {e}")
        raise
