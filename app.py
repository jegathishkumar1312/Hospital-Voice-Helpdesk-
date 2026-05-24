import streamlit as st
import speech_recognition as sr
import json
import os
import time
from datetime import datetime

# ---------------- PAGE SETTINGS ---------------- #

st.set_page_config(page_title="Hospital Voice Helpdesk")

st.title("Hospital Voice Helpdesk (NLP System)")
st.write("Voice + NLP powered hospital assistant")

# ---------------- DOMAIN DATABASE ---------------- #

hospital_data = {
    "icu": "The ICU department is located on the 2nd floor in Block A.",
    "pharmacy": "The pharmacy is available near the main reception area.",
    "op": "The OP department is located on the ground floor.",
    "emergency": "Emergency services are available 24/7.",
    "cardiology": "The cardiology department is located in Block B.",
    "radiology": "The radiology department is located in Block C.",
    "lab": "The laboratory is available on the 1st floor.",
    "billing": "The billing counter is available on the first floor.",
    "timing": "The hospital operates from 9 AM to 5 PM."
}

# ---------------- TRANSCRIPT STORAGE ---------------- #

def save_transcript(query, intent, answer):

    data = {
        "query": query,
        "intent": intent,
        "answer": answer,
        "time": str(datetime.now())
    }

    if os.path.exists("transcripts.json"):

        try:
            with open("transcripts.json", "r") as f:
                chats = json.load(f)

        except:
            chats = []

    else:
        chats = []

    chats.append(data)

    with open("transcripts.json", "w") as f:
        json.dump(chats, f, indent=4)

# ---------------- SUMMARIZATION ---------------- #

def summarize_text(text):

    words = text.split()

    summary = " ".join(words[:10])

    return summary + "..."

# ---------------- SENTIMENT ANALYSIS ---------------- #

def detect_sentiment(text):

    positive_words = ["good", "excellent", "fast", "best"]

    negative_words = ["bad", "slow", "worst"]

    for word in positive_words:

        if word in text.lower():
            return "Positive"

    for word in negative_words:

        if word in text.lower():
            return "Negative"

    return "Neutral"

# ---------------- VOICE RECOGNITION ---------------- #

def recognize_voice():

    recognizer = sr.Recognizer()

    with sr.Microphone() as source:

        st.info("Speak now...")

        audio = recognizer.listen(source)

        try:

            text = recognizer.recognize_google(audio)

            return text.lower()

        except:

            return ""

# ---------------- SESSION STATE ---------------- #

if "user_query" not in st.session_state:
    st.session_state.user_query = ""

# ---------------- TEXT INPUT ---------------- #

user_input = st.text_input(
    "Enter your hospital question",
    value=st.session_state.user_query
)

# ---------------- VOICE BUTTON ---------------- #

if st.button("Voice Input"):

    voice_text = recognize_voice()

    if voice_text != "":

        st.session_state.user_query = voice_text

        st.success(f"You said: {voice_text}")

        st.rerun()

    else:

        st.error("Could not recognize voice")

# ---------------- ASK BUTTON ---------------- #

if st.button("Ask"):

    start_time = time.time()

    query = user_input.lower().strip()

    # ---------------- BOUNDARY CASE ---------------- #

    if query == "":

        st.error("Please enter a valid query")

        st.stop()

    intent = "unknown"

    # ---------------- NLP INTENT DETECTION ---------------- #

    if (
        "icu" in query
        or "i see you" in query
        or "icu location" in query
        or "where is icu" in query
    ):
        intent = "icu"

    elif "pharmacy" in query:
        intent = "pharmacy"

    elif "op" in query:
        intent = "op"

    elif "emergency" in query:
        intent = "emergency"

    elif "cardiology" in query:
        intent = "cardiology"

    elif "radiology" in query:
        intent = "radiology"

    elif "lab" in query or "laboratory" in query:
        intent = "lab"

    elif "billing" in query:
        intent = "billing"

    elif "timing" in query or "time" in query:
        intent = "timing"

    # ---------------- RESPONSE GENERATION ---------------- #

    answer = hospital_data.get(
        intent,
        "Sorry, information not available"
    )

    # ---------------- SUMMARIZATION ---------------- #

    summary = summarize_text(answer)

    # ---------------- SENTIMENT ---------------- #

    sentiment = detect_sentiment(query)

    # ---------------- LATENCY ---------------- #

    end_time = time.time()

    latency = end_time - start_time

    # ---------------- SAVE TRANSCRIPT ---------------- #

    save_transcript(query, intent, answer)

    # ---------------- OUTPUT ---------------- #

    st.success(answer)

    st.write(f"Intent: {intent}")

    st.write(f"Summary: {summary}")

    st.write(f"Sentiment: {sentiment}")

    st.write(f"Response Time: {latency:.2f} seconds")

    st.write(f"Time: {datetime.now()}")

# ---------------- TRANSCRIPT REPLAY ---------------- #

st.subheader("Previous Transcripts")

if os.path.exists("transcripts.json"):

    try:

        with open("transcripts.json", "r") as f:
            chats = json.load(f)

        for chat in reversed(chats[-10:]):

            st.write(f"Q: {chat['query']}")
            st.write(f"Intent: {chat['intent']}")
            st.write(f"A: {chat['answer']}")
            st.write(f"Time: {chat['time']}")
            st.write("---")

    except:

        st.error("Transcript file is corrupted")