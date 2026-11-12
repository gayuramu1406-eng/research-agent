import os
from groq import Groq
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

resp = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[
        {
            "role": "user",
            "content": "Say hello and nothing else"
        }
    ]
)

print(resp.choices[0].message.content)