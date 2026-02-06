import os
import json
import time
import urllib.request
import urllib.error

# Configuration
RECITER_ID = 7  # Mishary Rashid Alafasy
OUTPUT_DIR = "/home/erp/my-quran-deen-assets/audio/quran/Alafasy_128kbps/timestamps"
# NEW QDC ENDPOINT
BASE_URL = "https://api.quran.com/api/qdc/audio/reciters/{reciter_id}/audio_files?chapter={chapter_id}&segments=true"

# User-Agent header
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

os.makedirs(OUTPUT_DIR, exist_ok=True)

def download_surah_timestamps(chapter_id):
    url = BASE_URL.format(reciter_id=RECITER_ID, chapter_id=chapter_id)
    
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                
                # The data structure from QDC has 'audio_files' as a list
                # We want to ensure we actually got segments
                if 'audio_files' in data and len(data['audio_files']) > 0:
                    audio_file = data['audio_files'][0]
                    if 'verse_timings' in audio_file:
                        filename = os.path.join(OUTPUT_DIR, f"{chapter_id}.json")
                        with open(filename, 'w', encoding='utf-8') as f:
                            json.dump(data, f, indent=2, ensure_ascii=False)
                        print(f"Downloaded Surah {chapter_id} (QDC Mode)")
                        return True
                
                print(f"Warning: Surah {chapter_id} has no verse_timings")
                return False
            else:
                print(f"Failed Surah {chapter_id}: {response.status}")
                return False
    except Exception as e:
        print(f"Error Surah {chapter_id}: {e}")
        return False

def main():
    print(f"Starting QDC download to {OUTPUT_DIR}")
    for chapter_id in range(1, 115):
        download_surah_timestamps(chapter_id)
        time.sleep(0.3)
    print("QDC Download complete.")

if __name__ == "__main__":
    main()
