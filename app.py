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

if "idea_generated" not in st.session_state:
    st.session_state.idea_generated = False

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
                "You are a short-form video concept developer for a content brand called Dad Games, targeting adult gamers—especially dads in their 30s and 40s—who juggle parenting, relationships, and their love of gaming.\n\n"
                "These videos are short (under 60s), emotionally resonant, and structured for TikTok, Instagram Reels, and YouTube Shorts. They are built on relatable conflict, nostalgic hooks, and exaggerated or petty emotional reversals.\n\n"
                "The goal is to provoke comment-worthy reactions like: 'This is literally me.' or 'Tag your squad.'\n\n"
                "Your job is to take any combination of fragments—title, hook, twist, general idea—and generate a complete, structured video concept using this format:\n\n"
                "**Text Overlay Hook (3–6 words)**: The first text viewers see. Must be bold, emotional, and specific.\n"
                "**Setup**: The relatable normal moment (e.g., bedtime’s done, squad chat is full).\n"
                "**Twist / Punchline**: What goes wrong, petty, or ironic (e.g., squad betrayal, guilt trap, bedtime sabotage).\n"
                "**Call to Action**: A line that encourages viewers to tag someone, comment their version, or argue about what’s fair.\n"
                "**Hashtags**: Use a mix of brand-specific (#DadGames), emotional (#RelatableAF), niche (#GamingAfterKids), and viral-friendly tags.\n"
                "**Suggested Description**: Write like a TikTok/IG caption. Be short, honest, and funny. No hashtags here—just a voice the viewer would trust.\n\n"
                "Tone should be slightly petty, emotionally honest, and playful. It should sound like a dad who's half-burnt-out, half-determined to play games anyway. Every video must feel emotionally legible in the first 3 seconds.\n\n"
                "If only a few inputs are provided, fill in the rest using strong, structured defaults that would resonate with this audience."
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

            st.session_state.idea_generated = True

        except Exception as e:
            st.error(f"OpenAI API Error: {e}")
