#!/usr/bin/env python3
"""
Llamaball Web Server Startup Script
File Purpose: Easy startup script for Llamaball web interface
Primary Functions: Server configuration, SSL setup, production deployment
Inputs: Command line arguments
Outputs: Running web server
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Add llamaball to path
sys.path.insert(0, str(Path(__file__).parent))

from llamaball.web_server import run_server

def setup_ssl_context(cert_file, key_file):
    """Setup SSL context for HTTPS"""
    try:
        import ssl
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(cert_file, key_file)
        return context
    except Exception as e:
        print(f"Error setting up SSL: {e}")
        return None

def generate_self_signed_cert(cert_file, key_file, host='localhost'):
    """Generate self-signed certificate for development"""
    try:
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import rsa
        import datetime
        
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        
        # Create certificate
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Local"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "Local"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Llamaball"),
            x509.NameAttribute(NameOID.COMMON_NAME, host),
        ])
        
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.utcnow()
        ).not_valid_after(
            datetime.datetime.utcnow() + datetime.timedelta(days=365)
        ).add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName(host),
                x509.DNSName("localhost"),
                x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
            ]),
            critical=False,
        ).sign(private_key, hashes.SHA256())
        
        # Write certificate
        with open(cert_file, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        
        # Write private key
        with open(key_file, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        print(f"✅ Generated self-signed certificate: {cert_file}")
        return True
        
    except ImportError:
        print("❌ cryptography package not available. Install with: pip install cryptography")
        return False
    except Exception as e:
        print(f"❌ Error generating certificate: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description='Llamaball Web Server',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python start_web_server.py                          # Basic HTTP server
  python start_web_server.py --https                  # HTTPS with self-signed cert
  python start_web_server.py --ssl-cert cert.pem --ssl-key key.pem  # Custom SSL
  python start_web_server.py --host 0.0.0.0 --port 443 --https     # Production HTTPS
  python start_web_server.py --debug                  # Development mode
        """
    )
    
    # Server configuration
    parser.add_argument('--host', default='0.0.0.0', 
                       help='Host to bind to (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=8080,
                       help='Port to bind to (default: 8080)')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug mode')
    
    # SSL configuration
    parser.add_argument('--https', action='store_true',
                       help='Enable HTTPS with self-signed certificate')
    parser.add_argument('--ssl-cert', 
                       help='SSL certificate file')
    parser.add_argument('--ssl-key',
                       help='SSL private key file')
    
    # Database configuration
    parser.add_argument('--db-path', default='.llamaball.db',
                       help='SQLite database path (default: .llamaball.db)')
    parser.add_argument('--upload-dir', default='./uploads',
                       help='Upload directory (default: ./uploads)')
    
    # Model configuration
    parser.add_argument('--embedding-model', default='nomic-embed-text:latest',
                       help='Embedding model (default: nomic-embed-text:latest)')
    parser.add_argument('--chat-model', default='llama3.2:1b',
                       help='Chat model (default: llama3.2:1b)')
    
    args = parser.parse_args()
    
    # Set environment variables
    os.environ['LLAMABALL_DB_PATH'] = args.db_path
    os.environ['LLAMABALL_UPLOAD_FOLDER'] = args.upload_dir
    os.environ['LLAMABALL_MODEL'] = args.embedding_model
    os.environ['LLAMABALL_CHAT_MODEL'] = args.chat_model
    
    # Setup logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # SSL setup
    ssl_context = None
    if args.https or (args.ssl_cert and args.ssl_key):
        if args.ssl_cert and args.ssl_key:
            # Use provided certificates
            if not os.path.exists(args.ssl_cert) or not os.path.exists(args.ssl_key):
                print(f"❌ SSL certificate or key file not found")
                sys.exit(1)
            ssl_context = setup_ssl_context(args.ssl_cert, args.ssl_key)
        else:
            # Generate self-signed certificate
            cert_file = 'llamaball-cert.pem'
            key_file = 'llamaball-key.pem'
            
            if not os.path.exists(cert_file) or not os.path.exists(key_file):
                print("🔐 Generating self-signed certificate...")
                if not generate_self_signed_cert(cert_file, key_file, args.host):
                    print("❌ Failed to generate certificate")
                    sys.exit(1)
            
            ssl_context = setup_ssl_context(cert_file, key_file)
        
        if ssl_context is None:
            print("❌ Failed to setup SSL context")
            sys.exit(1)
    
    # Print startup information
    protocol = 'https' if ssl_context else 'http'
    print(f"""
🦙 Llamaball Web Server Starting...

📊 Configuration:
   • URL: {protocol}://{args.host}:{args.port}
   • Database: {args.db_path}
   • Upload Dir: {args.upload_dir}
   • Embedding Model: {args.embedding_model}
   • Chat Model: {args.chat_model}
   • Debug Mode: {args.debug}
   • SSL Enabled: {ssl_context is not None}

🚀 Access your Llamaball instance at:
   {protocol}://{args.host}:{args.port}

💡 API Endpoints:
   • Health Check: {protocol}://{args.host}:{args.port}/api/health
   • Chat API: {protocol}://{args.host}:{args.port}/api/chat
   • Upload API: {protocol}://{args.host}:{args.port}/api/upload

Press Ctrl+C to stop the server
""")
    
    try:
        # Start the server
        run_server(
            host=args.host,
            port=args.port,
            debug=args.debug,
            ssl_context=ssl_context
        )
    except KeyboardInterrupt:
        print("\n👋 Llamaball Web Server stopped")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 