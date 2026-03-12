# 🌐 Llamaball Web Server

**Beautiful, accessible web interface for Llamaball document chat and RAG system**

## ✨ Features

- **🎨 Beautiful UI**: Modern, responsive design with Bootstrap 5
- **💬 Interactive Chat**: Real-time chat interface with your documents
- **📁 File Upload**: Drag-and-drop file upload with progress tracking
- **📊 Analytics Dashboard**: Comprehensive statistics and system monitoring
- **🔐 HTTPS Support**: Built-in SSL/TLS with self-signed certificates
- **🎛️ Real-time Settings**: Adjust model parameters on-the-fly
- **📱 Mobile Friendly**: Responsive design works on all devices
- **♿ Accessibility**: Screen reader friendly with semantic markup

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Install web server dependencies
./install_web_deps.sh

# Or manually:
pip install flask flask-cors cryptography gunicorn
```

### 2. Start the Server

```bash
# Basic HTTP server (development)
python start_web_server.py

# HTTPS server (recommended)
python start_web_server.py --https

# Production server
python start_web_server.py --host 0.0.0.0 --port 443 --https
```

### 3. Access the Interface

Open your browser and navigate to:
- **HTTP**: http://localhost:8080
- **HTTPS**: https://localhost:8080

## 📋 Server Options

### Basic Configuration

```bash
python start_web_server.py [OPTIONS]

Options:
  --host HOST              Host to bind to (default: 0.0.0.0)
  --port PORT              Port to bind to (default: 8080)
  --debug                  Enable debug mode
  --db-path PATH           SQLite database path (default: .llamaball.db)
  --upload-dir PATH        Upload directory (default: ./uploads)
```

### SSL/HTTPS Configuration

```bash
# Self-signed certificate (automatic)
python start_web_server.py --https

# Custom certificate
python start_web_server.py --ssl-cert cert.pem --ssl-key key.pem

# Production HTTPS on port 443
python start_web_server.py --host 0.0.0.0 --port 443 --https
```

### Model Configuration

```bash
python start_web_server.py \
  --embedding-model nomic-embed-text:latest \
  --chat-model llama3.2:3b
```

## 🌐 Web Interface

### Dashboard (`/`)
- **System Overview**: Database statistics, file counts, model status
- **Quick Actions**: Direct links to chat, upload, and statistics
- **Recent Files**: Recently added documents
- **Available Models**: Ollama models with sizes and details
- **System Status**: Health monitoring for database, Ollama, and web server

### Chat Interface (`/chat`)
- **Interactive Chat**: Real-time conversation with your documents
- **Model Selection**: Choose from available Ollama models
- **Parameter Tuning**: Adjust temperature, top-k, max tokens
- **Session Management**: Persistent chat sessions with history
- **Export/Import**: Save and load conversation history
- **Quick Actions**: Pre-defined questions for common queries

### File Upload (`/upload`)
- **Drag & Drop**: Modern file upload interface
- **Progress Tracking**: Real-time upload and processing status
- **File Validation**: Automatic file type checking
- **Batch Upload**: Multiple file support
- **Auto-Ingestion**: Automatic document processing and indexing

### Statistics (`/stats`)
- **Detailed Analytics**: Comprehensive database insights
- **File Type Breakdown**: Analysis by file extension
- **Usage Patterns**: Document access and query statistics
- **Performance Metrics**: System performance monitoring

## 🔌 API Endpoints

### Chat API
```bash
POST /api/chat
Content-Type: application/json

{
  "message": "What are the main topics in my documents?",
  "session_id": "session_123",
  "model": "llama3.2:1b",
  "top_k": 3,
  "temperature": 0.7,
  "max_tokens": 512
}
```

### Search API
```bash
POST /api/search
Content-Type: application/json

{
  "query": "machine learning algorithms",
  "top_k": 5
}
```

### Upload API
```bash
POST /api/upload
Content-Type: multipart/form-data

files: [file1.pdf, file2.docx, ...]
```

### Health Check
```bash
GET /api/health

Response:
{
  "status": "healthy",
  "database": "connected",
  "ollama": "connected",
  "timestamp": "2025-01-27T10:30:00Z",
  "stats": {
    "documents": 150,
    "embeddings": 150,
    "files": 45
  }
}
```

## 🏭 Production Deployment

### Using Gunicorn (Recommended)

```bash
# Install Gunicorn
pip install gunicorn

