import os
import time
import requests
import json
import hashlib
from pathlib import Path

class QuranDownloader:
    def __init__(self, reciter_id, url_path, min_file_size=5000):
        """
        Initialize the Quran downloader with resume and corruption check capabilities
        
        Args:
            reciter_id: Identifier for the reciter
            url_path: URL path for the reciter's audio files
            min_file_size: Minimum expected file size in bytes (default 5KB)
        """
        self.reciter_id = reciter_id
        self.url_path = url_path
        self.min_file_size = min_file_size
        self.base_source_url = "https://everyayah.com/data"
        
        # Target directory in your asset repo
        self.target_dir = Path(f"audio/quran/{url_path}")
        self.target_dir.mkdir(parents=True, exist_ok=True)
        
        # Progress tracking file
        self.progress_file = self.target_dir / ".download_progress.json"
        self.progress = self.load_progress()
        
        # Quran Structure: 114 Surahs with ayah counts
        self.ayah_counts = [
            7, 286, 200, 176, 120, 165, 206, 75, 129, 109, # 1-10
            123, 111, 43, 52, 99, 128, 111, 110, 98, 135, # 11-20
            112, 78, 118, 64, 77, 227, 93, 88, 69, 60, # 21-30
            34, 30, 73, 54, 45, 83, 182, 88, 75, 85, # 31-40
            54, 53, 89, 59, 37, 35, 38, 29, 18, 45, # 41-50
            60, 49, 62, 55, 78, 96, 29, 22, 24, 13, # 51-60
            14, 11, 11, 18, 12, 12, 30, 52, 52, 44, # 61-70
            28, 28, 20, 56, 40, 31, 50, 40, 46, 42, # 71-80
            29, 19, 36, 25, 22, 17, 19, 26, 30, 20, # 81-90
            15, 21, 11, 8, 8, 19, 5, 8, 8, 11, # 91-100
            11, 8, 3, 9, 5, 4, 7, 3, 6, 3, # 101-110
            5, 4, 5, 6 # 111-114
        ]
        
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        self.stats = {
            'downloaded': 0,
            'skipped': 0,
            'corrupted': 0,
            'failed': 0,
            'redownloaded': 0
        }
    
    def load_progress(self):
        """Load progress from JSON file"""
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r') as f:
                    return json.load(f)
            except:
                return {'completed_files': {}, 'last_surah': 0}
        return {'completed_files': {}, 'last_surah': 0}
    
    def save_progress(self):
        """Save progress to JSON file"""
        with open(self.progress_file, 'w') as f:
            json.dump(self.progress, f, indent=2)
    
    def is_file_valid(self, file_path):
        """
        Check if a downloaded file is valid (not corrupt)
        
        Args:
            file_path: Path to the file to check
            
        Returns:
            bool: True if file is valid, False otherwise
        """
        if not os.path.exists(file_path):
            return False
        
        file_size = os.path.getsize(file_path)
        
        # Check if file size is reasonable (not too small)
        if file_size < self.min_file_size:
            return False
        
        # Additional check: try to read first few bytes to ensure it's not empty/corrupt
        try:
            with open(file_path, 'rb') as f:
                header = f.read(10)
                # MP3 files typically start with ID3 or 0xFF 0xFB
                if len(header) < 10:
                    return False
        except:
            return False
        
        return True
    
    def download_file(self, source_url, target_path, file_name, max_retries=3):
        """
        Download a single file with retry mechanism
        
        Args:
            source_url: URL to download from
            target_path: Path to save the file
            file_name: Name of the file (for logging)
            max_retries: Maximum number of retry attempts
            
        Returns:
            bool: True if download succeeded, False otherwise
        """
        for attempt in range(max_retries):
            try:
                response = requests.get(source_url, headers=self.headers, stream=True, timeout=30)
                
                if response.status_code == 200:
                    # Download to temporary file first
                    temp_path = str(target_path) + '.tmp'
                    
                    with open(temp_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                    
                    # Verify the downloaded file
                    if self.is_file_valid(temp_path):
                        # Move temp file to actual location
                        os.replace(temp_path, target_path)
                        return True
                    else:
                        print(f"  ⚠️ Downloaded file appears corrupt: {file_name}")
                        if os.path.exists(temp_path):
                            os.remove(temp_path)
                        if attempt < max_retries - 1:
                            print(f"  🔄 Retrying ({attempt + 2}/{max_retries})...")
                            time.sleep(2 ** attempt)  # Exponential backoff
                        continue
                else:
                    print(f"  ❌ HTTP {response.status_code}: {file_name}")
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)
                    continue
                    
            except Exception as e:
                print(f"  ❌ Error downloading {file_name}: {e}")
                if attempt < max_retries - 1:
                    print(f"  🔄 Retrying ({attempt + 2}/{max_retries})...")
                    time.sleep(2 ** attempt)
                continue
        
        return False
    
    def verify_and_fix_existing_files(self):
        """
        Verify all existing files and mark corrupt ones for re-download
        
        Returns:
            list: List of corrupt file names
        """
        print(f"\n🔍 Verifying existing files in {self.target_dir}...")
        corrupt_files = []
        total_files = 0
        
        for surah_idx, count in enumerate(self.ayah_counts):
            surah_num = surah_idx + 1
            
            for ayah_num in range(1, count + 1):
                file_name = f"{surah_num:03d}{ayah_num:03d}.mp3"
                target_path = self.target_dir / file_name
                
                if target_path.exists():
                    total_files += 1
                    if not self.is_file_valid(target_path):
                        corrupt_files.append(file_name)
                        # Remove from completed files so it will be re-downloaded
                        if file_name in self.progress['completed_files']:
                            del self.progress['completed_files'][file_name]
                        print(f"  ⚠️ Corrupt file found: {file_name} (size: {os.path.getsize(target_path)} bytes)")
        
        if corrupt_files:
            print(f"\n⚠️ Found {len(corrupt_files)} corrupt file(s) out of {total_files} total files")
            print(f"These files will be re-downloaded.")
            self.save_progress()
        else:
            print(f"✅ All {total_files} existing files are valid!")
        
        return corrupt_files
    
    def download_quran_audio(self, download_all=True, verify_first=True):
        """
        Download Quran audio files with resume capability
        
        Args:
            download_all: If True, download all surahs. If False, only Surah 1 and 112-114
            verify_first: If True, verify existing files before downloading
        """
        print(f"\n{'='*60}")
        print(f"📖 Starting download for reciter: {self.reciter_id}")
        print(f"📁 Target directory: {self.target_dir}")
        print(f"{'='*60}\n")
        
        # Verify existing files first
        if verify_first:
            self.verify_and_fix_existing_files()
        
        total_files = sum(self.ayah_counts)
        print(f"\n📊 Total files to download: {total_files}")
        
        if self.progress['last_surah'] > 0:
            print(f"🔄 Resuming from Surah {self.progress['last_surah']}...")
        
        # Iterate through all Surahs
        for surah_idx, count in enumerate(self.ayah_counts):
            surah_num = surah_idx + 1
            
            # Skip if not downloading all and not in the selected range
            if not download_all and surah_num != 1 and surah_num < 112:
                continue
            
            print(f"\n📗 Surah {surah_num} ({count} ayahs)")
            
            for ayah_num in range(1, count + 1):
                file_name = f"{surah_num:03d}{ayah_num:03d}.mp3"
                source_url = f"{self.base_source_url}/{self.url_path}/{file_name}"
                target_path = self.target_dir / file_name
                
                # Check if already downloaded and valid
                if file_name in self.progress['completed_files']:
                    if self.is_file_valid(target_path):
                        self.stats['skipped'] += 1
                        continue
                    else:
                        # File was marked complete but is actually corrupt
                        print(f"  🔄 Re-downloading corrupt file: {file_name}")
                        self.stats['corrupted'] += 1
                
                # Check if file exists but not in progress
                if target_path.exists() and self.is_file_valid(target_path):
                    self.progress['completed_files'][file_name] = True
                    self.stats['skipped'] += 1
                    continue
                
                # Download the file
                is_redownload = target_path.exists()
                success = self.download_file(source_url, target_path, file_name)
                
                if success:
                    self.progress['completed_files'][file_name] = True
                    if is_redownload:
                        self.stats['redownloaded'] += 1
                        print(f"  ✅ Re-downloaded: {file_name}")
                    else:
                        self.stats['downloaded'] += 1
                        print(f"  ✅ Downloaded: {file_name}")
                else:
                    self.stats['failed'] += 1
                    print(f"  ❌ Failed to download: {file_name}")
                
                # Show progress every 10 files
                total_processed = sum(self.stats.values())
                if total_processed % 10 == 0:
                    completed = self.stats['downloaded'] + self.stats['skipped'] + self.stats['redownloaded']
                    print(f"\n  📊 Progress: {completed}/{total_files} files ({(completed/total_files)*100:.1f}%)")
                
                # Be polite to the server
                time.sleep(0.1)
            
            # Save progress after each surah
            self.progress['last_surah'] = surah_num
            self.save_progress()
        
        self.print_summary()
    
    def print_summary(self):
        """Print download summary statistics"""
        print(f"\n{'='*60}")
        print(f"📊 DOWNLOAD SUMMARY FOR {self.reciter_id}")
        print(f"{'='*60}")
        print(f"✅ Downloaded:     {self.stats['downloaded']} files")
        print(f"🔄 Re-downloaded:  {self.stats['redownloaded']} files")
        print(f"⏭️  Skipped:        {self.stats['skipped']} files")
        print(f"⚠️  Corrupt/Fixed:  {self.stats['corrupted']} files")
        print(f"❌ Failed:         {self.stats['failed']} files")
        print(f"{'='*60}\n")

if __name__ == "__main__":
    # Configuration
    DOWNLOAD_ALL = True  # Set to False to only download Surah 1 and 112-114
    VERIFY_EXISTING = True  # Set to True to verify existing files before downloading
    MIN_FILE_SIZE = 5000  # Minimum file size in bytes (5KB)
    
    # You can uncomment other reciters to download them too
    reciters = [
        ("alafasy", "Alafasy_128kbps"),
        # ("abdulbasit", "Abdul_Basit_Murattal_64kbps"), 
        # ("husary", "Husary_128kbps"),
        # ("minshawi", "Minshawy_Murattal_128kbps"),
    ]
    
    for reciter_id, url_path in reciters:
        downloader = QuranDownloader(reciter_id, url_path, min_file_size=MIN_FILE_SIZE)
        downloader.download_quran_audio(download_all=DOWNLOAD_ALL, verify_first=VERIFY_EXISTING)
