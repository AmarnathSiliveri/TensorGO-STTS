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
    st.set_page_config(page_title="AmarGPT 🦅", layout="wide")
    st.header("𝐀𝐦𝐚𝐫𝐆𝐏𝐓 🦅 based on Gemini LLM Application")
    st.write("This app integrates speech recognition, the Gemini API, and text-to-speech capabilities.")

    # Load and display Lottie animation
    lottie_hi = load_lottiefiles("higpt.json")  # Ensure you have this JSON file in the directory
    st_lottie(lottie_hi, loop=True, quality="high", speed=1.65, height=450)

    # Initialize session state for chat history
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []

    # Input method selection
    st.subheader("Choose Input Method")
    input_method = st.radio("How would you like to provide input?", ("Microphone", "Type Text"))

    tts_engine = initialize_tts_engine()  # Initialize TTS engine

    # Handle input from Microphone
    if input_method == "Microphone":
        if st.button("🎤 Start Speaking"):
            spoken_text = speech_to_text()
            if spoken_text:
                st.write(f"🗣 You said: {spoken_text}")
                response = get_gemini_response(spoken_text)

                # Display and speak the response
                st.success("The Response is:")
                for chunk in response:
                    st.write(chunk.text)
                    st.session_state['chat_history'].append(("BOT", chunk.text))
                    text_to_speech(tts_engine, chunk.text)

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
                text_to_speech(tts_engine, chunk.text)

    # Display chat history
    st.subheader("Chat History")
    for speaker, message in st.session_state['chat_history']:
        if speaker == "You":
            st.write(f"🗣 **{speaker}**: {message}")
        else:
            st.write(f"🤖 **{speaker}**: {message}")


if __name__ == "__main__":
    main()