# Basic production server
gunicorn -w 4 -b 0.0.0.0:8080 'llamaball.web_server:create_app()'

# With SSL
gunicorn -w 4 -b 0.0.0.0:443 \
  --certfile=cert.pem --keyfile=key.pem \
  'llamaball.web_server:create_app()'

# Advanced configuration
gunicorn -w 4 -b 0.0.0.0:8080 \
  --timeout 300 \
  --max-requests 1000 \
  --max-requests-jitter 100 \
  --preload \
  'llamaball.web_server:create_app()'
```

### Environment Variables

```bash
export LLAMABALL_DB_PATH="/path/to/production.db"
export LLAMABALL_UPLOAD_FOLDER="/path/to/uploads"
export LLAMABALL_MODEL="nomic-embed-text:latest"
export LLAMABALL_CHAT_MODEL="llama3.2:3b"
export FLASK_SECRET_KEY="your-secret-key-here"
```

### Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    client_max_body_size 100M;
    
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
}
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install flask flask-cors cryptography gunicorn

# Copy application
COPY . .

# Create uploads directory
RUN mkdir -p uploads

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/api/health || exit 1

# Start server
CMD ["python", "start_web_server.py", "--host", "0.0.0.0", "--port", "8080"]
```

## 🔧 Configuration

### File Upload Limits

```python
# In web_server.py
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB
```

### Supported File Types

The web interface supports all file types that Llamaball CLI supports:

- **Text**: .txt, .md, .rst, .tex, .org, .adoc, .wiki
- **Code**: .py, .js, .ts, .html, .css, .json, .yaml, .sql
- **Documents**: .pdf, .docx, .doc, .odt, .pages, .rtf
- **Data**: .csv, .tsv, .xlsx, .xls, .jsonl, .parquet
- **Archives**: .zip, .tar, .7z, .rar (with content extraction)
- **And 100+ more file types**

### Security Considerations

1. **HTTPS**: Always use HTTPS in production
2. **File Validation**: Only allow supported file types
3. **Size Limits**: Configure appropriate upload size limits
4. **Access Control**: Consider adding authentication for production
5. **CORS**: Configure CORS policies for your domain

## 🎨 Customization

### Themes and Styling

The web interface uses CSS custom properties for easy theming:

```css
:root {
    --primary-color: #00D4AA;
    --secondary-color: #0066CC;
    --success-color: #00C851;
    --warning-color: #FFB84D;
    --error-color: #FF4444;
}
```

### Adding Custom Pages

1. Create new template in `llamaball/templates/`
2. Add route in `llamaball/web_server.py`
3. Update navigation in `base.html`

## 🐛 Troubleshooting

### Common Issues

**Server won't start:**
```bash
# Check if port is in use
lsof -i :8080

# Try different port
python start_web_server.py --port 8081
```

**SSL certificate errors:**
```bash
# Regenerate self-signed certificate
rm llamaball-cert.pem llamaball-key.pem
python start_web_server.py --https
```

**Ollama connection failed:**
```bash
# Check Ollama status
ollama list

# Start Ollama if needed
ollama serve
```

**File upload fails:**
```bash
# Check upload directory permissions
chmod 755 uploads/

# Check disk space
df -h
```

### Debug Mode

Enable debug mode for detailed error messages:

```bash
python start_web_server.py --debug
```

## 📊 Performance

### Optimization Tips

1. **Use Gunicorn**: Better performance than Flask dev server
2. **Enable Caching**: Add Redis for session/response caching
3. **Database Optimization**: Use WAL mode for SQLite
4. **File Compression**: Enable gzip compression in Nginx
5. **CDN**: Use CDN for static assets in production

### Monitoring

Monitor your Llamaball web server with:

- **Health Endpoint**: `/api/health`
- **System Metrics**: CPU, memory, disk usage
- **Application Logs**: Gunicorn/Flask logs
- **Database Performance**: SQLite query performance

## 🤝 Contributing

To contribute to the web interface:

1. Follow accessibility guidelines (WCAG 2.1)
2. Test with screen readers
3. Ensure mobile responsiveness
4. Add comprehensive error handling
5. Include API documentation

## 📄 License

MIT License - Built with ❤️ for accessibility and local AI.

---

**Need help?** Check the main [Llamaball README](README.md) or open an issue on GitHub. 