#!/usr/bin/env python3
import binascii
import struct
import sys
from pathlib import Path

def analyze_header(file_path):
    """Analyze first 32 bytes of BF file"""
    with open(file_path, 'rb') as f:
        data = f.read(32)
        print(f"\nAnalysis of {file_path}:")
        print(f"Hex dump: {binascii.hexlify(data[:16]).decode('ascii')}...")
        
        # Check for Wii (big-endian)
        try:
            wii_magic = struct.unpack('>4s', data[:4])[0]
            if wii_magic == b'BF01':
                print(f"Wii format detected (Magic: {wii_magic.decode()})")
                return 'wii'
        except:
            pass
            
        # Check for PS2 (little-endian)
        try:
            ps2_magic = struct.unpack('<4s', data[:4])[0]
            if ps2_magic == b'BF02':
                print(f"PS2 format detected (Magic: {ps2_magic.decode()})")
                return 'ps2'
        except:
            pass
            
        return 'unknown'

if __name__ == '__main__':
    print("Rayman Raving Rabbids 2 BF File Analyzer")
    print("=======================================")
    
    if len(sys.argv) > 1:
        # Analyze specific file if path provided
        bf_files = [Path(sys.argv[1])]
    else:
        # Default to analyzing all source files
        source_dir = Path('../source_files')
        if not source_dir.exists():
            print("Error: source_files directory not found")
            exit(1)
            
        bf_files = list(source_dir.glob('*.bf'))
        if not bf_files:
            print("No .bf files found in source_files directory")
            exit(1)
        
    for bf_file in bf_files:
        if analyze_header(bf_file):
            print(f"{bf_file.name} appears to be valid Wii format")
        else:
            print(f"{bf_file.name} - unrecognized format")