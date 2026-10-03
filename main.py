import streamlit as st

from few_shot_posts import FewShotPosts
from llm_helper import call_llm

SIZE_OPTIONS = ["Small", "Medium", "Big"]
LANGUAGE_OPTIONS = ["English", "Hinglish"]
SIZE_WORD_RANGES = {
    "Small": "30 to 50 words",
    "Medium": "51 to 150 words",
    "Big": "151 to 300 words",
}
MAX_EXAMPLES = 3

GENERATE_POST_PROMPT_TEMPLATE = """You are an expert LinkedIn ghostwriter. Write one original LinkedIn post using the details below.

Post details:
- Topic: {tag}
- Writing style inspired by: {name}
- Length: {word_range}
- Language: {language}

Rules for the content:
1. The post must be clearly about the topic "{tag}".
2. Match the tone, voice, sentence style, and structure of {name}'s posts shown in the examples. Do not copy sentences from the examples.
3. Do not pretend to be {name}. Do not invent personal stories, achievements, numbers, or facts about {name} or their companies.
4. Start with a strong hook in the first line that makes people want to keep reading.
5. Use short paragraphs and line breaks so the post is easy to read on LinkedIn.
6. End with a clear takeaway, a question, or a call to action that invites engagement.
7. Stay within the length of {word_range}.

Rules for the language:
1. If the language is "English", write the full post in English.
2. If the language is "Hinglish", mix Hindi and English naturally, the way young Indian professionals talk. Write the Hindi words in English letters (Roman script), never in Devanagari script. Example: "Aaj ka din bahut productive tha, finally launched our product!"

Output rules:
1. Return only the post text.
2. Do not add a title, explanation, preamble, quotes around the post, or markdown formatting.
3. You may add up to 3 relevant hashtags at the end of the post.
{examples}"""


@st.cache_resource
def load_few_shot_posts():
    return FewShotPosts()


def get_few_shot_examples(fs, tag, name, size, language):
    # Try the strictest filters first, then relax them until some examples are found
    filter_options = [
        {"tag": tag, "name": name, "size": size, "language": language},
        {"tag": tag, "name": name, "language": language},
        {"name": name, "size": size, "language": language},
        {"name": name, "language": language},
        {"tag": tag, "size": size, "language": language},
        {"tag": tag, "language": language},
        {"name": name},
    ]
    for filters in filter_options:
        examples = fs.get_filtered_posts(**filters)
        if examples:
            return examples[:MAX_EXAMPLES]
    return []


def build_generate_post_prompt(tag, name, size, language, examples):
    examples_text = ""
    if examples:
        examples_text = "\nUse these example posts as a reference for writing style:\n"
        for i, post in enumerate(examples, start=1):
            examples_text += f"\nExample {i}:\n\"\"\"\n{post['text']}\n\"\"\"\n"

    return GENERATE_POST_PROMPT_TEMPLATE.format(
        tag=tag,
        name=name,
        word_range=SIZE_WORD_RANGES[size],
        language=language,
        examples=examples_text,
    )


def generate_post(fs, tag, name, size, language):
    examples = get_few_shot_examples(fs, tag, name, size, language)
    prompt = build_generate_post_prompt(tag, name, size, language, examples)
    return call_llm(prompt, temperature=0.7)


def main():
    st.set_page_config(page_title="PostPilot AI", page_icon="✍️")
    st.title("PostPilot AI")
    st.caption("Generate LinkedIn posts in the style of top influencers")

    fs = load_few_shot_posts()

    col1, col2 = st.columns(2)
    with col1:
        selected_tag = st.selectbox("Topic", options=fs.get_tags())
    with col2:
        selected_name = st.selectbox("Influencer", options=fs.get_names())

    col3, col4 = st.columns(2)
    with col3:
        selected_size = st.selectbox(
            "Size",
            options=SIZE_OPTIONS,
            help="Small: up to 50 words · Medium: 51–150 words · Big: more than 150 words",
        )
    with col4:
        selected_language = st.selectbox("Language", options=LANGUAGE_OPTIONS)

    if st.button("Generate", type="primary"):
        with st.spinner("Writing your post..."):
            post = generate_post(fs, selected_tag, selected_name, selected_size, selected_language)
        st.write(post)


if __name__ == "__main__":
    main()
