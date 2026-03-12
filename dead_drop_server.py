#!/usr/bin/env python3
"""
Dead Drop Server - Secure Message Exchange Server
Part of the 4-Layer Covert Communication System
"""

from flask import Flask, request, send_file, jsonify, render_template_string
import os
import hashlib
import time
from datetime import datetime, timedelta
import threading
import secrets
import logging

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = '/tmp/dead_drop_messages'
MESSAGE_EXPIRY_HOURS = 24
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Create upload directory
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Message storage
messages = {}
messages_lock = threading.Lock()

# Statistics
stats = {
    'total_uploads': 0,
    'total_downloads': 0,
    'start_time': datetime.now()
}


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_message_id():
    """Generate cryptographically secure random message ID"""
    return secrets.token_urlsafe(32)


def cleanup_expired_messages():
    """Background thread to delete expired messages"""
    while True:
        time.sleep(300)  # Check every 5 minutes
        
        with messages_lock:
            current_time = datetime.now()
            expired_ids = []
            
            for msg_id, msg_data in messages.items():
                upload_time = msg_data['upload_time']
                age = current_time - upload_time
                
                if age > timedelta(hours=MESSAGE_EXPIRY_HOURS):
                    try:
                        if os.path.exists(msg_data['file_path']):
                            os.remove(msg_data['file_path'])
                        expired_ids.append(msg_id)
                        logging.info(f"Deleted expired message: {msg_id}")
                    except Exception as e:
                        logging.error(f"Failed to delete {msg_id}: {e}")
            
            for msg_id in expired_ids:
                del messages[msg_id]


