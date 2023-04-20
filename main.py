import os
import sys
import time
import numpy as np
import sounddevice as sd
import RPi.GPIO as GPIO
import openai
from pocketsphinx import LiveSpeech, get_model_path
import pyttsx3


# Initialize text-to-speech engine
engine = pyttsx3.init()

# Set up the OpenAI API
openai.api_key = "API_KEY_HERE"

# Set up the GPIO button
button_pin = 18
GPIO.setmode(GPIO.BCM)
GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Define variables for ChatGPT
personality = f"""You are Assistant, a helpful AI assistant. You will answer any questions brought to you in a formal, professional tone."""
textFormat = f"""All responses should be under 2000 characters. Format your responses so that they can be properly spoken by a text to speech program using pyttsx3."""

# Define a default system message
default_system_message = [
    {"role": "system", "content": personality},
    {"role": "system", "content": textFormat},
]


def recognize_speech():
    speech = LiveSpeech(
        verbose=False,
        sampling_rate=16000,
        buffer_size=2048,
        no_search=False,
        full_utt=False,
        hmm=os.path.join(get_model_path(), "en-us"),
        lm=os.path.join(get_model_path(), "en-us.lm.bin"),
        dic=os.path.join(get_model_path(), "cmudict-en-us.dict"),
    )

    print("Listening...")

    for phrase in speech:
        if GPIO.input(button_pin) == GPIO.LOW:
            break
        else:
            print(phrase)
            return str(phrase)


def ask_openai(question):
    completion_messages = default_system_message + [{"role": "user", "content": question}]

    # Request a response from the OpenAI API
    response = openai.Completion.create(
        model="gpt-3.5-turbo",
        messages=completion_messages,
        top_p=0.1,
    )

    # Extract and return the answer text
    return response.choices[0].message.content.strip()


def speak(text):
    print("Assistant: ", text)
    engine.say(text)
    engine.runAndWait()


# Main body of program
try:
	while True:
		# Check if the button is pressed
		input_state = GPIO.input(button_pin)
		if input_state == GPIO.LOW:
			print("Button Pressed")
			time.sleep(0.2)

			# Recognize speech and ask the OpenAI API for an answer
			question = recognize_speech()
			if question:
				answer = ask_openai(question)
				
				# Speak the answer
				speak(answer)

except KeyboardInterrupt:
	print("Exiting...")
	GPIO.cleanup()
