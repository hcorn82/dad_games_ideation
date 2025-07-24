
import streamlit as st
import sqlite3
import openai

# --- Setup ---
st.set_page_config(page_title="Dad Games Idea Generator", layout="wide")
st.title("🎮 Dad Games Idea Generator")

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

# --- Form Inputs ---
st.subheader("🧠 Create a New Video Idea")

with st.form("idea_form"):
    title = st.text_input("Video Title")
    hook = st.text_input("Text Overlay / Hook")
    setup = st.text_area("Setup")
    twist = st.text_area("Twist / Punchline")
    cta = st.text_input("Call to Action")
    hashtags = st.text_input("Hashtags")

    submitted = st.form_submit_button("💾 Save Idea")
    if submitted:
        c.execute("INSERT INTO ideas (title, hook, setup, twist, cta, hashtags) VALUES (?, ?, ?, ?, ?, ?)", 
                  (title, hook, setup, twist, cta, hashtags))
        conn.commit()
        st.success("Idea saved!")

# --- OpenAI Hook Punch-up (optional) ---
st.subheader("✨ Punch Up Hook (Optional AI Assist)")
openai_api_key = st.text_input("Enter OpenAI API Key", type="password")
prompt_input = st.text_input("Hook to improve")

if st.button("🔁 Improve Hook"):
    if openai_api_key and prompt_input:
        openai.api_key = openai_api_key
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a punchy short-form video writer. Make this hook more emotionally charged, relatable, or funny."},
                {"role": "user", "content": prompt_input}
            ]
        )
        improved_hook = response['choices'][0]['message']['content']
        st.text_area("Improved Hook", value=improved_hook, height=100)
    else:
        st.warning("Please enter your OpenAI API key and a hook to improve.")

# --- View Saved Ideas ---
st.subheader("📚 Saved Ideas")
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
