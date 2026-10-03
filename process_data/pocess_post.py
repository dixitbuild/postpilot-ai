import json
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

# RAW_POST_PATH = Path(__file__).resolve().parent.parent / "data" / "raw_post.json"
RAW_POST_PATH = "data/raw_post.json"
GROQ_MODEL = "openai/gpt-oss-120b"

groq_client = Groq()  # reads GROQ_API_KEY from the environment

METADATA_PROMPT_TEMPLATE = """You are an expert LinkedIn content analyst. Read the LinkedIn post below and extract its language and topic tags.

Rules for "language":
1. The value must be exactly "English" or "Hinglish". No other value is allowed.
2. "Hinglish" means the post mixes Hindi and English, for example "Aaj ka din bahut productive tha, finally launched our product!"
3. Hindi words written in English letters (Roman script) count as Hindi. Hindi written in Devanagari script also counts as Hindi.
4. If the post contains Hindi words or phrases used as part of a sentence, the language is "Hinglish".
5. Common Indian words that are widely used in English, like "crore", "lakh", "rupees" or "chai", do not make a post Hinglish on their own.
6. If the post is written fully in English, the language is "English".

Rules for "tags":
1. Return between 1 and 3 tags. Never return more than 3 tags.
2. Each tag must describe a main topic of the post, not a minor detail.
3. Each tag must be 1 to 3 words long and written in Title Case, for example "Leadership", "Personal Finance", "Mental Health".
4. Prefer broad, reusable topics over narrow ones, so the same tag can group many similar posts. For example, use "Startups" instead of "Bootstrapping My Second Startup".
5. Do not use hashtags (#), emojis, or punctuation in tags.
6. Do not use the author's name, company names, or brand names as tags.
7. Do not repeat the same idea twice, for example "Career" and "Career Growth" together.
8. Order the tags from most relevant to least relevant.

Output rules:
1. Return only a valid JSON object with exactly two keys: "language" and "tags".
2. Do not add any explanation, preamble, or markdown code fences.
3. The output must follow this format exactly:
{{"language": "English", "tags": ["Leadership", "Career Growth"]}}

LinkedIn post:
\"\"\"
{post_text}
\"\"\"
"""


def load_posts(raw_post_path):
    with open(raw_post_path, encoding="utf-8") as f:
        return json.load(f)


def build_metadata_prompt(post_text):
    return METADATA_PROMPT_TEMPLATE.format(post_text=post_text)


def call_llm(prompt):
    response = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0,
    )
    return json.loads(response.choices[0].message.content)


def extract_metadata(post):
    text = post["text"]
    # Extract metadata using python operations
    metadata = {
        "line_count": len(text.splitlines()),
        "word_count": len(text.split()),
        "char_count": len(text),
    }
    # Extract metadata using LLM
    prompt = build_metadata_prompt(text)
    llm_metadata = call_llm(prompt)
    metadata["language"] = llm_metadata["language"]
    metadata["tags"] = llm_metadata["tags"][:3]
    return {**post, **metadata}


def process_posts(raw_post_path=RAW_POST_PATH):
    posts = load_posts(raw_post_path)
    processed_posts = []
    for i, post in enumerate(posts):
        if i >5:
            break
        processed_posts.append(extract_metadata(post))
    return processed_posts


if __name__ == "__main__":
    for post in process_posts(RAW_POST_PATH):
        print(post)
