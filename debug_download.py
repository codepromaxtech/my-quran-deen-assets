import os
import json
import time
import urllib.request
import urllib.error
import sys

# Configuration
RECITER_ID = 7  # Mishary Rashid Alafasy
OUTPUT_DIR = "/home/erp/my-quran-deen-assets/audio/quran/Alafasy_128kbps/timestamps"
BASE_URL = "https://api.quran.com/api/v4/recitations/{reciter_id}/by_chapter/{chapter_id}?segments=true"

# User-Agent header
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

print(f"DEBUG: Script started. Output dir: {OUTPUT_DIR}")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def download_surah_timestamps(chapter_id):
    url = BASE_URL.format(reciter_id=RECITER_ID, chapter_id=chapter_id)
    print(f"DEBUG: Requesting {url}")
    
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req) as response:
            print(f"DEBUG: Response status: {response.status}")
            if response.status == 200:
                body = response.read().decode()
                print(f"DEBUG: Body length: {len(body)}")
                data = json.loads(body)
                
                filename = os.path.join(OUTPUT_DIR, f"{chapter_id}.json")
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                print(f"DEBUG: Saved to {filename}")
                return True
            else:
                return False
    except Exception as e:
        print(f"DEBUG: Error: {e}")
        return False

# Just Surah 1 for test
download_surah_timestamps(1)
print("DEBUG: Script finished.")
