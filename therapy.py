import streamlit as st
import sounddevice as sd
import queue
import json
import gtts
import base64
from vosk import Model, KaldiRecognizer
import google.generativeai as genai
from io import BytesIO

# Set up Gemini API
genai.configure(api_key="AIzaSyCWDe5o49MP4RSuNLMDN2eRIgmeXQI0AFE")

# Load Vosk Model
VOSK_MODEL_PATH = r"vosk-model-small-en-us-0.15"
model = Model(VOSK_MODEL_PATH)


# Function to record and recognize speech
def recognize_speech():
    q = queue.Queue()

    def callback(indata, frames, time, status):
        q.put(bytes(indata))

    with sd.RawInputStream(samplerate=16000, blocksize=4000, dtype='int16',
                           channels=1, callback=callback):
        recognizer = KaldiRecognizer(model, 16000)
        transcript = ""

        while True:
            data = q.get()
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                transcript = result.get("text", "")
                break

    return transcript

# Function to call Gemini API
def get_gemini_response(text):
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        prompt = (
                "You are a kind and supportive therapist. Respond empathetically in a concise manner, "
                "offering reassurance, encouragement, and brief insights. Keep responses under 120 words."
                "Here is what the user said: " + text
        )
        response = model.generate_content(prompt)
        return response.text if response else "I'm here to support you. Can you tell me more?"
    except Exception as e:
        return f"Error: {e}"


# Function to convert text to speech and play automatically (faster)
def speak_text(text):
    tts = gtts.gTTS(text=text, lang='en', slow=False)
    mp3_fp = BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)

    # Convert BytesIO object to base64
    audio_bytes = mp3_fp.getvalue()
    b64 = base64.b64encode(audio_bytes).decode()

    # HTML audio tag with autoplay enabled but hidden
    audio_html = f"""
    <audio autoplay style="display:none;">
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
    </audio>
    """

    return audio_html


# Function to display text immediately
def display_text(text):
    st.markdown(f"**AI Therapist:** {text}")


# Function to run the therapy chatbot in Streamlit
def main():
    st.title("🔊 Supportive AI Therapist")
    st.text("Speak or type to receive comforting AI responses.")

    user_input = st.text_input("Type your message or use the microphone:")

    if st.button("🎤 Start Talking"):
        st.text("Listening...")
        user_input = recognize_speech()

    if user_input:
        st.text(f"You: {user_input}")
        ai_response = get_gemini_response(user_input)

        # Display text and audio at the same time
        audio_html = speak_text(ai_response)
        st.markdown(audio_html, unsafe_allow_html=True)  # Ensures autoplay without visible player

        # Display text immediately
        display_text(ai_response)


# Ensure this runs only when executed directly
if __name__ == "__main__":
    main()
