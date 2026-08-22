import datetime
import webbrowser
import pyttsx3
import os
import json
import requests
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

# ===== API KEYS =====
YOUR_CITY = "Mumbai"  # Change to your city!

# ===== SETUP =====
client = Groq(api_key=GROQ_API_KEY)
engine = pyttsx3.init()
engine.setProperty("rate", 180)
engine.setProperty("volume", 1.0)

# ===== MEMORY =====
MEMORY_FILE = "jarvis_memory.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return {"user_name": "Sir", "preferences": {}}

def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f)

memory = load_memory()
USER_NAME = memory["user_name"]

# ===== JARVIS PERSONALITY =====
history = [
    {"role": "system", "content": f"""You are Jarvis, an AI assistant like from Iron Man. 
    You are intelligent, professional, and slightly witty. 
    You address the user as {USER_NAME}. 
    Keep responses short and to the point.
    Today's date is {datetime.date.today()}."""}
]

# ===== CORE FUNCTIONS =====
def speak(text):
    print("Jarvis: " + text)
    engine.say(text)
    engine.runAndWait()

def ask_jarvis(question):
    history.append({"role": "user", "content": question})
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=history
    )
    answer = response.choices[0].message.content
    history.append({"role": "assistant", "content": answer})
    return answer

# ===== WEATHER =====
def get_weather():
    url = f"http://api.openweathermap.org/data/2.5/weather?q={YOUR_CITY}&appid={WEATHER_API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()
    if data["cod"] == 200:
        temp = data["main"]["temp"]
        desc = data["weather"][0]["description"]
        city = data["name"]
        return f"The weather in {city} is {temp}°C with {desc} {USER_NAME}."
    else:
        return "Sorry Sir, I couldn't fetch the weather right now."

# ===== NEWS =====
def get_news():
    url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey=demo&pageSize=3"
    try:
        response = requests.get(url)
        data = response.json()
        if data["status"] == "ok" and data["articles"]:
            speak("Here are the top headlines Sir.")
            for i, article in enumerate(data["articles"][:3]):
                speak(f"Headline {i+1}: {article['title']}")
        else:
            answer = ask_jarvis("Give me 3 current top news headlines from India in one line each")
            speak(answer)
    except:
        answer = ask_jarvis("Give me 3 current top news headlines from India in one line each")
        speak(answer)

# ===== SYSTEM CONTROL =====
def system_control(command):
    if "shutdown" in command:
        speak("Shutting down your computer Sir. Goodbye!")
        os.system("shutdown /s /t 5")
    elif "restart" in command:
        speak("Restarting your computer Sir.")
        os.system("shutdown /r /t 5")
    elif "volume up" in command:
        speak("Increasing volume Sir.")
        for _ in range(5):
            os.system("nircmd.exe changesysvolume 5000")
    elif "volume down" in command:
        speak("Decreasing volume Sir.")
        for _ in range(5):
            os.system("nircmd.exe changesysvolume -5000")
    elif "mute" in command:
        speak("Muting Sir.")
        os.system("nircmd.exe mutesysvolume 1")

# ===== MEMORY COMMANDS =====
def handle_memory(command):
    global USER_NAME
    if "remember my name is" in command:
        name = command.replace("remember my name is", "").strip().title()
        memory["user_name"] = name
        USER_NAME = name
        save_memory(memory)
        speak(f"Got it! I will call you {name} from now on.")
    elif "what is my name" in command or "what's my name" in command:
        speak(f"Your name is {memory['user_name']}.")
    elif "remember" in command:
        fact = command.replace("remember", "").strip()
        memory["preferences"][fact] = True
        save_memory(memory)
        speak(f"Got it Sir, I will remember that {fact}.")
    elif "what do you know about me" in command:
        if memory["preferences"]:
            facts = ", ".join(memory["preferences"].keys())
            speak(f"Here is what I know about you Sir: {facts}")
        else:
            speak("I don't have any stored preferences yet Sir.")

# ===== MAIN RESPOND FUNCTION =====
def respond(command):
    # Time & Date
    if "time" in command:
        now = datetime.datetime.now()
        speak(f"The time is {now.hour}:{now.minute:02d} {USER_NAME}.")

    elif "date" in command:
        today = datetime.date.today()
        speak(f"Today is {today.strftime('%B %d, %Y')} {USER_NAME}.")

    # Weather
    elif "weather" in command:
        speak(get_weather())

    # News
    elif "news" in command or "headlines" in command:
        get_news()

    # Open websites
    elif "open youtube" in command:
        speak("Opening YouTube Sir.")
        webbrowser.open("https://youtube.com")

    elif "open google" in command:
        speak("Opening Google Sir.")
        webbrowser.open("https://google.com")

    elif "open github" in command:
        speak("Opening GitHub Sir.")
        webbrowser.open("https://github.com")

    elif "open whatsapp" in command:
        speak("Opening WhatsApp Sir.")
        webbrowser.open("https://web.whatsapp.com")

    elif "open instagram" in command:
        speak("Opening Instagram Sir.")
        webbrowser.open("https://instagram.com")

    elif "open netflix" in command:
        speak("Opening Netflix Sir.")
        webbrowser.open("https://netflix.com")

    # Search
    elif "search" in command:
        query = command.replace("search", "").strip()
        speak(f"Searching for {query} Sir.")
        webbrowser.open(f"https://www.google.com/search?q={query}")

    # YouTube play
    elif "play" in command and "youtube" in command:
        query = command.replace("play", "").replace("youtube", "").strip()
        speak(f"Playing {query} on YouTube Sir.")
        webbrowser.open(f"https://www.youtube.com/results?search_query={query}")

    # System control
    elif any(word in command for word in ["shutdown", "restart", "volume up", "volume down", "mute"]):
        system_control(command)

    # Memory
    elif any(word in command for word in ["remember", "what is my name", "what's my name", "what do you know about me"]):
        handle_memory(command)

    # Identity
    elif "who are you" in command:
        speak("I am Jarvis, your personal AI assistant. Built by you, at your service always.")

    elif "who am i" in command:
        speak(f"You are {USER_NAME}, my creator and master.")

    # Joke
    elif "joke" in command:
        answer = ask_jarvis("Tell me a short funny joke")
        speak(answer)

    # Goodbye
    elif any(word in command for word in ["bye", "goodbye", "exit", "quit"]):
        speak(f"Goodbye {USER_NAME}! Have a great day!")
        save_memory(memory)
        exit()

    # Empty
    elif command.strip() == "":
        pass

    # AI handles everything else
    else:
        answer = ask_jarvis(command)
        speak(answer)

# ===== START JARVIS =====
speak(f"Hello {USER_NAME}! I am Jarvis, your personal AI assistant. All systems online.")
speak("Weather, news, web search, memory — all systems ready Sir.")

import sounddevice as sd
import scipy.io.wavfile as wav
import speech_recognition as sr
import numpy as np
import tempfile

def listen():
    print("Listening... (speak now)")
    duration = 5
    sample_rate = 16000
    recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype="int16")
    sd.wait()
    
    temp_file = tempfile.mktemp(suffix=".wav")
    wav.write(temp_file, sample_rate, recording)
    
    recognizer = sr.Recognizer()
    with sr.AudioFile(temp_file) as source:
        audio = recognizer.record(source)
    
    os.remove(temp_file)
    
    try:
        command = recognizer.recognize_google(audio)
        print("You: " + command)
        return command.lower()
    except:
        print("Could not hear anything...")
        return ""

while True:
    command = listen()
    respond(command)

    