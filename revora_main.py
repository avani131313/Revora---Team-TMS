import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import therapy
import journal
import json
import os
from moderation import is_content_appropriate

# Database setup
conn = sqlite3.connect("community.db", check_same_thread=False)
cursor = conn.cursor()

# Create tables if they don't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    bio TEXT)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    content TEXT,
                    likes INTEGER DEFAULT 0,
                    timestamp TEXT)''')

conn.commit()


# Function to add a new user
def add_user(username, bio):
    cursor.execute("INSERT INTO users (username, bio) VALUES (?, ?)", (username, bio))
    conn.commit()


# Function to check if a user exists
def user_exists(username):
    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    return cursor.fetchone() is not None


# Function to add a post with moderation
def add_post(username, content):
    if not is_content_appropriate(content):
        st.error("🚫 Your post contains inappropriate content. Please revise it.")
        return

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO posts (username, content, timestamp) VALUES (?, ?, ?)", (username, content, timestamp))
    conn.commit()
    st.success("Your post has been shared!")


# Function to get all posts
def get_posts():
    return pd.read_sql("SELECT * FROM posts ORDER BY timestamp DESC", conn)


# Function to like a post
def like_post(post_id):
    cursor.execute("UPDATE posts SET likes = likes + 1 WHERE id = ?", (post_id,))
    conn.commit()


# Memory Book Setup
MEMORY_BOOK_FILE = "memory_book.json"


def load_memory_book():
    if os.path.exists(MEMORY_BOOK_FILE):
        with open(MEMORY_BOOK_FILE, "r") as file:
            return json.load(file)
    return {}


def save_memory_book(data):
    with open(MEMORY_BOOK_FILE, "w") as file:
        json.dump(data, file, indent=4)


#Memory Book Page
def memory_book_main():
    st.title("📖 Memory Book")
    st.text("Write heartfelt messages for someone special.")

    recipient = st.text_input("Who is this message for?")
    sender = st.text_input("Your name:")
    message = st.text_area("Write your message:")

    if st.button("Save Message"):
        if recipient and sender and message:
            memory_book = load_memory_book()
            if recipient not in memory_book:
                memory_book[recipient] = []

            memory_book[recipient].append({"sender": sender, "message": message})
            save_memory_book(memory_book)
            st.success("Message saved successfully!")
        else:
            st.error("Please fill out all fields.")

    st.header("📜 View Messages")
    recipient_to_view = st.text_input("Enter the name of the person to see their messages:")

    if st.button("Show Messages"):
        memory_book = load_memory_book()
        if recipient_to_view in memory_book:
            st.subheader(f"Messages for {recipient_to_view}:")
            for entry in memory_book[recipient_to_view]:
                st.markdown(f"**{entry['sender']}**: {entry['message']}")
        else:
            st.warning("No messages found for this person.")


# Home Page
def home():
    st.image("logo.png", width=600)
    st.title("🌸 Welcome to Revora 🌸")
    st.markdown("""
    ### Where Every Emotion Finds a Voice 💖
    Revora is a **community platform** for individuals facing terminal illnesses and mental health struggles. Here, you can:

    -  **Express your thoughts** in a personal journal  
    -  **Share and receive support** from the community  
    -  **Talk to our AI assistant** for therapeutic guidance  
    -  **Leave heartfelt messages** in the Memory Book  

    💖 *You're not alone. We are in this together.*  
    """)


#streamlit UI
st.sidebar.title("Revora Navigation")
menu = st.sidebar.radio("", ["Home", "Sign Up", "Post", "Feed", "AI Assistant", "Journal", "Memory Book"])

if menu == "Home":
    home()

elif menu == "Journal":
    journal.main()

elif menu == "AI Assistant":
    therapy.main()

elif menu == "Sign Up":
    st.subheader("🔑 Create an Account")
    username = st.text_input("Choose a Username")
    bio = st.text_area("Write a short bio about yourself")

    if st.button("Sign Up"):
        if username and bio:
            if user_exists(username):
                st.error("Username already taken! Try another one.")
            else:
                add_user(username, bio)
                st.success(f"Welcome {username}! Your profile has been created.")
        else:
            st.error("Please fill out all fields.")

elif menu == "Post":
    st.subheader("📝 Share a Post")
    username = st.text_input("Enter your username")
    content = st.text_area("What's on your mind?")

    if st.button("Post"):
        if user_exists(username):
            add_post(username, content)
        else:
            st.error("User not found. Please sign up first.")

elif menu == "Feed":
    st.subheader("📢 Community Feed")
    posts = get_posts()

    for _, row in posts.iterrows():
        st.write(f"*{row['username']}* 🕒 {row['timestamp']}")
        st.write(row["content"])
        st.write(f"👍 {row['likes']} Likes")
        if st.button(f"Like Post {row['id']}", key=row['id']):
            like_post(row["id"])
            st.rerun()

elif menu == "Memory Book":
    memory_book_main()

conn.close()
