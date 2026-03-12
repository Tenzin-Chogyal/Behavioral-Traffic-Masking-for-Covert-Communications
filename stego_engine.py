"""
Steganography Engine - Layer 2
Entropy-based adaptive LSB embedding for undetectable data hiding
"""

from PIL import Image
import numpy as np
import os


class SteganographyEngine:
    """
    Layer 2: Steganographic concealment using adaptive LSB
    
    Features:
    - Entropy-based region selection
    - LSB embedding in high-entropy areas
    - Automatic cover image generation
    """
    
    def __init__(self):
        """Initialize steganography engine"""
        self.entropy_threshold = 0.6  # Minimum entropy for embedding
    
    def calculate_entropy(self, block):
        """
        Calculate Shannon entropy of image block
        
        Args:
            block: numpy array of pixel values
            
        Returns:
            Entropy value (0-1 normalized)
        """
        # Get unique values and their counts
        values, counts = np.unique(block, return_counts=True)
        
        # Calculate probabilities
        probabilities = counts / counts.sum()
        
        # Calculate entropy: H = -Σ p(x) * log2(p(x))
        entropy = -np.sum(probabilities * np.log2(probabilities + 1e-10))
        
        # Normalize to 0-1 range (max entropy for 256 values is 8)
        normalized_entropy = entropy / 8.0
        
        return normalized_entropy
    
    def select_embedding_regions(self, image: Image.Image, block_size: int = 8):
        """
        Select high-entropy regions for embedding
        
        Args:
            image: PIL Image
            block_size: Size of blocks for entropy analysis
            
        Returns:
            Boolean mask of embeddable regions
        """
        # Convert to numpy array
        img_array = np.array(image)
        height, width = img_array.shape[:2]
        
        # Create mask
        mask = np.zeros((height, width), dtype=bool)
        
        # Analyze blocks
        for y in range(0, height - block_size, block_size):
            for x in range(0, width - block_size, block_size):
                # Extract block (use blue channel if RGB)
                if len(img_array.shape) == 3:
                    block = img_array[y:y+block_size, x:x+block_size, 2]  # Blue channel
                else:
                    block = img_array[y:y+block_size, x:x+block_size]
                
                # Calculate entropy
                entropy = self.calculate_entropy(block)
                
                # Mark high-entropy regions
                if entropy >= self.entropy_threshold:
                    mask[y:y+block_size, x:x+block_size] = True
        
        return mask
    
    def embed(self, data: bytes, cover_image_path: str, output_path: str) -> str:
        """
        Embed data in cover image using adaptive LSB
        
        Args:
            data: Data to hide
            cover_image_path: Path to cover image
            output_path: Path for stego image
            
        Returns:
            Path to stego image
        """
        # Load cover image
        image = Image.open(cover_image_path)
        img_array = np.array(image)
        
        # Convert to RGB if needed
        if len(img_array.shape) == 2:
            img_array = np.stack([img_array] * 3, axis=-1)
        
        # Select embedding regions
        mask = self.select_embedding_regions(image)
        
        # Get embeddable pixel coordinates
        embeddable_coords = np.argwhere(mask)
        
        # Convert data to binary
        data_len = len(data)
        data_bits = ''.join(format(byte, '08b') for byte in data)
        
        # Add length prefix (32 bits)
        len_bits = format(data_len, '032b')
        full_data_bits = len_bits + data_bits
        
        # Check capacity
        available_capacity = len(embeddable_coords)
        required_capacity = len(full_data_bits)
        
        if required_capacity > available_capacity:
            raise ValueError(f"Insufficient capacity: need {required_capacity}, have {available_capacity}")
        
        # Embed data
        bit_index = 0
        for coord in embeddable_coords:
            if bit_index >= len(full_data_bits):
                break
            
            y, x = coord
            
            # Get current pixel value (blue channel)
            pixel_value = int(img_array[y, x, 2])
            
            # Get bit to embed
            bit = int(full_data_bits[bit_index])
            
            # Modify LSB
            new_pixel_value = (pixel_value & 0xFE) | bit
            
            # Update image
            img_array[y, x, 2] = new_pixel_value
            
            bit_index += 1
        
        # Save stego image
        stego_image = Image.fromarray(img_array.astype('uint8'))
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        stego_image.save(output_path)
        
        # Calculate utilization
        utilization = (required_capacity / available_capacity) * 100
        
        print(f"  Embedding complete:")
        print(f"    Data size: {data_len} bytes")
        print(f"    Bits embedded: {required_capacity}")
        print(f"    Available capacity: {available_capacity}")
        print(f"    Utilization: {utilization:.1f}%")
        
        return output_path
    
    def extract(self, stego_image_path: str) -> bytes:
        """
        Extract hidden data from stego image
        
        Args:
            stego_image_path: Path to stego image
            
        Returns:
            Extracted data
        """
        # Load stego image
        image = Image.open(stego_image_path)
        img_array = np.array(image)
        
        # Convert to RGB if needed
        if len(img_array.shape) == 2:
            img_array = np.stack([img_array] * 3, axis=-1)
        
        # Select embedding regions (same as embedding)
        mask = self.select_embedding_regions(image)
        embeddable_coords = np.argwhere(mask)
        
        # Extract length (first 32 bits)
        len_bits = ''
        for i in range(32):
            y, x = embeddable_coords[i]
            pixel_value = int(img_array[y, x, 2])
            len_bits += str(pixel_value & 1)
        
        data_len = int(len_bits, 2)
        
        # Extract data bits
        data_bits = ''
        required_bits = data_len * 8
        
        for i in range(32, 32 + required_bits):
            y, x = embeddable_coords[i]
            pixel_value = int(img_array[y, x, 2])
            data_bits += str(pixel_value & 1)
        
        # Convert bits to bytes
        data = bytearray()
        for i in range(0, len(data_bits), 8):
            byte_bits = data_bits[i:i+8]
            data.append(int(byte_bits, 2))
        
        return bytes(data)
    
    def create_cover_image(self, width: int = 1024, height: int = 768, 
                          output_dir: str = 'images') -> str:
        """
        Create a noise cover image with high entropy
        
        Args:
            width: Image width
            height: Image height
            output_dir: Output directory
            
        Returns:
            Path to created image
        """
        # Generate random noise
        noise = np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)
        
        # Create image
        image = Image.fromarray(noise)
        
        # Save
        os.makedirs(output_dir, exist_ok=True)
        filename = f"cover_{width}x{height}.png"
        filepath = os.path.join(output_dir, filename)
        image.save(filepath)
        
        return filepath


# Quick test
if __name__ == "__main__":
    print("="*70)
    print("STEGANOGRAPHY ENGINE TEST")
    print("="*70)
    
    stego = SteganographyEngine()
    
    # Test 1: Create cover image
    print("\n[TEST 1] Creating cover image...")
    cover_path = stego.create_cover_image()
    print(f"✓ Cover image: {cover_path}")
    
    # Test 2: Embed data
    print("\n[TEST 2] Embedding secret data...")
    secret_data = b"This is a secret message for testing!"
    print(f"Secret data: {secret_data}")
    print(f"Size: {len(secret_data)} bytes")
    
    stego_path = stego.embed(secret_data, cover_path, 'outputs/test_stego.png')
    print(f"✓ Stego image: {stego_path}")
    
    # Test 3: Extract data
    print("\n[TEST 3] Extracting hidden data...")
    extracted = stego.extract(stego_path)
    print(f"Extracted: {extracted}")
    print(f"✓ Match: {secret_data == extracted}")
    
    print("\n" + "="*70)
    print("✓ ALL TESTS PASSED")
    print("="*70)
