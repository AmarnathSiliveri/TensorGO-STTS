# Import necessary libraries
import streamlit as st
import speech_recognition as sr
import pyttsx3
#import os
import google.generativeai as genai
import json
from gtts import gTTS
#from dotenv import load_dotenv

# Load environment variables
#load_dotenv()  # Ensure you have a .env file with API_KEY stored    
genai.configure(api_key=st.secrets['API_KEY'])

# Function to load Lottie files for animations
def load_lottiefiles(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)

# Initialize the Gemini model
model = genai.GenerativeModel("gemini-1.5-pro-002")
chat = model.start_chat(history=[])

# Initialize the TTS engine
def initialize_tts_engine():
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)  # Adjust speech rate
        engine.setProperty('volume', 1.0)  # Max volume
        return engine
    except ImportError:
        st.error("TTS initialization failed. Ensure Pyttsx3 is properly installed.")
        return None

# Function for speech recognition
def speech_to_text():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("🎙 Listening... Speak now!")
        try:
            audio = recognizer.listen(source, timeout=5)  # 5-second timeout
            input_text = recognizer.recognize_google(audio)
            return input_text
        except sr.UnknownValueError:
            st.error("Sorry, I couldn't understand the audio.")
            return None
        except sr.RequestError as e:
            st.error(f"Error with the recognition service: {e}")
            return None

# Function for processing text using Gemini API
def get_gemini_response(question):
    response = chat.send_message(question, stream=True)
    return response

# Function for text-to-speech conversion
def text_to_speech(text):
    tts = gTTS(text=text, lang='en')
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file_path = temp_file.name + ".mp3"
        tts.save(temp_file_path)
        return temp_file_path

# Streamlit app
def main():
    # Page setup
    st.set_page_config(page_title="STTS", layout="wide")
    st.header("🦅 Based on Gemini LLM Application")
    st.write("This app integrates speech recognition, the Gemini API, and text-to-speech capabilities.")

    # Initialize session state for chat history
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []

    # Input method selection
    st.subheader("Choose Input Method")
    input_method = st.radio("How would you like to provide input?", ("Upload Audio", "Type Text"))

    # Handle input from Audio File Upload
    if input_method == "Upload Audio":
        audio_file = st.file_uploader("Upload an audio file (wav, mp3, etc.)", type=["wav", "mp3"])
        if audio_file:
            st.audio(audio_file, format="audio/mp3")
            spoken_text = speech_to_text(audio_file)
            if spoken_text:
                st.write(f"🗣 You said: {spoken_text}")
                response = get_gemini_response(spoken_text)

                # Display and speak the response
                st.success("The Response is:")
                for chunk in response:
                    st.write(chunk.text)
                    st.session_state['chat_history'].append(("BOT", chunk.text))
                    # Generate and play the TTS
                    audio_path = text_to_speech(chunk.text)
                    st.audio(audio_path, format="audio/mp3")

    # Handle typed input
    elif input_method == "Type Text":
        input_text = st.text_input("Type your question here:", key="input")
        submit_button = st.button("Ask the Question")
        if submit_button and input_text:
            st.write(f"🗣 You typed: {input_text}")
            response = get_gemini_response(input_text)

            # Display and speak the response
            st.success("The Response is:")
            for chunk in response:
                st.write(chunk.text)
                st.session_state['chat_history'].append(("BOT", chunk.text))
                # Generate and play the TTS
                audio_path = text_to_speech(chunk.text)
                st.audio(audio_path, format="audio/mp3")

    # Display chat history
    st.subheader("Chat History")
    for speaker, message in st.session_state['chat_history']:
        if speaker == "You":
            st.write(f"🗣 **{speaker}**: {message}")
        else:
            st.write(f"🤖 **{speaker}**: {message}")


if __name__ == "__main__":
    main()
