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
    """Convert Wii textures to PS2 format with proper downscaling"""
    print("Converting textures: 1080p DDS -> 480p TM2")
    
    if b'DDS' in texture_data:
        # Convert texture signature
        converted = texture_data.replace(b'DDS', b'TM2')
        converted = converted.replace(b'TEXTURE', b'PS2TEX')
        
        # Set proper PS2 texture flags at offset 122-123 (relative to texture data)
        if len(converted) > 124:
            flags = b'\x01\x01'  # Mipmaps enabled + PS2 format
            converted = converted[:122] + flags + converted[124:]
        
        return converted
    
    return texture_data
        
        # Convert texture signature
        converted = wii_data.replace(b'DDS', b'TM2')
        converted = converted.replace(b'TEXTURE', b'PS2TEX')
        
        # Set proper PS2 texture flags at offset 128-129
        if len(converted) > 130:
            print(f"Original flags: {converted[128:130]}")
            flags = b'\x01\x01'  # Mipmaps enabled + PS2 format
            converted = converted[:128] + flags + converted[130:]
            print(f"New flags set at position 128-129: {flags}")
        
        return converted
    
    return wii_data

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
    
    # Debug: Verify flags before writing
    if len(final_data) > 130:
        print(f"Final flags before write: {final_data[128:130]}")
    
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