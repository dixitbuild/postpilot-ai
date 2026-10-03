import json

import pandas as pd

ENRICHED_POST_PATH = "data/enriched_post.json"


class FewShotPosts:
    def __init__(self, file_path=ENRICHED_POST_PATH):
        self.df = None
        self.unique_tags = None
        self.load_posts(file_path)

    def load_posts(self, file_path):
        with open(file_path, encoding="utf-8") as f:
            posts = json.load(f)
        self.df = pd.json_normalize(posts)
        self.unique_tags = sorted(self.df["tags"].explode().dropna().unique())

    def get_tags(self):
        return self.unique_tags

    def get_filtered_posts(self, language=None, tag=None):
        df = self.df
        if language:
            df = df[df["language"] == language]
        if tag:
            df = df[df["tags"].apply(lambda tags: tag in tags)]
        return df.to_dict(orient="records")


if __name__ == "__main__":
    fs = FewShotPosts()
    print(fs.df)
    print(fs.get_tags())
    print(fs.get_filtered_posts(language="English", tag="Leadership"))
