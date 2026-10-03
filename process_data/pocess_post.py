import json
from pathlib import Path

# RAW_POST_PATH = Path(__file__).resolve().parent.parent / "data" / "raw_post.json"
RAW_POST_PATH = "data/raw_post.json"

def load_posts():
    with open(RAW_POST_PATH, encoding="utf-8") as f:
        return json.load(f)



if __name__ == "__main__":
    posts = load_posts()
    for post in posts:
        print(post)
