import requests
import sys
import os

def transcribe_audio(file_path):
    url = "http://localhost:8000/api/transcribe"
    
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        return

    print(f"Sending {file_path} to {url}...")

    try:
        with open(file_path, 'rb') as f:
            # The key 'file' matches the parameter name in FastAPI: file: UploadFile = File(...)
            files = {'file': f}
            response = requests.post(url, files=files)
        
        if response.status_code == 200:
            print("\n--- Transcription Result ---")
            print(response.json().get('text', 'No text found'))
            print("----------------------------")
        else:
            print(f"Error {response.status_code}:")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the backend. Is it running on localhost:8000?")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

def process_entry(file_path):
    url = "http://localhost:8000/api/process-entry"
    
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        return

    print(f"\nTesting Combined Endpoint: Sending {file_path} to {url}...")

    try:
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(url, files=files)
        
        if response.status_code == 200:
            data = response.json()
            print("\n--- Process Entry Result ---")
            print(f"Transcription: {data.get('transcription', 'N/A')}")
            print(f"Follow-up Question: {data.get('follow_up_question', 'N/A')}")
            print("----------------------------")
            return data
        else:
            print(f"Error {response.status_code}:")
            print(response.text)
        
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")

def generate_question(text):
    url = "http://localhost:8000/api/generate-question"
    
    try:
        response = requests.post(url, json={'context': text})
        
        if response.status_code == 200:
            data = response.json()
            print("\n--- Generate Question Result ---")
            print(f"Question: {data.get('question', 'N/A')}")
            print("----------------------------")
            return data
        else:
            print(f"Error {response.status_code}:")
            print(response.text)
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    


import time

fp = "./test.mp3"

# start = time.time()
# text = transcribe_audio(fp)
# end = time.time()
# print(f"Transcription took {end - start} seconds")

text = "Hey Bear, go away! Says the bee. This is not your honey! Mr. Bear is annoyed. I am bigger than you."
start = time.time()
generate_question(text)
end = time.time()
print(f"Generate Question took {end - start} seconds")


# start = time.time()
# process_entry(fp)
# end = time.time()
# print(f"Process Entry took {end - start} seconds")