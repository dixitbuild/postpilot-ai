import json

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GROQ_MODEL = "openai/gpt-oss-120b"

groq_client = Groq()  # reads GROQ_API_KEY from the environment


def call_llm(prompt, json_output=False, temperature=0):
    request = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
    }
    if json_output:
        request["response_format"] = {"type": "json_object"}

    response = groq_client.chat.completions.create(**request)
    content = response.choices[0].message.content
    return json.loads(content) if json_output else content.strip()
