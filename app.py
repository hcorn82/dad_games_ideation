import streamlit as st
import sqlite3
from openai import OpenAI

# --- Setup ---
st.set_page_config(page_title="Dad Games Idea Builder", layout="wide")
st.title("🎮 Dad Games Flexible Idea Builder")

# --- Connect to SQLite ---
conn = sqlite3.connect("ideas.db", check_same_thread=False)
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS ideas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        hook TEXT,
        setup TEXT,
        twist TEXT,
        cta TEXT,
        hashtags TEXT
    )
''')
conn.commit()

# --- Initialize Session State ---
if "form_data" not in st.session_state:
    st.session_state.form_data = {
        "title": "",
        "hook": "",
        "setup": "",
        "twist": "",
        "cta": "",
        "hashtags": ""
    }

# --- Flexible Input Section ---
st.subheader("💡 Input anything you're thinking — we’ll build around it")

raw_thought = st.text_area("🧠 Stream of Consciousness / General Idea", placeholder="Dump your messy idea here...")

title = st.text_input("📛 Video Title (Optional)", value=st.session_state.form_data["title"])
hook = st.text_input("🎯 Text Overlay / Hook (Optional)", value=st.session_state.form_data["hook"])
setup = st.text_area("🎬 Setup (Optional)", height=100, value=st.session_state.form_data["setup"])
twist = st.text_area("💥 Twist / Punchline (Optional)", height=100, value=st.session_state.form_data["twist"])
cta = st.text_input("📣 Call to Action (Optional)", value=st.session_state.form_data["cta"])
hashtags = st.text_input("🏷 Hashtags (Optional)", value=st.session_state.form_data["hashtags"])

# --- OpenAI Key ---
openai_api_key = st.secrets.get("OPENAI_API_KEY", None)
if not openai_api_key:
    st.info("No OpenAI API key found in secrets. Please enter it manually for this session.")
    openai_api_key = st.text_input("Enter your OpenAI API key", type="password")

# --- Remix Helper ---
def remix_section(prompt, section_name):
    try:
        client = OpenAI(api_key=openai_api_key)
        remix_prompt = f"Rewrite the {section_name} of this video idea in a funnier, more surprising, and emotionally specific way: {prompt}"
        remix_response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert in punchy short-form storytelling."},
                {"role": "user", "content": remix_prompt}
            ]
        )
        return remix_response.choices[0].message.content
    except Exception as e:
        return f"Error remixing {section_name}: {e}"

# --- Idea Synthesizer ---
if st.button("🧠 Build My Video Concept"):
    if not openai_api_key:
        st.warning("Missing API key.")
    elif not any([raw_thought, title, hook, setup, twist, cta, hashtags]):
        st.warning("Enter at least one idea input.")
    else:
        try:
            client = OpenAI(api_key=openai_api_key)

            user_message = (
                f"Raw Thought: {raw_thought}\n\n"
                f"Video Title: {title}\n"
                f"Text Overlay Hook: {hook}\n"
                f"Setup: {setup}\n"
                f"Twist: {twist}\n"
                f"CTA: {cta}\n"
                f"Hashtags: {hashtags}"
            )

            system_prompt = (
                "You are a short-form video concept developer for a content brand called Dad Games... [TRUNCATED for clarity in update] ..."
            )

            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ]
            )

            idea_output = response.choices[0].message.content.split("**")
            output_dict = {idea_output[i].strip(): idea_output[i+1].strip() for i in range(1, len(idea_output)-1, 2)}

            st.session_state.form_data.update({
                "hook": output_dict.get("Text Overlay Hook", st.session_state.form_data["hook"]),
                "setup": output_dict.get("Setup", st.session_state.form_data["setup"]),
                "twist": output_dict.get("Twist / Punchline", st.session_state.form_data["twist"]),
                "cta": output_dict.get("Call to Action", st.session_state.form_data["cta"]),
                "hashtags": output_dict.get("Hashtags", st.session_state.form_data["hashtags"])
            })

        except Exception as e:
            st.error(f"OpenAI API Error: {e}")

# --- Always Show Output Section ---
st.subheader("📋 Generated Video Blueprint")
st.text_input("🎯 Hook", value=st.session_state.form_data["hook"])

col1, col2 = st.columns([4, 1])
with col1:
    new_setup = st.text_area("🎬 Setup", value=st.session_state.form_data["setup"], height=100)
with col2:
    if st.button("🔁 Remix Setup"):
        st.session_state.form_data["setup"] = remix_section(new_setup, "setup")

col3, col4 = st.columns([4, 1])
with col3:
    new_twist = st.text_area("💥 Twist", value=st.session_state.form_data["twist"], height=100)
with col4:
    if st.button("🔁 Remix Twist"):
        st.session_state.form_data["twist"] = remix_section(new_twist, "twist")

col5, col6 = st.columns([4, 1])
with col5:
    new_cta = st.text_input("📣 Call to Action", value=st.session_state.form_data["cta"])
with col6:
    if st.button("🔁 Remix CTA"):
        st.session_state.form_data["cta"] = remix_section(new_cta, "call to action")

st.text_input("🏷 Hashtags", value=st.session_state.form_data["hashtags"])

if st.button("💾 Save This Concept"):
    c.execute("INSERT INTO ideas (title, hook, setup, twist, cta, hashtags) VALUES (?, ?, ?, ?, ?, ?)",
              (title, st.session_state.form_data["hook"], st.session_state.form_data["setup"],
               st.session_state.form_data["twist"], st.session_state.form_data["cta"], st.session_state.form_data["hashtags"]))
    conn.commit()
    st.success("Concept saved!")

# --- Load and View Saved Ideas ---
st.markdown("---")
st.subheader("📂 Load a Saved Idea")
c.execute("SELECT id, title FROM ideas ORDER BY id DESC")
idea_options = c.fetchall()

if idea_options:
    selected = st.selectbox("Choose an idea to load", [f"{row[0]} - {row[1]}" for row in idea_options])
    if st.button("📥 Load Selected Idea"):
        idea_id = int(selected.split(" - ")[0])
        c.execute("SELECT title, hook, setup, twist, cta, hashtags FROM ideas WHERE id = ?", (idea_id,))
        data = c.fetchone()
        if data:
            st.session_state.form_data = {
                "title": data[0],
                "hook": data[1],
                "setup": data[2],
                "twist": data[3],
                "cta": data[4],
                "hashtags": data[5]
            }
            st.success("Idea loaded into input fields.")

st.subheader("📦 Saved Ideas")
c.execute("SELECT * FROM ideas ORDER BY id DESC")
rows = c.fetchall()
for row in rows:
    st.markdown(f"### {row[1]}")
    st.markdown(f"- **Hook**: {row[2]}")
    st.markdown(f"- **Setup**: {row[3]}")
    st.markdown(f"- **Twist**: {row[4]}")
    st.markdown(f"- **CTA**: {row[5]}")
    st.markdown(f"- **Hashtags**: {row[6]}")
    st.markdown("---")
