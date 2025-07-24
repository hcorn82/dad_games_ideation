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

# --- Flexible Input Section ---
st.subheader("💡 Input anything you're thinking — we’ll build around it")

raw_thought = st.text_area("🧠 Stream of Consciousness / General Idea", placeholder="Dump your messy idea here...")

title = st.text_input("📛 Video Title (Optional)")
hook = st.text_input("🎯 Text Overlay / Hook (Optional)")
setup = st.text_area("🎬 Setup (Optional)", height=100)
twist = st.text_area("💥 Twist / Punchline (Optional)", height=100)
cta = st.text_input("📣 Call to Action (Optional)")
hashtags = st.text_input("🏷 Hashtags (Optional)")

# --- Load Idea Section ---
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
            title, hook, setup, twist, cta, hashtags = data
            st.experimental_rerun()

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
                "These videos are short (under 60s), emotionally resonant, and structured for TikTok, Instagram Reels, and YouTube Shorts. They are built on relatable conflict, nostalgic hooks, and exaggerated or petty emotional reversals. The goal is to provoke comment-worthy reactions, such as:\n"
                "- 'This is literally me.'\n"
                "- 'Tag your squad.'\n"
                "- 'I’ve lived this EXACT moment.'\n\n"
                "Your job is to take any combination of fragments—title, hook, twist, general idea—and generate a complete, structured video concept using this format:\n\n"
                "**Text Overlay Hook** (3–6 words):\nThe first text viewers see. Must be bold, emotional, and specific.\n\n"
                "**Setup**:\nThe relatable normal moment (e.g., bedtime’s done, squad chat is full).\n\n"
                "**Twist / Punchline**:\nWhat goes wrong, petty, or ironic (e.g., squad betrayal, guilt trap, bedtime sabotage).\n\n"
                "**Call to Action**:\nA line that encourages viewers to tag someone, comment their version, or argue about what’s fair.\n\n"
                "**Hashtags**:\nUse a mix of brand-specific (#DadGames), emotional (#RelatableAF), niche (#GamingAfterKids), and viral-friendly tags.\n\n"
                "**Suggested Description**:\nWrite like a TikTok/IG caption. Be short, honest, and funny. No hashtags here—just a voice the viewer would trust.\n\n"
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

            idea_output = response.choices[0].message.content

            st.subheader("📋 Generated Video Blueprint")
            st.markdown(idea_output)

        except Exception as e:
            st.error(f"OpenAI API Error: {e}")

# --- Save to Idea Vault ---
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
