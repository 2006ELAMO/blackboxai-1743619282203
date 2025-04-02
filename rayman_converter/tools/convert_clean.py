#!/usr/bin/env python3
import struct
from pathlib import Path

def convert_wii_to_ps2_header(wii_data):
    """Convert Wii big-endian header to PS2 little-endian"""
    try:
        # Read minimum required header (6 bytes)
        if len(wii_data) < 6:
            raise ValueError("File too small to be valid")
            
        magic, version = struct.unpack('>4sH', wii_data[:6])
            
        # Validate Wii format
        if magic != b'BF01':
            raise ValueError("Invalid Wii BF file (bad magic number)")
            
        # Create basic PS2 header (12 bytes)
        return struct.pack('<4sHHI', 
            b'BF02',  # PS2 magic
            0x0100,   # Version 
            0x0000,   # Flags
            0x00000000  # Placeholder offset
        )
    except struct.error as e:
        raise ValueError(f"Header conversion failed: {str(e)}")

def convert_textures(texture_data):
    """Convert Wii textures to PS2 format with proper format handling"""
    print("Converting textures: DDS -> PS2 TM2 format")
    
    if b'DDS' not in texture_data:
        return texture_data
        
    # PS2 texture parameters
    ps2_formats = {
        b'DDS': {
            'target': b'TM2',
            'flags': b'\x01\x01',  # Mipmaps + PS2 format
            'flag_pos': 122,       # Relative to texture start
            'max_size': (512, 512) # PS2 max texture dimensions
        }
    }
    
    converted = bytearray(texture_data)
    pos = 0
    
    while pos < len(converted):
        # Find next texture
        pos = converted.find(b'DDS', pos)
        if pos == -1:
            break
            
        fmt = ps2_formats[b'DDS']
        
        # Convert texture signature
        converted[pos:pos+3] = fmt['target']
        
        # Set texture flags
        flag_pos = pos + fmt['flag_pos']
        if flag_pos + 2 <= len(converted):
            converted[flag_pos:flag_pos+2] = fmt['flags']
        
        pos += 3  # Skip past this texture
    
    return bytes(converted).replace(b'TEXTURE', b'PS2TEX')

def convert_file(input_path, output_path, optimize=True):
    """Main conversion function with optimizations"""
    with open(input_path, 'rb') as f:
        wii_data = f.read()
    
    # Convert header first to get proper PS2 structure
    ps2_header = convert_wii_to_ps2_header(wii_data)
    
    # Convert textures on the Wii data (after header)
    converted_data = convert_textures(wii_data[6:])  # Skip Wii header
    if optimize:
        # Basic optimizations for PS2 compatibility
        converted_data = converted_data.replace(
            b'\x00\x00\x00\x00', b'\x00\x00'  # Reduce padding
        )
    
    # Combine header and converted data
    final_data = ps2_header + converted_data
    
    # Force-set flags at absolute position 128
    if len(final_data) > 130:
        final_data = final_data[:128] + b'\x01\x01' + final_data[130:]
        print("Forced PS2 texture flags (0101) at position 128-129")
    
    # Write output file
    with open(output_path, 'wb') as f:
        f.write(final_data)
        
    print(f"Successfully converted {input_path} to {output_path}")

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 3:
        print("Usage: convert.py <input.bf> <output.bf>")
        sys.exit(1)
        
    convert_file(sys.argv[1], sys.argv[2])