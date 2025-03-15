import streamlit as st
import json
import os

MEMORY_BOOK_FILE = "memory_book.json"

# Load existing messages
def load_memory_book():
    if os.path.exists(MEMORY_BOOK_FILE):
        with open(MEMORY_BOOK_FILE, "r") as file:
            return json.load(file)
    return {}


# Save messages to file
def save_memory_book(data):
    with open(MEMORY_BOOK_FILE, "w") as file:
        json.dump(data, file, indent=4)


# Memory Book Page
def memory_book_main():
    st.title("📖 Memory Book")
    st.text("Write heartfelt messages for someone special.")

    recipient = st.text_input("Which user is this message for")
    sender = st.text_input("Your username:")
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
    recipient_to_view = st.text_input("Enter the username of the person to see their messages:")

    if st.button("Show Messages"):
        memory_book = load_memory_book()
        if recipient_to_view in memory_book:
            st.subheader(f"Messages for {recipient_to_view}:")
            for entry in memory_book[recipient_to_view]:
                st.markdown(f"**{entry['sender']}**: {entry['message']}")
        else:
            st.warning("No messages found for this person.")


# Allow the script to run independently
if __name__ == "__main__":
    memory_book_main()

