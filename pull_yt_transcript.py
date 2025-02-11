import requests
from bs4 import BeautifulSoup
import re
import json
import os
from datetime import datetime

def get_youtube_transcript(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        script_tag = soup.find("script", string=re.compile("ytInitialPlayerResponse"))

        if script_tag:
            json_str = re.search(r'ytInitialPlayerResponse\s*=\s*({.+?});', script_tag.string).group(1)
            data = json.loads(json_str)
            transcript_data = data.get('captions', {}).get('playerCaptionsTracklistRenderer', {}).get('captionTracks', [])

            if transcript_data:
                transcript_url = transcript_data[0]['baseUrl']
                transcript_response = requests.get(transcript_url)
                transcript_response.raise_for_status()
                transcript_soup = BeautifulSoup(transcript_response.text, 'xml')
                return " ".join([text.text for text in transcript_soup.find_all('text')])
            else:
                return "No transcript available for this video."
        else:
            return "Could not find transcript data in the page source."

    except requests.RequestException as e:
        return f"Error fetching the video page: {str(e)}"
    except (json.JSONDecodeError, AttributeError, KeyError) as e:
        return f"Error parsing transcript data: {str(e)}"

def save_transcript_to_file(transcript):
    current_datetime = datetime.now()
    filename = current_datetime.strftime("%Y%m%d_%H%M%S.txt")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, filename)
    
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(transcript)
    
    return file_path

if __name__ == "__main__":
    video_url = input("Enter YouTube video URL: ")
    transcript = get_youtube_transcript(video_url)
    
    if transcript:
        saved_file_path = save_transcript_to_file(transcript)
        print(f"Transcript saved to: {saved_file_path}")
    else:
        print("Could not retrieve transcript. The video might not have captions.")
