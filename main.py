"""
Complete 4-Layer Covert Communication System with Dead Drop Architecture
Interactive Mode - Manual Message Input

Author: Tenzin Chogyal, Rishav Ranjan, Tanish C
Supervisor: Dr. Harinee S
"""

import time
import sys
import os
from datetime import datetime
from crypto_engine import CryptographicEngine
from stego_engine import SteganographyEngine
from network_engine import NetworkEngine
from adaptive_behavioral_engine import AdaptiveBehavioralEngine


class CovertCommunicationSystem:
    """
    Complete 4-layer covert communication system with dead drop architecture
    """
    
    def __init__(self, dead_drop_url='http://localhost:8080',
                 real_password="SecureOperationPassword2024",
                 duress_password="InnocentPhotoPassword2024"):
        """
        Initialize all 4 layers with dead drop support
        
        Args:
            dead_drop_url: URL of dead drop server (default port 8080)
            real_password: Password for real secret messages
            duress_password: Password for fake innocuous messages
        """
        print("="*70)
        print("🔒 COVERT COMMUNICATION SYSTEM - INITIALIZATION")
        print("="*70)
        print(f"Architecture: 4-Layer Defense-in-Depth with Dead Drop")
        print(f"Dead Drop Server: {dead_drop_url}")
        print()
        
        # Store config
        self.dead_drop_url = dead_drop_url
        
        # Test server connectivity first
        print("[Pre-Check] Testing dead drop server connectivity...")
        if not self._test_server_connection():
            print("  ✗ Cannot reach dead drop server!")
            print(f"\n⚠️  Make sure server is running:")
            print(f"   python dead_drop_server.py --port 8080")
            print(f"\n   Or change the port in this script.")
            raise ConnectionError("Dead drop server not reachable")
        print("  ✓ Dead drop server is reachable")
        print()
        
        # Layer 1: Cryptographic Engine
        print("[Layer 1] Initializing Cryptographic Engine...")
        self.crypto = CryptographicEngine(real_password, duress_password)
        print("  ✓ AES-256-GCM encryption ready")
        print("  ✓ Deniable encryption (dual password) ready")
        
        # Layer 2: Steganography Engine
        print("\n[Layer 2] Initializing Steganography Engine...")
        self.stego = SteganographyEngine()
        print("  ✓ Entropy-based adaptive LSB ready")
        
        # Layer 3: Network Engine (with Dead Drop)
        print("\n[Layer 3] Initializing Network Engine...")
        self.network = NetworkEngine(dead_drop_url)
        print("  ✓ HTTP protocol mimicry ready")
        print("  ✓ Dead drop client ready")
        
        # Layer 4: Adaptive Behavioral Engine
        print("\n[Layer 4] Initializing Adaptive Behavioral Engine...")
        self.behavioral = AdaptiveBehavioralEngine()
        print("  ✓ Circadian rhythm modeling ready")
        print("  ✓ Markov chain navigation ready")
        print("  ✓ Adaptive volume control ready")
        
        print("\n" + "="*70)
        print("✓ ALL 4 LAYERS + DEAD DROP INITIALIZED SUCCESSFULLY")
        print("="*70)
        
        # Statistics
        self.messages_sent = 0
        self.messages_received = 0
        self.last_message_id = None
    
    def _test_server_connection(self):
        """Test if dead drop server is reachable"""
        try:
            import requests
            response = requests.get(f"{self.dead_drop_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def send_message(self, message: str, receiver_info: str = "dead_drop",
                    use_real_password: bool = True, cover_image: str = None):
        """
        Send a covert message through all 4 layers + dead drop
        
        Args:
            message: Secret message to send
            receiver_info: Info about receiver (for display only)
            use_real_password: True for real, False for duress
            cover_image: Path to cover image (auto-created if None)
        
        Returns:
            message_id for recipient to download
        """
        print(f"\n{'='*70}")
        print(f"📤 SENDING COVERT MESSAGE VIA DEAD DROP")
        print(f"{'='*70}")
        print(f"Message: \"{message}\"")
        print(f"Receiver: {receiver_info}")
        print(f"Password: {'Real (secret)' if use_real_password else 'Duress (decoy)'}")
        print()
        
        # Create cover image if needed
        if cover_image is None:
            print("[Preparation] Creating cover image...")
            cover_image = self.stego.create_cover_image()
            print(f"  ✓ Cover image: {cover_image}")
            print()
        
        # STAGE 1: ENCRYPTION (Layer 1)
        print("[STAGE 1] Encrypting message (Layer 1)...")
        encrypted = self.crypto.encrypt(message, use_real_password)
        print(f"  ✓ Encrypted: {len(encrypted)} bytes")
        print(f"    Original: {len(message)} chars → Encrypted: {len(encrypted)} bytes")
        print()
        
        # STAGE 2: STEGANOGRAPHIC CONCEALMENT (Layer 2)
        print("[STAGE 2] Hiding in image (Layer 2)...")
        stego_path = self.stego.embed(encrypted, cover_image, 'outputs/stego.png')
        print(f"  ✓ Data hidden in: {stego_path}")
        print()
        
        # STAGE 3: DEAD DROP UPLOAD (Layer 3)
        print("[STAGE 3] Uploading to dead drop server (Layer 3)...")
        message_id = self.network.send_covert_packet(stego_path)
        print()
        
        if message_id:
            self.messages_sent += 1
            self.last_message_id = message_id
            
            print(f"{'='*70}")
            print("✅ MESSAGE SENT SUCCESSFULLY VIA DEAD DROP")
            print(f"{'='*70}")
            print(f"Message ID: {message_id}")
            print(f"\n📋 SHARE THIS MESSAGE ID WITH RECEIVER:")
            print(f"   {message_id}")
            print(f"\nReceiver command:")
            print(f"   > receive {message_id}")
            print(f"{'='*70}")
            
            # Layer 4 running in background
            if self.behavioral.is_running:
                print("\n[STAGE 4] Adaptive behavioral engine active (decoy traffic)")
            
            return message_id
        else:
            print("\n❌ SEND FAILED - Check if dead drop server is running")
            return None
    
    def receive_message(self, message_id: str, use_real_password: bool = True):
        """
        Receive and decrypt a covert message from dead drop
        
        Args:
            message_id: ID of message to download from dead drop
            use_real_password: True for real, False for duress
        
        Returns:
            Decrypted message
        """
        print(f"\n{'='*70}")
        print(f"📥 RECEIVING COVERT MESSAGE FROM DEAD DROP")
        print(f"{'='*70}")
        print(f"Message ID: {message_id}")
        print(f"Password: {'Real (secret)' if use_real_password else 'Duress (decoy)'}")
        print()
        
        # STAGE 1: DEAD DROP DOWNLOAD (Layer 3)
        print("[STAGE 1] Downloading from dead drop server (Layer 3)...")
        stego_path = 'outputs/received_stego.png'
        success = self.network.receive_covert_packet(message_id, stego_path)
        print()
        
        if not success:
            print("❌ RECEIVE FAILED - Message not found")
            return None
        
        # STAGE 2: EXTRACT HIDDEN DATA (Layer 2)
        print("[STAGE 2] Extracting hidden data (Layer 2)...")
        try:
            encrypted = self.stego.extract(stego_path)
            print(f"  ✓ Extracted: {len(encrypted)} bytes")
            print()
        except Exception as e:
            print(f"  ✗ Extraction failed: {e}")
            print("❌ RECEIVE FAILED - Cannot extract data")
            return None
        
        # STAGE 3: DECRYPTION (Layer 1)
        print("[STAGE 3] Decrypting message (Layer 1)...")
        try:
            message = self.crypto.decrypt(encrypted, use_real_password)
            print(f"  ✓ Decrypted successfully")
            print()
            
            self.messages_received += 1
            
            print(f"{'='*70}")
            print("✅ MESSAGE RECEIVED SUCCESSFULLY")
            print(f"{'='*70}")
            print(f"\n📨 Decrypted Message:")
            print(f"   \"{message}\"")
            print(f"{'='*70}")
            
            return message
        except Exception as e:
            print(f"  ✗ Decryption failed: {e}")
            print("  (Wrong password or corrupted data)")
            print()
            print("❌ RECEIVE FAILED - Decryption error")
            return None
    
    def start_decoy_traffic(self):
        """Start Layer 4: Adaptive behavioral decoy traffic"""
        print("\n[Layer 4] Starting adaptive behavioral engine...")
        self.behavioral.start()
        print("  ✓ Decoy traffic generation active")
    
    def stop_decoy_traffic(self):
        """Stop Layer 4: Adaptive behavioral decoy traffic"""
        print("\n[Layer 4] Stopping adaptive behavioral engine...")
        self.behavioral.stop()
        print("  ✓ Decoy traffic generation stopped")
    
    def show_statistics(self):
        """Display comprehensive system statistics"""
        network_stats = self.network.get_statistics()
        behavioral_stats = self.behavioral.get_statistics()
        
        print(f"\n{'='*70}")
        print("📊 SYSTEM STATISTICS")
        print(f"{'='*70}")
        
        print(f"\n🔒 Covert Communication:")
        print(f"  Messages sent: {self.messages_sent}")
        print(f"  Messages received: {self.messages_received}")
        if self.last_message_id:
            print(f"  Last message ID: {self.last_message_id}")
        
        print(f"\n🌐 Network (Layer 3):")
        print(f"  Dead drop server: {network_stats['dead_drop_url']}")
        print(f"  Packets sent via dead drop: {network_stats['messages_sent']}")
        
        print(f"\n🤖 Adaptive Behavioral Engine (Layer 4):")
        print(f"  Status: {'🟢 Running' if behavioral_stats['is_running'] else '🔴 Stopped'}")
        print(f"  Total decoys sent: {behavioral_stats['total_decoys_sent']}")
        print(f"  Current domain: {behavioral_stats['current_domain']}")
        print(f"  Activity level: {behavioral_stats['current_activity']:.2f}x")
        print(f"  Current hour: {behavioral_stats['current_hour']}:00")
        
        print(f"\n{'='*70}")


