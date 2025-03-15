import streamlit as st
import sqlite3
import pandas as pd
import nltk
import google.generativeai as genai
from datetime import datetime
from streamlit_calendar import calendar

nltk.download("punkt")

# Set up Gemini API Key
GEMINI_API_KEY = "AIzaSyDzZaW-lhjkolxgg0RgV-hfBHaqel1t3Wk"  # 🔹 Replace with your API key
genai.configure(api_key=GEMINI_API_KEY)

# Database setup
conn = sqlite3.connect("journal.db", check_same_thread=False)
cursor = conn.cursor()

# Create journal table
cursor.execute('''CREATE TABLE IF NOT EXISTS journal (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    date TEXT,
                    entry TEXT,
                    sentiment REAL)''')
conn.commit()

# Function to analyze sentiment using Gemini API
def analyze_sentiment(text):
    prompt = f"Analyze the sentiment of this text: '{text}'. " \
             "Return a single word response as Positive, Negative, or Neutral."

    model = genai.GenerativeModel("gemini-1.5-pro-latest")
    response = model.generate_content(prompt)

    sentiment_text = response.text.strip().lower()

    # Convert response to polarity score
    if "positive" in sentiment_text:
        return 1.0  # Happy
    elif "negative" in sentiment_text:
        return -1.0  # Sad
    else:
        return 0.0  # Neutral

# Function to add a journal entry
def add_journal_entry(username, entry):
    date = datetime.now().strftime("%Y-%m-%d")
    sentiment = analyze_sentiment(entry)

    cursor.execute("INSERT INTO journal (username, date, entry, sentiment) VALUES (?, ?, ?, ?)",
                   (username, date, entry, sentiment))
    conn.commit()

# Function to get journal data
def get_journal_entries(username):
    return pd.read_sql("SELECT * FROM journal WHERE username = ? ORDER BY date DESC", conn, params=(username,))

# Function to get mood color and emoji
def get_mood(sentiment):
    if sentiment > 0.5:
        return "green", "😊 Happy"
    elif sentiment < -0.2:
        return "red", "😢 Sad"
    else:
        return "yellow", "😐 Neutral"

# Main function
def main():
    st.title("📝 Mood Journal & Tracker")

    username = st.text_input("Enter your username")

    menu = st.sidebar.radio("Your Journal", ["Journal", "Mood Tracker", "Past Entries"])

    if menu == "Journal":
        st.subheader("✍️ Write Your Daily Journal")
        journal_entry = st.text_area("How was your day?")

        if st.button("Save Entry"):
            if username and journal_entry:
                add_journal_entry(username, journal_entry)
                st.success("Your journal entry has been saved!")
            else:
                st.error("Please enter your username and journal entry.")

    elif menu == "Mood Tracker":
        st.subheader("📅 Mood Tracker Calendar")

        if username:
            entries = get_journal_entries(username)
            if not entries.empty:
                events = []
                for _, row in entries.iterrows():
                    mood_color, mood_emoji = get_mood(row["sentiment"])
                    events.append({
                        "title": f"{mood_emoji}",
                        "start": row["date"],
                        "color": mood_color
                    })

                calendar(events)
            else:
                st.info("No journal entries found. Start writing in your journal!")
        else:
            st.error("Please enter your username.")

    elif menu == "Past Entries":
        st.subheader("📖 Your Past Journal Entries")

        if username:
            entries = get_journal_entries(username)
            if not entries.empty:
                for _, row in entries.iterrows():
                    mood_color, mood_emoji = get_mood(row["sentiment"])
                    st.markdown(f"**📅 {row['date']} - {mood_emoji}**")
                    st.write(f"📝 {row['entry']}")
                    st.markdown("---")
            else:
                st.info("No past entries found. Start writing today!")
        else:
            st.error("Please enter your username.")

if __name__ == "__main__":
    main()
