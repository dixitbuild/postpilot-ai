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

UNIFY_TAGS_PROMPT_TEMPLATE = """You are an expert content taxonomist. Below is a list of topic tags collected from many LinkedIn posts. Many of them mean the same thing but are worded differently. Your job is to merge tags with the same meaning into one unified tag.

Examples of how to merge:
- "Job Hunting", "Job Search", "Job Switch" and "Job Seekers" all point to "Job Search"
- "Inspiration", "Drive" and "Motivation" all point to "Motivation"
- "Personal Growth", "Self Improvement" and "Self Development" all point to "Personal Growth"

Rules:
1. Every tag in the input list must appear exactly once as a key in the output, spelled exactly as given.
2. The value for each key is the unified tag it belongs to.
3. Merge tags only when they clearly mean the same topic. Keep different topics separate, for example "Leadership" and "Management" stay separate, and "Health" and "Mental Health" stay separate.
4. A tag that has no similar tag maps to itself, for example "Climate Change" maps to "Climate Change".
5. Unified tags must be 1 to 3 words long and written in Title Case, for example "Job Search", "Personal Finance".
6. When possible, use one of the existing tags from the list as the unified tag instead of inventing a new one.
7. Do not use hashtags (#), emojis, or punctuation in unified tags.

Output rules:
1. Return only a valid JSON object where each key is an input tag and each value is its unified tag.
2. Do not add any explanation, preamble, or markdown code fences.
3. The output must follow this format exactly:
{{"Job Hunting": "Job Search", "Job Switch": "Job Search", "Inspiration": "Motivation", "Motivation": "Motivation"}}

Tags:
{tags}
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


def get_unified_tags(processed_posts):
    unique_tags = set()
    for post in processed_posts:
        unique_tags.update(post["tags"])

    prompt = UNIFY_TAGS_PROMPT_TEMPLATE.format(tags=", ".join(sorted(unique_tags)))
    return call_llm(prompt)


def process_posts(raw_post_path=RAW_POST_PATH):
    posts = load_posts(raw_post_path)
    processed_posts = []
    for i, post in enumerate(posts):
        if i >5:
            break
        processed_posts.append(extract_metadata(post))

    unified_tags = get_unified_tags(processed_posts)
    for post in processed_posts:
        new_tags = []
        for tag in post["tags"]:
            unified_tag = unified_tags.get(tag, tag)
            if unified_tag not in new_tags:
                new_tags.append(unified_tag)
        post["tags"] = new_tags
    return processed_posts


if __name__ == "__main__":
    processed_posts = process_posts(RAW_POST_PATH)
    for post in processed_posts:
        print(post["name"], post["tags"])
