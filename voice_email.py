import os
from dotenv import load_dotenv
import sounddevice as sd
from scipy.io.wavfile import write
import speech_recognition as sr
import pyttsx3
import smtplib
from email.mime.text import MIMEText
import google.generativeai as genai

# Load keys from .env
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

AUDIO_FILENAME = "input.wav"

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

# Text-to-Speech 
engine = pyttsx3.init()
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Record Audio
def record_audio(duration=5, fs=44100):
    print("🎤 Speak now...")
    speak("Speak now")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype="int16")
    sd.wait()
    write(AUDIO_FILENAME, fs, recording)
    print("✅ Recording done")
    return AUDIO_FILENAME

# Speech Recognition 
def recognize_speech(filename=AUDIO_FILENAME):
    r = sr.Recognizer()
    try:
        with sr.AudioFile(filename) as source:
            audio = r.record(source)
        text = r.recognize_google(audio)
        print("📝 You said:", text)
        return text
    except:
        print("⚠️ Could not understand audio")
        return None

# Gemini Formalization
def formalize_email(casual_text):
    prompt = f"Convert this casual text into a professional email:\n\n{casual_text}"
    model = genai.GenerativeModel("gemini-1.5-flash-002")
    response = model.generate_content(prompt)
    formal_email = response.text.strip()
    print("📝 Formal Email:", formal_email)
    return formal_email

# Send Email
def send_email(receiver_email, subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = receiver_email
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SENDER_EMAIL, GMAIL_APP_PASSWORD)
        server.send_message(msg)
    print("📧 Email sent successfully!")
    speak("Email sent successfully!")

# Main
def main():
    audio_file = record_audio(duration=7)
    casual_text = recognize_speech(audio_file)
    if casual_text:
        formal_text = formalize_email(casual_text)
        receiver_email = os.getenv("RECEIVER_EMAIL")  # <-- Fetch from .env
        send_email(receiver_email, "Automated Email", formal_text)


if __name__ == "__main__":
    main()