def interactive_mode():
    """Interactive mode for manual message sending"""
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║   SECURE COMMUNICATION SYSTEM FOR COVERT OPERATIONS                 ║
║   Interactive Mode - Dead Drop Architecture                         ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
    """)
    
    # Get dead drop server URL
    print("Dead Drop Server Configuration")
    print("-" * 70)
    default_url = "http://localhost:8080"
    server_url = input(f"Dead drop server URL [{default_url}]: ").strip()
    if not server_url:
        server_url = default_url
    print()
    
    # Initialize system
    try:
        system = CovertCommunicationSystem(dead_drop_url=server_url)
    except ConnectionError:
        print("\n❌ Cannot connect to dead drop server. Exiting.")
        return
    
    # Start adaptive decoy traffic
    system.start_decoy_traffic()
    
    print("\n" + "="*70)
    print("INTERACTIVE COMMANDS")
    print("="*70)
    print("  send                     - Send a new message")
    print("  receive <message_id>     - Receive message by ID")
    print("  send_duress              - Send duress (fake) message")
    print("  receive_duress <msg_id>  - Receive with duress password")
    print("  stats                    - Show statistics")
    print("  help                     - Show this help")
    print("  quit                     - Exit")
    print("="*70)
    
    try:
        while True:
            command = input("\n> ").strip()
            
            if not command:
                continue
            
            if command == "send":
                print("\n--- SEND MESSAGE ---")
                receiver_ip = input("Receiver info (IP/name): ").strip()
                if not receiver_ip:
                    receiver_ip = "unknown"
                
                message = input("Message to send: ").strip()
                if message:
                    system.send_message(message, receiver_info=receiver_ip, 
                                      use_real_password=True)
                else:
                    print("❌ No message entered")
            
            elif command == "send_duress":
                print("\n--- SEND DURESS MESSAGE (FAKE) ---")
                receiver_ip = input("Receiver info (IP/name): ").strip()
                if not receiver_ip:
                    receiver_ip = "unknown"
                
                message = input("Decoy message to send: ").strip()
                if message:
                    system.send_message(message, receiver_info=receiver_ip,
                                      use_real_password=False)
                else:
                    print("❌ No message entered")
            
            elif command.startswith("receive "):
                msg_id = command[8:].strip()
                if msg_id:
                    system.receive_message(msg_id, use_real_password=True)
                else:
                    print("❌ No message ID specified")
                    print("Usage: receive <message_id>")
            
            elif command.startswith("receive_duress "):
                msg_id = command[15:].strip()
                if msg_id:
                    system.receive_message(msg_id, use_real_password=False)
                else:
                    print("❌ No message ID specified")
                    print("Usage: receive_duress <message_id>")
            
            elif command == "stats":
                system.show_statistics()
            
            elif command == "help":
                print("\n" + "="*70)
                print("AVAILABLE COMMANDS")
                print("="*70)
                print("  send                     - Send a real secret message")
                print("  receive <message_id>     - Receive and decrypt message")
                print("  send_duress              - Send fake duress message")
                print("  receive_duress <msg_id>  - Receive duress message")
                print("  stats                    - Show system statistics")
                print("  help                     - Show this help")
                print("  quit                     - Exit program")
                print("="*70)
            
            elif command == "quit":
                print("\nShutting down...")
                break
            
            else:
                print("❌ Unknown command. Type 'help' for available commands.")
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    finally:
        system.stop_decoy_traffic()
        print("✓ System shutdown complete")


def quick_test():
    """Quick test mode to verify system works"""
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                      QUICK SYSTEM TEST                               ║
╚══════════════════════════════════════════════════════════════════════╝
    """)
    
    try:
        system = CovertCommunicationSystem(dead_drop_url='http://localhost:8080')
    except ConnectionError:
        print("\n❌ Cannot connect to dead drop server.")
        print("   Make sure it's running: python dead_drop_server.py --port 8080")
        return
    
    system.start_decoy_traffic()
    
    # Send test message
    print("\n" + "="*70)
    print("TEST: Sending message...")
    print("="*70)
    msg_id = system.send_message("Test message from quick test", 
                                 receiver_info="localhost")
    
    if msg_id:
        # Wait
        print("\n⏱  Waiting 2 seconds...")
        time.sleep(2)
        
        # Receive
        print("\n" + "="*70)
        print("TEST: Receiving message...")
        print("="*70)
        system.receive_message(msg_id)
        
        # Stats
        system.show_statistics()
        
        print("\n✅ System test successful!")
    else:
        print("\n❌ System test failed")
    
    system.stop_decoy_traffic()


def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            quick_test()
        elif sys.argv[1] == "interactive":
            interactive_mode()
        else:
            print("Usage:")
            print("  python main.py                 - Interactive mode (default)")
            print("  python main.py interactive     - Interactive mode")
            print("  python main.py test            - Quick system test")
    else:
        interactive_mode()


if __name__ == "__main__":
    main()
