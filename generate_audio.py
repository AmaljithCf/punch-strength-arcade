#!/usr/bin/env python3
"""
Punch Arcade Machine - Audio File Generator
Generates all 35 required WAV files (8kHz, mono, 8-bit) for the project
"""

import os
import sys
from pathlib import Path

try:
    from gtts import gTTS
    from pydub import AudioSegment
except ImportError:
    print("ERROR: Required libraries not installed!")
    print("\nPlease install required packages:")
    print("  pip install gtts pydub")
    print("\nNote: pydub also requires ffmpeg to be installed:")
    print("  - Windows: Download from https://ffmpeg.org/download.html")
    print("  - Mac: brew install ffmpeg")
    print("  - Linux: sudo apt-get install ffmpeg")
    sys.exit(1)

# Configuration
OUTPUT_DIR = "audio_files"
TEMP_DIR = "temp_audio"
SAMPLE_RATE = 8000  # 8kHz
CHANNELS = 1        # Mono
SAMPLE_WIDTH = 1    # 8-bit (1 byte)

# Audio vocabulary
NUMBERS_1_9 = {
    1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five',
    6: 'six', 7: 'seven', 8: 'eight', 9: 'nine'
}

NUMBERS_10_19 = {
    10: 'ten', 11: 'eleven', 12: 'twelve', 13: 'thirteen', 14: 'fourteen',
    15: 'fifteen', 16: 'sixteen', 17: 'seventeen', 18: 'eighteen', 19: 'nineteen'
}

NUMBERS_TENS = {
    20: 'twenty', 30: 'thirty', 40: 'forty', 50: 'fifty',
    60: 'sixty', 70: 'seventy', 80: 'eighty', 90: 'ninety'
}

NUMBERS_HUNDREDS = {
    100: 'one hundred', 200: 'two hundred', 300: 'three hundred',
    400: 'four hundred', 500: 'five hundred', 600: 'six hundred',
    700: 'seven hundred', 800: 'eight hundred', 900: 'nine hundred'
}


def create_directories():
    """Create necessary directories"""
    Path(OUTPUT_DIR).mkdir(exist_ok=True)
    Path(TEMP_DIR).mkdir(exist_ok=True)
    print(f"✓ Created directories: {OUTPUT_DIR}/ and {TEMP_DIR}/")


def generate_tts(text, filename):
    """Generate TTS audio and save as MP3"""
    try:
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(filename)
        return True
    except Exception as e:
        print(f"  ✗ Failed to generate TTS for '{text}': {e}")
        return False


def convert_to_wav(mp3_file, wav_file):
    """Convert MP3 to 8kHz mono 8-bit WAV"""
    try:
        # Load MP3
        audio = AudioSegment.from_mp3(mp3_file)
        
        # Convert to target format
        audio = audio.set_frame_rate(SAMPLE_RATE)  # 8kHz
        audio = audio.set_channels(CHANNELS)       # Mono
        audio = audio.set_sample_width(SAMPLE_WIDTH)  # 8-bit
        
        # Normalize audio to prevent clipping
        audio = audio.normalize()
        
        # Export as WAV
        audio.export(
            wav_file,
            format="wav",
            parameters=["-acodec", "pcm_u8"]  # Unsigned 8-bit PCM
        )
        return True
    except Exception as e:
        print(f"  ✗ Failed to convert {mp3_file}: {e}")
        return False


def generate_audio_file(number, text):
    """Generate single audio file (TTS + convert to WAV)"""
    mp3_path = os.path.join(TEMP_DIR, f"{number}_temp.mp3")
    wav_path = os.path.join(OUTPUT_DIR, f"{number}.wav")
    
    # Generate TTS MP3
    if not generate_tts(text, mp3_path):
        return False
    
    # Convert to WAV
    if not convert_to_wav(mp3_path, wav_path):
        return False
    
    # Clean up temp file
    try:
        os.remove(mp3_path)
    except:
        pass
    
    return True


def generate_all_files():
    """Generate all 35 audio files"""
    print("\n" + "="*60)
    print("GENERATING AUDIO FILES FOR PUNCH ARCADE MACHINE")
    print("="*60 + "\n")
    
    total_files = 35
    success_count = 0
    
    # Generate 1-9
    print(" Generating numbers 1-9...")
    for num, text in NUMBERS_1_9.items():
        if generate_audio_file(num, text):
            print(f"  ✓ {num}.wav - '{text}'")
            success_count += 1
        else:
            print(f"  ✗ Failed: {num}.wav")
    
    # Generate 10-19
    print("\n Generating numbers 10-19...")
    for num, text in NUMBERS_10_19.items():
        if generate_audio_file(num, text):
            print(f"  ✓ {num}.wav - '{text}'")
            success_count += 1
        else:
            print(f"  ✗ Failed: {num}.wav")
    
    # Generate 20-90 (tens)
    print("\n Generating tens (20-90)...")
    for num, text in NUMBERS_TENS.items():
        if generate_audio_file(num, text):
            print(f"  ✓ {num}.wav - '{text}'")
            success_count += 1
        else:
            print(f"  ✗ Failed: {num}.wav")
    
    # Generate 100-900 (hundreds)
    print("\n Generating hundreds (100-900)...")
    for num, text in NUMBERS_HUNDREDS.items():
        if generate_audio_file(num, text):
            print(f"  ✓ {num}.wav - '{text}'")
            success_count += 1
        else:
            print(f"  ✗ Failed: {num}.wav")
    
    # Generate "and"
    print("\n Generating connector word...")
    if generate_audio_file('and', 'and'):
        print(f"  ✓ and.wav - 'and'")
        success_count += 1
    else:
        print(f"  ✗ Failed: and.wav")
    
    return success_count, total_files


