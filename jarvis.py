"""Jarvis - a Python voice assistant.

Listens for spoken commands, converts speech to text, and performs
desktop tasks such as launching apps, opening websites, reading
Wikipedia summaries, telling the time, and sending email.

Configuration (e.g. email credentials) is read from environment
variables so that no secrets live in the source code. See README.md.
"""

import datetime
import os
import smtplib
import webbrowser
from email.message import EmailMessage

import pyttsx3
import speech_recognition as sr
import wikipedia

# Email configuration is read from the environment. Never hard-code
# credentials. For Gmail, use an App Password, not your account password.
EMAIL_ADDRESS = os.environ.get("JARVIS_EMAIL")
EMAIL_PASSWORD = os.environ.get("JARVIS_EMAIL_PASSWORD")

# Voice of the assistant.
engine = pyttsx3.init()
voices = engine.getProperty("voices")
if voices:
    engine.setProperty("voice", voices[0].id)


def speak(audio):
    """Speak the given text aloud."""
    engine.say(audio)
    engine.runAndWait()


def assistant_start():
    """Greet the user based on the time of day."""
    hour = datetime.datetime.now().hour
    if 5 <= hour < 12:
        speak("Good Morning, Boss")
    elif 12 <= hour < 18:
        speak("Good Afternoon, Boss")
    else:
        speak("Good Evening, Boss")
    speak("I am Jarvis. How may I help you?")


def take_command():
    """Listen on the microphone and return recognized text (or 'None')."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.pause_threshold = 1
        audio = recognizer.listen(source)

    try:
        print("Recognizing...")
        query = recognizer.recognize_google(audio, language="en-in")
        print(f"Boss: {query}\n")
    except Exception:
        speak("Boss, can you say that again please...")
        return "None"

    return query


def send_email(to, content):
    """Send a plain-text email using credentials from the environment."""
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        raise RuntimeError(
            "Email is not configured. Set JARVIS_EMAIL and "
            "JARVIS_EMAIL_PASSWORD environment variables."
        )
    message = EmailMessage()
    message["From"] = EMAIL_ADDRESS
    message["To"] = to
    message["Subject"] = "Message from Jarvis"
    message.set_content(content)

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.ehlo()
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(message)


def open_app(path):
    """Launch a desktop application by path (Windows-style os.startfile)."""
    try:
        os.startfile(path)
    except (AttributeError, FileNotFoundError, OSError):
        speak("Sorry, I could not open that application on this system.")


def main():
    assistant_start()
    while True:
        query = take_command().lower()

        # Open Wikipedia and read a summary aloud.
        if "wikipedia" in query:
            speak("Searching Wikipedia...")
            query = query.replace("wikipedia", "")
            results = wikipedia.summary(query, sentences=5)
            speak("According to Wikipedia")
            speak(results)

        # Open websites.
        elif "open youtube" in query:
            webbrowser.open("https://www.youtube.com")

        elif "open google" in query:
            webbrowser.open("https://www.google.com")

        elif "open coursera" in query:
            webbrowser.open("https://www.coursera.org")

        elif "chatgpt" in query:
            webbrowser.open("https://chat.openai.com/")

        # Tell the current time.
        elif "time" in query:
            str_time = datetime.datetime.now().strftime("%I:%M %p")
            speak(f"It's {str_time}")

        # Send an email to the configured address.
        elif "send email to me" in query:
            try:
                speak("What should I write?")
                content = take_command()
                send_email(EMAIL_ADDRESS, content)
                speak("Email sent.")
            except Exception:
                speak("Due to some issue I am not able to complete the command.")

        # Power controls (Windows).
        elif "shutdown" in query:
            os.system("shutdown /s /t 1")

        elif "restart" in query:
            os.system("shutdown /r /t 1")

        elif "logout" in query:
            os.system("shutdown -l")

        # Stop the assistant.
        elif "stop" in query:
            speak("Goodbye, Boss.")
            break


if __name__ == "__main__":
    main()
