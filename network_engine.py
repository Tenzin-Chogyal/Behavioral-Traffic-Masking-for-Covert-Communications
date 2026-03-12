"""
Network Engine - Layer 3 with Dead Drop Integration
HTTP protocol mimicry + Dead drop client for server-mediated communication
"""

import requests
import time
from datetime import datetime
from PIL import Image
import io


class DeadDropClient:
    """
    Client for interacting with dead drop server
    Handles upload/download of steganographic images
    """
    
    def __init__(self, server_url='http://localhost:5000'):
        """
        Initialize dead drop client
        
        Args:
            server_url: URL of dead drop server
        """
        self.server_url = server_url.rstrip('/')
        self.upload_endpoint = f"{self.server_url}/api/upload"
        self.download_endpoint = f"{self.server_url}/api/download"
        self.list_endpoint = f"{self.server_url}/api/list"
        
        # Session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
    
    def upload_image(self, image_path, filename='photo.png'):
        """
        Upload steganographic image to dead drop server
        
        Args:
            image_path: Path to image file
            filename: Original filename (for mimicry)
        
        Returns:
            message_id: Unique ID for retrieving the message
        """
        try:
            # Read image
            with open(image_path, 'rb') as f:
                image_bytes = f.read()
            
            # Prepare multipart form data (mimics browser upload)
            files = {
                'file': (filename, image_bytes, 'image/png')
            }
            
            # Upload to server
            print(f"  [Dead Drop] Uploading to {self.server_url}...")
            response = self.session.post(
                self.upload_endpoint,
                files=files,
                timeout=30
            )
            
            if response.status_code == 201:
                data = response.json()
                message_id = data['message_id']
                print(f"  [Dead Drop] ✓ Upload successful")
                print(f"  [Dead Drop]   Message ID: {message_id}")
                print(f"  [Dead Drop]   Expires in: {data['expires_in_hours']} hours")
                return message_id
            else:
                error_msg = response.json().get('error', 'Unknown error')
                print(f"  [Dead Drop] ✗ Upload failed: {error_msg}")
                return None
                
        except requests.exceptions.ConnectionError:
            print(f"  [Dead Drop] ✗ Cannot connect to server at {self.server_url}")
            print(f"  [Dead Drop]   Make sure dead drop server is running!")
            print(f"  [Dead Drop]   Start with: python dead_drop_server.py")
            return None
        except Exception as e:
            print(f"  [Dead Drop] ✗ Upload error: {e}")
            return None
    
    def download_image(self, message_id, output_path):
        """
        Download steganographic image from dead drop server
        
        Args:
            message_id: Unique message identifier
            output_path: Where to save downloaded image
        
        Returns:
            True if successful, False otherwise
        """
        try:
            download_url = f"{self.download_endpoint}/{message_id}"
            
            print(f"  [Dead Drop] Downloading from {self.server_url}...")
            response = self.session.get(download_url, timeout=30)
            
            if response.status_code == 200:
                # Save image
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                
                print(f"  [Dead Drop] ✓ Download successful")
                print(f"  [Dead Drop]   Saved to: {output_path}")
                return True
            elif response.status_code == 404:
                print(f"  [Dead Drop] ✗ Message not found (may have expired)")
                return False
            else:
                error_msg = response.json().get('error', 'Unknown error')
                print(f"  [Dead Drop] ✗ Download failed: {error_msg}")
                return False
                
        except Exception as e:
            print(f"  [Dead Drop] ✗ Download error: {e}")
            return False
    
    def list_messages(self):
        """
        List available messages on server
        
        Returns:
            List of message dictionaries
        """
        try:
            response = self.session.get(self.list_endpoint, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data['messages']
            return []
        except Exception as e:
            print(f"  [Dead Drop] ✗ List error: {e}")
            return []
    
    def poll_for_new_messages(self, last_check_time=None):
        """
        Poll server for new messages
        
        Args:
            last_check_time: datetime of last check
        
        Returns:
            List of new message IDs
        """
        messages = self.list_messages()
        
        if last_check_time is None:
            return [msg['message_id'] for msg in messages]
        
        new_messages = []
        for msg in messages:
            upload_time = datetime.fromisoformat(msg['upload_time'])
            if upload_time > last_check_time:
                new_messages.append(msg['message_id'])
        
        return new_messages


class NetworkEngine:
    """
    Layer 3: Network communication with HTTP protocol mimicry
    Integrates with dead drop server for server-mediated communication
    """
    
    def __init__(self, dead_drop_url='http://localhost:5000'):
        """
        Initialize network engine
        
        Args:
            dead_drop_url: URL of dead drop server
        """
        self.dead_drop = DeadDropClient(dead_drop_url)
        self.messages_sent = 0
    
    def send_covert_packet(self, image_path: str):
        """
        Send covert packet via dead drop server
        
        Args:
            image_path: Path to steganographic image
        
        Returns:
            message_id for recipient to download
        """
        print(f"  [Layer 3] Preparing HTTP packet...")
        print(f"  [Layer 3] Protocol: HTTP POST (multipart/form-data)")
        print(f"  [Layer 3] Mimics: Photo upload to CDN")
        
        # Upload via dead drop
        message_id = self.dead_drop.upload_image(image_path, filename='IMG_4173.png')
        
        if message_id:
            self.messages_sent += 1
            print(f"  [Layer 3] ✓ Packet sent via dead drop server")
            print(f"  [Layer 3]   Message ID: {message_id}")
            return message_id
        else:
            print(f"  [Layer 3] ✗ Failed to send packet")
            return None
    
    def receive_covert_packet(self, message_id: str, output_path: str) -> bool:
        """
        Receive covert packet from dead drop server
        
        Args:
            message_id: Message ID to download
            output_path: Where to save received image
        
        Returns:
            True if successful
        """
        print(f"  [Layer 3] Protocol: HTTP GET")
        print(f"  [Layer 3] Mimics: Photo download from CDN")
        
        success = self.dead_drop.download_image(message_id, output_path)
        
        if success:
            print(f"  [Layer 3] ✓ Packet received from dead drop server")
        else:
            print(f"  [Layer 3] ✗ Failed to receive packet")
        
        return success
    
    def get_statistics(self):
        """Get network statistics"""
        return {
            'messages_sent': self.messages_sent,
            'dead_drop_url': self.dead_drop.server_url
        }


# Quick test
if __name__ == "__main__":
    print("="*70)
    print("NETWORK ENGINE + DEAD DROP TEST")
    print("="*70)
    
    print("\n⚠️  Make sure dead drop server is running!")
    print("    Start with: python dead_drop_server.py\n")
    
    input("Press Enter when server is ready...")
    
    # Create test image
    from PIL import Image
    import numpy as np
    
    print("\n[TEST 1] Creating test image...")
    noise = np.random.randint(0, 256, (800, 600, 3), dtype=np.uint8)
    img = Image.fromarray(noise)
    img.save('test_upload.png')
    print("✓ Test image created")
    
    # Test network engine
    print("\n[TEST 2] Testing network engine with dead drop...")
    network = NetworkEngine('http://localhost:5000')
    
    # Send
    print("\n--- SENDING ---")
    message_id = network.send_covert_packet('test_upload.png')
    
    if message_id:
        # Receive
        print("\n--- RECEIVING ---")
        success = network.receive_covert_packet(message_id, 'test_download.png')
        
        if success:
            print("\n" + "="*70)
            print("✓ ALL TESTS PASSED")
            print("="*70)
            print(f"Message ID: {message_id}")
            print("Images: test_upload.png → test_download.png")
        else:
            print("\n✗ Receive test failed")
    else:
        print("\n✗ Send test failed")
