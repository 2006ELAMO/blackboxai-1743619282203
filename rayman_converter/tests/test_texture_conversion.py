import unittest
import sys
from pathlib import Path

# Add tools directory to path
sys.path.append(str(Path(__file__).parent.parent/'tools'))
from convert_clean import convert_textures

class TestTextureConversion(unittest.TestCase):
    def test_dds_to_tm2_conversion(self):
        """Test basic DDS to TM2 conversion"""
        test_data = b'TESTDDS_TEXTURE_DATA'
        converted = convert_textures(test_data)
        self.assertIn(b'TM2', converted)
        self.assertNotIn(b'DDS', converted)

    def test_flag_position(self):
        """Verify flags are set at correct position"""
        test_data = b'DDS' + b'\x00'*125  # 122 + 3 byte header
        converted = convert_textures(test_data)
        self.assertEqual(converted[122:124], b'\x01\x01')

    def test_multiple_textures(self):
        """Test conversion of multiple textures"""
        test_data = b'DDS_TEXTURE1DDS_TEXTURE2'
        converted = convert_textures(test_data)
        self.assertEqual(converted.count(b'TM2'), 2)

    def test_header_conversion(self):
        """Test Wii to PS2 header conversion"""
        from convert_clean import convert_wii_to_ps2_header
        wii_header = b'BF01\x02\x00'
        ps2_header = convert_wii_to_ps2_header(wii_header)
        self.assertEqual(ps2_header[:4], b'BF02')

    def test_file_operations(self):
        """Test full file conversion"""
        from convert_clean import convert_file
        import tempfile
        with tempfile.NamedTemporaryFile() as tmp:
            test_data = b'BF01\x02\x00DDS_TEXTURE'
            tmp.write(test_data)
            tmp.flush()
            convert_file(tmp.name, 'test_output.bf')
            with open('test_output.bf', 'rb') as f:
                self.assertEqual(f.read(4), b'BF02')

if __name__ == '__main__':
    unittest.main()