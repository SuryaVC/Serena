import streamlit as st
import sounddevice as sd
import soundfile as sf
import openai
import requests
import re
from colorama import Fore, Style, init
import base64
from pydub import AudioSegment
from pydub.playback import play

init()

def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()

api_key = open_file('openai_api_key1.txt')
elapikey = open_file('voice_api_key1.txt')

conversation1 = []
chatbot1 = open_file('chatbot1.txt')

def chatgpt(api_key, conversation, chatbot, user_input, temperature=0.9, frequency_penalty=0.2, presence_penalty=0):
    openai.api_key = api_key
    conversation.append({"role": "user","content": user_input})
    messages_input = conversation.copy()
    prompt = [{"role": "system", "content": chatbot}]
    messages_input.insert(0, prompt[0])
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        temperature=temperature,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
        messages=messages_input)
    chat_response = completion['choices'][0]['message']['content']
    conversation.append({"role": "assistant", "content": chat_response})
    return chat_response

def text_to_speech(text, voice_id, api_key):
    url = f'https://api.elevenlabs.io/v1/text-to-speech/{voice_id}'
    headers = {
        'Accept': 'audio/mpeg',
        'xi-api-key': api_key,
        'Content-Type': 'application/json'
    }
    data = {
        'text': text,
        'model_id': 'eleven_monolingual_v1',
        'voice_settings': {
            'stability': 0.6,
            'similarity_boost': 0.85
        }
    }
    print(f'API Key: {elapikey}')
    print(f'Headers: {headers}')
    response = requests.post(url, headers=headers, json=data)

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)
        with open('output.mp3', 'wb') as f:
            f.write(response.content)
        audio = AudioSegment.from_mp3('output.mp3')
        play(audio)
    except requests.exceptions.HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'An error occurred: {err}')


def print_colored(agent, text):
    agent_colors = {
        "Julie:": Fore.YELLOW,
    }
    color = agent_colors.get(agent, "")
    print(color + f"{agent}: {text}" + Style.RESET_ALL, end="")

voice_id1 = 'pMsXgVXv3BLzUgSXRplE'

st.title('Voice Assistant Chatbot')

def record_and_transcribe(duration=10, fs=44100):
    st.write('Recording...')
    myrecording = sd.rec(int(duration * fs), samplerate=fs, channels=1)  # Change channels to 1
    sd.wait()
    st.write('Recording complete.')
    filename = 'myrecording.wav'
    sf.write(filename, myrecording, fs)
    with open(filename, "rb") as file:
        openai.api_key = api_key
        result = openai.Audio.transcribe("whisper-1", file)
    transcription = result['text']
    return transcription

if st.button('Start Chat'):
    while True:
        user_message = record_and_transcribe()
        response = chatgpt(api_key, conversation1, chatbot1, user_message)
        st.write(f"Julie: {response}\n\n")
        user_message_without_generate_image = re.sub(r'(Response:|Narration:|Image: generate_image:.*|)', '', response).strip()
        text_to_speech(user_message_without_generate_image, voice_id1, elapikey)
