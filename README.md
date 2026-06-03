# Voice-Assistant-Using-Python

Jarvis is a Python-based voice assistant that listens for spoken commands,
converts speech to text, and performs desktop tasks such as launching
applications, opening websites, reading Wikipedia summaries, telling the
time, and sending email — replying back with a synthesized voice.

## Features

- Time-aware greeting (morning / afternoon / evening)
- Speech-to-text command recognition (Google Speech Recognition)
- Text-to-speech responses (`pyttsx3`)
- Wikipedia summaries
- Open websites (YouTube, Google, Coursera, ChatGPT)
- Tell the current time
- Send email to yourself
- Power controls (shutdown / restart / logout)

## Requirements

- Python 3.8+
- A working microphone
- The packages in `requirements.txt`

Install dependencies:

```bash
pip install -r requirements.txt
```

> **Note:** `PyAudio` may require system audio libraries (e.g. `portaudio`).
> On some platforms you may need to install those first.

## Configuration

Email credentials are read from environment variables — **no secrets are
stored in the source code**. For Gmail, create an
[App Password](https://support.google.com/accounts/answer/185833) and set:

```bash
export JARVIS_EMAIL="you@gmail.com"
export JARVIS_EMAIL_PASSWORD="your-app-password"
```

## Usage

```bash
python jarvis.py
```

Then speak commands such as:

- "wikipedia <topic>"
- "open youtube" / "open google" / "open coursera" / "chatgpt"
- "what's the time"
- "send email to me"
- "shutdown" / "restart" / "logout"
- "stop" to quit

## Platform notes

Application launching and power commands use Windows APIs
(`os.startfile`, `shutdown`). These features are Windows-oriented; the
voice, speech, web, and Wikipedia features are cross-platform.