@app.route('/')
def index():
    """Landing page - mimics photo sharing service"""
    uptime = datetime.now() - stats['start_time']
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>PhotoShare - Free Image Hosting</title>
        <style>
            body {
                font-family: 'Segoe UI', Arial, sans-serif;
                max-width: 900px;
                margin: 50px auto;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            .container {
                background: rgba(255,255,255,0.95);
                padding: 40px;
                border-radius: 15px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.3);
                color: #333;
            }
            h1 {
                color: #667eea;
                margin-bottom: 10px;
            }
            .subtitle {
                color: #666;
                margin-bottom: 30px;
            }
            .stats {
                background: #f8f9fa;
                padding: 20px;
                border-radius: 10px;
                margin: 20px 0;
                border-left: 4px solid #667eea;
            }
            .stat-item {
                padding: 8px 0;
                display: flex;
                justify-content: space-between;
            }
            .stat-label {
                font-weight: 600;
                color: #555;
            }
            .stat-value {
                color: #667eea;
                font-weight: bold;
            }
            .status-online {
                color: #28a745;
                font-weight: bold;
            }
            .api-section {
                background: #fff;
                padding: 20px;
                border-radius: 10px;
                margin: 20px 0;
                border: 1px solid #dee2e6;
            }
            code {
                background: #f4f4f4;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: 'Courier New', monospace;
            }
            .endpoint {
                margin: 10px 0;
                padding: 10px;
                background: #f8f9fa;
                border-left: 3px solid #667eea;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📷 PhotoShare</h1>
            <p class="subtitle">Free, fast, and secure image hosting service</p>
            
            <div class="stats">
                <div class="stat-item">
                    <span class="stat-label">Server Status:</span>
                    <span class="status-online">● Online</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Active Images:</span>
                    <span class="stat-value">""" + str(len(messages)) + """</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Total Uploads:</span>
                    <span class="stat-value">""" + str(stats['total_uploads']) + """</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Total Downloads:</span>
                    <span class="stat-value">""" + str(stats['total_downloads']) + """</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Uptime:</span>
                    <span class="stat-value">""" + str(uptime).split('.')[0] + """</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Auto-Delete:</span>
                    <span class="stat-value">""" + str(MESSAGE_EXPIRY_HOURS) + """ hours</span>
                </div>
            </div>
            
            <div class="api-section">
                <h3>API Endpoints:</h3>
                <div class="endpoint">
                    <strong>POST</strong> <code>/api/upload</code> - Upload image
                </div>
                <div class="endpoint">
                    <strong>GET</strong> <code>/api/download/&lt;message_id&gt;</code> - Download image
                </div>
                <div class="endpoint">
                    <strong>GET</strong> <code>/api/list</code> - List recent uploads
                </div>
                <div class="endpoint">
                    <strong>GET</strong> <code>/health</code> - Health check
                </div>
            </div>
            
            <p style="text-align: center; color: #999; margin-top: 30px;">
                Powered by PhotoShare © 2026
            </p>
        </div>
    </body>
    </html>
    """
    return html


@app.route('/api/upload', methods=['POST'])
def upload_message():
    """Upload endpoint - Accepts steganographic images"""
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Only PNG/JPG allowed'}), 400
    
    try:
        file_data = file.read()
        
        if len(file_data) > MAX_FILE_SIZE:
            return jsonify({'error': f'File too large. Max {MAX_FILE_SIZE/1024/1024}MB'}), 400
        
        message_id = generate_message_id()
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{message_id}.{file_extension}"
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        
        with open(file_path, 'wb') as f:
            f.write(file_data)
        
        with messages_lock:
            messages[message_id] = {
                'file_path': file_path,
                'upload_time': datetime.now(),
                'access_count': 0,
                'original_filename': file.filename,
                'size': len(file_data)
            }
            stats['total_uploads'] += 1
        
        logging.info(f"Upload: {message_id} ({len(file_data)} bytes)")
        
        return jsonify({
            'success': True,
            'message_id': message_id,
            'download_url': f'/api/download/{message_id}',
            'expires_in_hours': MESSAGE_EXPIRY_HOURS
        }), 201
        
    except Exception as e:
        logging.error(f"Upload failed: {e}")
        return jsonify({'error': 'Upload failed'}), 500


@app.route('/api/download/<message_id>', methods=['GET'])
def download_message(message_id):
    """Download endpoint - Retrieve steganographic image by ID"""
    
    with messages_lock:
        if message_id not in messages:
            return jsonify({'error': 'Message not found or expired'}), 404
        
        msg_data = messages[message_id]
        file_path = msg_data['file_path']
        msg_data['access_count'] += 1
        stats['total_downloads'] += 1
        
        logging.info(f"Download: {message_id} (access #{msg_data['access_count']})")
    
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found on server'}), 404
    
    try:
        return send_file(
            file_path,
            mimetype='image/png',
            as_attachment=False,
            download_name=msg_data['original_filename']
        )
    except Exception as e:
        logging.error(f"Download failed: {e}")
        return jsonify({'error': 'Download failed'}), 500


@app.route('/api/list', methods=['GET'])
def list_messages():
    """List endpoint - Show available messages"""
    
    with messages_lock:
        message_list = []
        for msg_id, msg_data in messages.items():
            message_list.append({
                'message_id': msg_id,
                'upload_time': msg_data['upload_time'].isoformat(),
                'age_minutes': int((datetime.now() - msg_data['upload_time']).total_seconds() / 60),
                'size': msg_data['size'],
                'access_count': msg_data['access_count']
            })
        
        message_list.sort(key=lambda x: x['upload_time'], reverse=True)
    
    return jsonify({
        'count': len(message_list),
        'messages': message_list
    })


@app.route('/api/delete/<message_id>', methods=['DELETE'])
def delete_message(message_id):
    """Delete endpoint - Remove message after reading"""
    
    with messages_lock:
        if message_id not in messages:
            return jsonify({'error': 'Message not found'}), 404
        
        msg_data = messages[message_id]
        file_path = msg_data['file_path']
        
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            del messages[message_id]
            logging.info(f"Deleted: {message_id}")
            
            return jsonify({'success': True, 'message': 'Message deleted'})
        except Exception as e:
            logging.error(f"Delete failed: {e}")
            return jsonify({'error': 'Delete failed'}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'active_messages': len(messages),
        'total_uploads': stats['total_uploads'],
        'total_downloads': stats['total_downloads'],
        'uptime_seconds': int((datetime.now() - stats['start_time']).total_seconds())
    })


def run_server(host='0.0.0.0', port=5000, debug=False):
    """Start the dead drop server"""
    
    print("="*70)
    print("🔒 DEAD DROP SERVER STARTING")
    print("="*70)
    print(f"Server URL: http://{host}:{port}")
    print(f"Upload: POST /api/upload")
    print(f"Download: GET /api/download/<message_id>")
    print(f"List: GET /api/list")
    print(f"Storage: {UPLOAD_FOLDER}")
    print(f"Auto-delete: {MESSAGE_EXPIRY_HOURS} hours")
    print("="*70)
    print()
    
    # Start cleanup thread
    cleanup_thread = threading.Thread(target=cleanup_expired_messages, daemon=True)
    cleanup_thread.start()
    
    # Start Flask server
    app.run(host=host, port=port, debug=debug, threaded=True)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Dead Drop Server for Covert Communications')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to listen on')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    run_server(host=args.host, port=args.port, debug=args.debug)