def cleanup_temp():
    """Remove temporary directory"""
    try:
        import shutil
        shutil.rmtree(TEMP_DIR)
        print(f"\n✓ Cleaned up temporary files")
    except Exception as e:
        print(f"\n⚠ Could not remove temp directory: {e}")


def verify_files():
    """Verify all files were created correctly"""
    print("\n" + "="*60)
    print("VERIFYING GENERATED FILES")
    print("="*60 + "\n")
    
    required_files = (
        [f"{i}.wav" for i in range(1, 10)] +           # 1-9
        [f"{i}.wav" for i in range(10, 20)] +          # 10-19
        [f"{i}.wav" for i in range(20, 100, 10)] +     # 20-90
        [f"{i}.wav" for i in range(100, 1000, 100)] +  # 100-900
        ['and.wav']
    )
    
    missing_files = []
    total_size = 0
    
    for filename in required_files:
        filepath = os.path.join(OUTPUT_DIR, filename)
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            total_size += size
            print(f"  ✓ {filename:12s} - {size:>6,} bytes")
        else:
            missing_files.append(filename)
            print(f"  ✗ {filename:12s} - MISSING!")
    
    print(f"\n Total files: {len(required_files) - len(missing_files)}/{len(required_files)}")
    print(f" Total size: {total_size:,} bytes ({total_size/1024:.1f} KB)")
    
    if missing_files:
        print(f"\n⚠ WARNING: {len(missing_files)} files missing!")
        return False
    else:
        print("\n All files generated successfully!")
        return True


def show_usage_instructions():
    """Display instructions for using the generated files"""
    print("\n" + "="*60)
    print("NEXT STEPS")
    print("="*60 + "\n")
    
    print("1. Copy the audio_files/ directory to your Arduino sketch folder:")
    print("   YourSketch/")
    print("   ├── YourSketch.ino")
    print("   └── data/")
    print("       ├── 1.wav")
    print("       ├── 2.wav")
    print("       └── ... (all 35 files)")
    print()
    print("2. In Arduino IDE, go to: Tools → LittleFS Upload")
    print()
    print("3. Wait for upload to complete (2-3 minutes)")
    print()
    print("4. Upload your Arduino sketch and test!")
    print()
    print("="*60)


def test_score_announcement(score):
    """Show which files would be played for a given score"""
    print(f"\nTest Score: {score}")
    print("Files to play:")
    
    hundreds = (score // 100) * 100
    remainder = score % 100
    tens = (remainder // 10) * 10
    ones = remainder % 10
    
    # Play hundreds
    if hundreds > 0:
        print(f"  → {hundreds}.wav")
    
    # Play "and" if remainder
    if remainder > 0:
        print(f"  → and.wav")
    
    # Play tens and ones
    if remainder >= 20:
        print(f"  → {tens}.wav")
        if ones > 0:
            print(f"  → {ones}.wav")
    elif remainder >= 10:
        print(f"  → {remainder}.wav")
    elif ones > 0:
        print(f"  → {ones}.wav")


def main():
    """Main function"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║   PUNCH ARCADE MACHINE - AUDIO FILE GENERATOR v1.0          ║
║   Generates 35 WAV files (8kHz, Mono, 8-bit)                ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Check dependencies
    print("Checking dependencies...")
    try:
        import gtts
        import pydub
        print("  ✓ gtts installed")
        print("  ✓ pydub installed")
        
        # Check ffmpeg
        from pydub.utils import which
        if which("ffmpeg") is None:
            print("  ✗ ffmpeg not found in PATH!")
            print("\nPlease install ffmpeg:")
            print("  Windows: https://ffmpeg.org/download.html")
            print("  Mac: brew install ffmpeg")
            print("  Linux: sudo apt-get install ffmpeg")
            sys.exit(1)
        print("  ✓ ffmpeg found")
    except ImportError as e:
        print(f"  ✗ Missing dependency: {e}")
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Generate all files
    success_count, total_files = generate_all_files()
    
    # Cleanup
    cleanup_temp()
    
    # Verify
    all_good = verify_files()
    
    # Show results
    print("\n" + "="*60)
    print("GENERATION COMPLETE")
    print("="*60)
    print(f"\n Successfully generated {success_count}/{total_files} files")
    
    if all_good:
        print("\n All files are ready to use!")
        show_usage_instructions()
        
        # Test examples
        print("\nExample score announcements:")
        test_score_announcement(347)
        test_score_announcement(812)
        test_score_announcement(999)
    else:
        print("\n⚠ Some files are missing. Please check errors above.")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠ Generation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)