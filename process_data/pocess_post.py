import json
from pathlib import Path

# RAW_POST_PATH = Path(__file__).resolve().parent.parent / "data" / "raw_post.json"
RAW_POST_PATH = "data/raw_post.json"

def load_posts(raw_post_path):
    with open(raw_post_path, encoding="utf-8") as f:
        return json.load(f)


def extract_metadata(post):
    text = post["text"]
    metadata = {
        "line_count": len(text.splitlines()),
        "word_count": len(text.split()),
        "char_count": len(text),
    }
    return {**post, **metadata}


def process_posts():
    posts = load_posts()
    processed_posts = []
    for post in posts:
        processed_posts.append(extract_metadata(post))
    return processed_posts


if __name__ == "__main__":
    for post in process_posts():
        print(post)
