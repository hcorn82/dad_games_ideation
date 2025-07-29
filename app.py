import streamlit as st
import sqlite3

# --- Setup ---
st.set_page_config(page_title="Dad Games Viral Builder", layout="wide")
st.title("🎮 Dad Games Viral Video Builder")

# --- Connect to SQLite ---
conn = sqlite3.connect("ideas.db", check_same_thread=False)
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS ideas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mode TEXT,
        title TEXT,
        hook TEXT,
        setup TEXT,
        twist TEXT,
        cta TEXT,
        hashtags TEXT,
        description TEXT
    )
''')
conn.commit()

# --- Session State Init ---
if "mode" not in st.session_state:
    st.session_state.mode = "Quick Idea Mode"

mode = st.radio("Select Mode:", ["Quick Idea Mode", "Workbook Mode"], horizontal=True)
st.session_state.mode = mode

def save_idea(mode, title, hook, setup, twist, cta, hashtags, description):
    c.execute("INSERT INTO ideas (mode, title, hook, setup, twist, cta, hashtags, description) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
              (mode, title, hook, setup, twist, cta, hashtags, description))
    conn.commit()
    st.success("Concept saved!")

# --- Quick Idea Mode ---
if mode == "Quick Idea Mode":
    st.subheader("💡 Quick Build: Input anything you're thinking")
    raw_thought = st.text_area("🧠 Dump your idea", placeholder="What dumb frustration are we turning into a viral hit?")
    col1, col2 = st.columns(2)
    with col1:
        title = st.text_input("📛 Video Title")
        hook = st.text_input("🎯 Hook")
        cta = st.text_input("📣 Call to Action")
    with col2:
        hashtags = st.text_input("🏷 Hashtags")
        description = st.text_area("📝 Suggested Description", height=100)
    setup = st.text_area("🎬 Setup", height=100)
    twist = st.text_area("💥 Twist", height=100)

    if st.button("💥 Generate + Save"):
        save_idea("Quick", title, hook, setup, twist, cta, hashtags, description)

# --- Workbook Mode ---
else:
    st.subheader("🧩 Workbook Mode: Walk through the full blueprint")
    st.markdown("Answer each section below. We’ll stitch together your idea into a viral-ready post.")

    with st.expander("🎯 Phase 1: Viral Trigger"):
        emotion = st.selectbox("Pick a dominant emotion", ["🤬 Frustration", "😂 Absurdity", "😢 Loss", "🤯 Surprise", "😤 Righteousness"])
        trigger_note = st.text_area("What’s the emotional shrapnel?", placeholder="E.g., wife scheduled dinner over raid night")

    with st.expander("📬 Phase 2: Sharable Premise"):
        conflict = st.text_input("Recognizable conflict", placeholder="He bailed on game night… again")
        overreaction = st.text_input("Overreaction", placeholder="You're killing him!")
        petty_stakes = st.text_input("Petty stakes / fallout", placeholder="Just one hawk tuah, is that too much??")

    with st.expander("🪞 Phase 3: The ‘You’ Test"):
        you_line = st.text_input("What’s the callout line?", placeholder="You’re the reason he doesn’t rank up.")

    with st.expander("🧰 Phase 4: Toolkit Pick"):
        format_choice = st.radio("Choose a video delivery format", ["🎭 Meme Remix", "📹 On-Cam Skit", "🎧 VO Reaction", "🎬 Movie Clip + Text"])

    with st.expander("📣 Phase 5: Comment Bait"):
        bait = st.text_input("What will get people typing?", placeholder="Tag someone who bailed on game night.")

    with st.expander("🔥 CTRL-ALT-DELETE Jam"):
        ctrl = st.text_area("CTRL – What’s the real-life frustration?", height=80)
        alt = st.text_area("ALT – What absurd lens could we use?", height=80)
        delete = st.text_area("DELETE – What’s the emotional collapse?", height=80)

    if st.button("🧠 Save Workbook Concept"):
        full_hook = f"{emotion} — {you_line}"
        full_setup = f"Conflict: {conflict}\nOverreaction: {overreaction}\nPetty Fallout: {petty_stakes}\nCTRL: {ctrl}\nALT: {alt}"
        full_twist = f"DELETE: {delete}"
        full_description = f"{format_choice} | {trigger_note}"
        save_idea("Workbook", "", full_hook, full_setup, full_twist, bait, "", full_description)

# --- Saved Ideas ---
st.markdown("---")
st.subheader("📦 Saved Concepts")
c.execute("SELECT * FROM ideas ORDER BY id DESC")
rows = c.fetchall()
for row in rows:
    st.markdown(f"### [{row[1]} Mode] {row[2] or '(Untitled)'}")
    st.markdown(f"- **Hook**: {row[3]}")
    st.markdown(f"- **Setup**: {row[4]}")
    st.markdown(f"- **Twist**: {row[5]}")
    st.markdown(f"- **CTA**: {row[6]}")
    st.markdown(f"- **Hashtags**: {row[7]}")
    st.markdown(f"- **Description**: {row[8]}")
    st.markdown("---")
