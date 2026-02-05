import os
import requests
import time

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
    
    # Be polite to the API
    time.sleep(0.5)

# Ensure directory exists
output_dir = "audio/qaida"
os.makedirs(output_dir, exist_ok=True)

# Audio Mapping for all lessons
# Key: Filename (without extension) -> Value: Arabic text for TTS
audio_map = {
    # Lesson 2: Harakat
    "alif_fatha": "أَ", "alif_kasra": "إِ", "alif_damma": "أُ",
    "ba_fatha": "بَ", "ba_kasra": "بِ", "ba_damma": "بُ",
    "ta_fatha": "تَ", "ta_kasra": "تِ", "ta_damma": "تُ",

    # Lesson 3: Tanween
    "alif_an": "أً", "alif_in": "إٍ", "alif_un": "أٌ",
    "ba_an": "بًا", "ba_in": "بٍ", "ba_un": "بٌ",
    "ta_an": "تًا", "ta_in": "تٍ", "ta_un": "تٌ",

    # Lesson 4: Madd (Long Vowels)
    "ba_aa": "بَا", "ba_ee": "بِي", "ba_oo": "بُو",
    "ta_aa": "تَا", "ta_ee": "تِي", "ta_oo": "تُو",
    "jim_aa": "جَا", "jim_ee": "جِي", "jim_oo": "جُو",

    # Lesson 5: Sukoon
    "ab": "اَبْ", "ib": "اِبْ", "ub": "اُبْ",
    "at": "اَتْ", "it": "اِتْ", "ut": "اُتْ",

    # Lesson 6: Tashdeed
    "abba": "اَبَّ", "ibba": "اِبَّ", "ubba": "اُبَّ",
    "atta": "اَتَّ", 

    # Lesson 7: Practice Words
    "word_rabb": "رَبِّ",
    "word_maliki": "مَلِكِ",
    "word_kitab": "كِتَابٌ",
    "word_qalam": "قَلَمٌ",
    "word_salam": "سَلَامٌ",

    # Lesson 8: Surah Al-Fatiha
    "fatiha_1_1": "بِسْمِ",
    "fatiha_1_2": "ٱللَّهِ",
    "fatiha_1_3": "ٱلرَّحْمَـٰنِ",
    "fatiha_1_4": "ٱلرَّحِيمِ",
    "fatiha_2_1": "ٱلْحَمْدُ",
    "fatiha_2_2": "لِلَّهِ",
    "fatiha_2_3": "رَبِّ",
    "fatiha_2_4": "ٱلْعَـٰلَمِينَ",
    "fatiha_4_1": "مَـٰلِكِ",
    "fatiha_4_2": "يَوْمِ",
    "fatiha_4_3": "ٱلدِّينِ",
}

print("Generating Qaida Audio Assets...")
for id, text in audio_map.items():
    filename = f"{output_dir}/{id}.mp3"
    if not os.path.exists(filename):
        download_tts(filename, text)
    else:
        # print(f"Skipping {filename} (exists)")
        pass

print("Done! Push these assets to your repo.")
