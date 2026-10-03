import json

import pandas as pd

ENRICHED_POST_PATH = "data/enriched_post.json"

# Post size by word count
SMALL_POST_MAX_WORDS = 50    # Small: up to 50 words
MEDIUM_POST_MAX_WORDS = 150  # Medium: 51 to 150 words, Big: more than 150 words


class FewShotPosts:
    def __init__(self, file_path=ENRICHED_POST_PATH):
        self.df = None
        self.unique_tags = None
        self.load_posts(file_path)

    def load_posts(self, file_path):
        with open(file_path, encoding="utf-8") as f:
            posts = json.load(f)
        self.df = pd.json_normalize(posts)
        self.df["size"] = self.df["word_count"].apply(self.categorize_size)
        self.unique_tags = sorted(self.df["tags"].explode().dropna().unique())

    def categorize_size(self, word_count):
        if word_count <= SMALL_POST_MAX_WORDS:
            return "Small"
        if word_count <= MEDIUM_POST_MAX_WORDS:
            return "Medium"
        return "Big"

    def get_tags(self):
        return self.unique_tags

    def get_filtered_posts(self, language=None, tag=None, name=None, size=None):
        df = self.df
        if name:
            df = df[df["name"] == name]
        if size:
            df = df[df["size"] == size]
        if language:
            df = df[df["language"] == language]
        if tag:
            df = df[df["tags"].apply(lambda tags: tag in tags)]
        return df.to_dict(orient="records")


if __name__ == "__main__":
    fs = FewShotPosts()
    print(fs.df)
    print(fs.get_tags())
    print(fs.get_filtered_posts(language="English", tag="Leadership", name="Simon Sinek", size="Small"))
