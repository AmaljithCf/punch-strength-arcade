#!/usr/bin/env python3
"""
Convert WAV files to C header files for embedding in Arduino sketch
Creates audio_data.h with all audio files as byte arrays
"""

import os
import sys
from pathlib import Path

# Configuration
AUDIO_DIR = "audio_files"
OUTPUT_FILE = "audio_data.h"

# Audio file list
REQUIRED_FILES = (
    [f"{i}.wav" for i in range(1, 10)] +           # 1-9
    [f"{i}.wav" for i in range(10, 20)] +          # 10-19
    [f"{i}.wav" for i in range(20, 100, 10)] +     # 20-90
    [f"{i}.wav" for i in range(100, 1000, 100)] +  # 100-900
    ['and.wav']
)

def convert_wav_to_array(filepath, var_name):
    """Convert WAV file to C array string"""
    with open(filepath, 'rb') as f:
        data = f.read()
    
    # Skip WAV header (first 44 bytes)
    audio_data = data[44:]  # Only audio samples
    
    array_str = f"// {os.path.basename(filepath)} - {len(audio_data)} bytes\n"
    array_str += f"const uint8_t {var_name}[] PROGMEM = {{\n"
    
    # Write bytes in rows of 16
    for i in range(0, len(audio_data), 16):
        chunk = audio_data[i:i+16]
        hex_values = ', '.join(f'0x{b:02X}' for b in chunk)
        array_str += f"  {hex_values}"
        if i + 16 < len(audio_data):
            array_str += ","
        array_str += "\n"
    
    array_str += "};\n"
    array_str += f"const uint32_t {var_name}_len = {len(audio_data)};\n\n"
    
    return array_str

def get_var_name(filename):
    """Convert filename to valid C variable name"""
    # Remove .wav extension
    name = filename.replace('.wav', '')
    
    # Handle special cases
    if name == 'and':
        return 'audio_and'
    
    # Number files
    return f'audio_{name}'

def create_lookup_table(file_list):
    """Create lookup table structure"""
    lookup = "// Lookup table for audio files\n"
    lookup += "struct AudioFile {\n"
    lookup += "  const char* name;\n"
    lookup += "  const uint8_t* data;\n"
    lookup += "  uint32_t length;\n"
    lookup += "};\n\n"
    
    lookup += f"const AudioFile audioFiles[] = {{\n"
    
    for filename in file_list:
        var_name = get_var_name(filename)
        lookup += f'  {{"{filename}", {var_name}, {var_name}_len}},\n'
    
    lookup += "};\n\n"
    lookup += f"const int audioFileCount = {len(file_list)};\n\n"
    
    return lookup

def main():
    print("="*60)
    print("WAV TO C HEADER CONVERTER")
    print("="*60)
    
    # Check if audio directory exists
    if not os.path.exists(AUDIO_DIR):
        print(f"\n❌ ERROR: Directory '{AUDIO_DIR}/' not found!")
        print("Please run generate_audio.py first")
        sys.exit(1)
    
    # Check which files exist
    existing_files = []
    missing_files = []
    total_size = 0
    
    print(f"\n📂 Checking files in {AUDIO_DIR}/...")
    
    for filename in REQUIRED_FILES:
        filepath = os.path.join(AUDIO_DIR, filename)
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            # Subtract 44 bytes for WAV header
            data_size = size - 44
            total_size += data_size
            existing_files.append(filename)
            print(f"  ✓ {filename:12s} - {data_size:>6,} bytes (audio data)")
        else:
            missing_files.append(filename)
            print(f"  ✗ {filename:12s} - MISSING!")
    
    if missing_files:
        print(f"\n⚠️  WARNING: {len(missing_files)} files missing!")
        print("Proceeding with available files only...")
    
    print(f"\n📊 Summary:")
    print(f"  Files found: {len(existing_files)}/{len(REQUIRED_FILES)}")
    print(f"  Total audio data: {total_size:,} bytes ({total_size/1024:.1f} KB)")
    
    # Check if it will fit in flash
    FLASH_SIZE = 1500 * 1024  # 1.5MB typical for MG24
    if total_size > FLASH_SIZE * 0.6:
        print(f"\n⚠️  WARNING: Audio data is large ({total_size/1024:.0f}KB)")
        print(f"  This may not fit with your program code!")
        print(f"  Consider:")
        print(f"    - Using shorter audio clips")
        print(f"    - Lower sample rate (4kHz instead of 8kHz)")
        print(f"    - Using SD card instead")
    
    # Ask for confirmation
    response = input(f"\n🔄 Convert {len(existing_files)} files to C header? (y/n): ")
    if response.lower() != 'y':
        print("Cancelled.")
        sys.exit(0)
    
    # Generate header file
    print(f"\n⚙️  Generating {OUTPUT_FILE}...")
    
    with open(OUTPUT_FILE, 'w') as f:
        # Write header guard and info
        f.write("// Auto-generated audio data from WAV files\n")
        f.write("// DO NOT EDIT MANUALLY\n")
        f.write(f"// Generated from {len(existing_files)} WAV files\n")
        f.write(f"// Total audio data: {total_size:,} bytes\n\n")
        f.write("#ifndef AUDIO_DATA_H\n")
        f.write("#define AUDIO_DATA_H\n\n")
        f.write("#include <Arduino.h>\n\n")
        
        # Convert each file
        for i, filename in enumerate(existing_files, 1):
            filepath = os.path.join(AUDIO_DIR, filename)
            var_name = get_var_name(filename)
            
            print(f"  [{i}/{len(existing_files)}] Converting {filename}...", end='')
            
            array_str = convert_wav_to_array(filepath, var_name)
            f.write(array_str)
            
            print(" ✓")
        
        # Add lookup table
        print("  Creating lookup table...", end='')
        f.write(create_lookup_table(existing_files))
        print(" ✓")
        
        # Close header guard
        f.write("#endif // AUDIO_DATA_H\n")
    
    # Show results
    output_size = os.path.getsize(OUTPUT_FILE)
    print(f"\n✅ Success!")
    print(f"  Created: {OUTPUT_FILE}")
    print(f"  Header size: {output_size:,} bytes ({output_size/1024:.1f} KB)")
    
    print("\n" + "="*60)
    print("NEXT STEPS")
    print("="*60)
    print(f"1. Copy {OUTPUT_FILE} to your Arduino sketch folder")
    print(f"   (same directory as your .ino file)")
    print()
    print("2. In your sketch, add:")
    print("   #include \"audio_data.h\"")
    print()
    print("3. Upload to XIAO MG24 and test!")
    print()
    print("⚠️  Note: Large sketches may take 2-3 minutes to upload")
    print("="*60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)