import os
import requests

def download_tts(filename, text, lang='ar'):
    url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={text}&tl={lang}&client=tw-ob"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"Generated: {filename}")
        else:
            print(f"Failed to generate {filename}: {response.status_code}")
    except Exception as e:
        print(f"Error {filename}: {e}")

# Ensure directory exists
output_dir = "audio/qaida"
os.makedirs(output_dir, exist_ok=True)

# Lesson 2: Harakat (Short Vowels)
# We use Arabic text that approximates the sound.
harakat_map = {
    # Alif
    "alif_fatha": "أَ",
    "alif_kasra": "إِ",
    "alif_damma": "أُ",
    
    # Ba
    "ba_fatha": "بَ",
    "ba_kasra": "بِ", 
    "ba_damma": "بُ",

    # Ta
    "ta_fatha": "تَ",
    "ta_kasra": "تِ",
    "ta_damma": "تُ",
}

print("Generating Harakat Audio...")
for id, text in harakat_map.items():
    filename = f"{output_dir}/{id}.mp3"
    if not os.path.exists(filename):
        download_tts(filename, text)
    else:
        print(f"Skipping {filename} (exists)")

print("Done! Push these assets to your repo.")
