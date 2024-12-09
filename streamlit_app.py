import os
import wave
import streamlit as st
from vosk import Model, KaldiRecognizer
import json
import tempfile
import urllib.request
import zipfile

# Function to download and extract the Vosk model
def download_and_extract_model(model_url, model_dir):
    # Check if the model directory exists
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)
        zip_file_path = os.path.join(model_dir, "vosk_model.zip")
        # Download the Vosk model
        st.write("Downloading Vosk model...")
        try:
            urllib.request.urlretrieve(model_url, zip_file_path)
            st.write("Model downloaded successfully.")
        except Exception as e:
            st.write(f"Error downloading model: {e}")
            raise

        # Extract the model
        try:
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                zip_ref.extractall(model_dir)
            st.write("Vosk model downloaded and extracted.")
        except Exception as e:
            st.write(f"Error extracting model: {e}")
            raise
    else:
        st.write("Vosk model already exists.")

# Function to load the Vosk model
def load_model(model_path):
    if not os.path.exists(model_path):
        raise Exception(f"Model path {model_path} does not exist.")
    return Model(model_path)

# Function to process the audio and transcribe it
def transcribe_audio(audio_file, model):
    wf = wave.open(audio_file, "rb")
    recognizer = KaldiRecognizer(model, wf.getframerate())
    
    result_text = ""
    
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if recognizer.AcceptWaveform(data):
            result_text += recognizer.Result() + "\n"
    
    result_text += recognizer.FinalResult()  # Get final result
    return result_text

# Streamlit App UI
def main():
    st.title("Automatic Audio Transcription with Vosk")

    # URL for downloading the Vosk English model
    model_url = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
    model_dir = "vosk_model/vosk-model-small-en-us-0.15"
    
    # Download and extract the Vosk model if not already present
    download_and_extract_model(model_url, model_dir)
    
    # Load the model
    try:
        st.write("Loading Vosk model...")
        model = load_model(model_dir)
    except Exception as e:
        st.write(f"Error loading model: {e}")
        return
    
    # Upload audio file
    audio_file = st.file_uploader("Upload an audio file (.wav)", type=["wav"])
    
    if audio_file is not None:
        # Save uploaded audio to a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as tmp_audio_file:
            tmp_audio_file.write(audio_file.read())
            tmp_audio_file_path = tmp_audio_file.name
        
        # Transcribe the audio
        st.write("Transcribing audio...")
        try:
            transcription = transcribe_audio(tmp_audio_file_path, model)
            # Display transcription
            st.subheader("Transcription Result:")
            st.text(transcription)
        except Exception as e:
            st.write(f"Error transcribing audio: {e}")

if __name__ == "__main__":
    main()
