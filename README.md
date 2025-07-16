# IEEE Document Formatter - Complete Documentation

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [System Requirements](#system-requirements)
- [Installation Guide](#installation-guide)
- [Configuration](#configuration)
- [Usage Guide](#usage-guide)
- [Troubleshooting](#troubleshooting)
- [File Structure](#file-structure)
- [API Documentation](#api-documentation)


## 🎯 Overview

The IEEE Document Formatter is a comprehensive offline application designed to convert various document formats (PDF, DOCX, DOC, ZIP) into properly formatted IEEE-style papers. The application features AI-powered title and abstract suggestions, real-time document editing with image upload support, and automatic PDF generation using LaTeX.

### Key Capabilities

- **Multi-format Support**: PDF, DOCX, DOC, ZIP file parsing
- **AI-Powered Suggestions**: Generate title and abstract alternatives using local LLM
- **Real-time Editing**: Live preview with synchronized editing and base64 image support
- **IEEE Compliance**: Generate IEEE-standard formatted papers
- **Offline Operation**: Complete functionality without internet connection
- **User Management**: Secure authentication and document history
- **Advanced Image Handling**: Support for both file-based and uploaded (base64) images


## ✨ Features

### Document Processing

- Parse PDF documents with text and image extraction
- Convert DOCX/DOC files with table and image preservation
- Extract academic content (abstract, sections, references)
- Handle ZIP archives with multiple documents
- Process inline images and tables during document conversion


### AI Integration

- Local LLM integration via Ollama (phi3:mini model)
- Generate multiple title suggestions based on document content
- Create abstract alternatives maintaining academic tone
- Maintain document context and subject matter expertise


### Document Editor

- Real-time synchronized editing with live PDF preview
- **Enhanced Image Support**: Upload images directly in editor with base64 encoding
- Image caption management and size control (small/medium/large)
- Automatic image format conversion (JPEG → PNG for LaTeX compatibility)
- Dynamic table editing and formatting
- Section and subsection management with drag-and-drop
- Reference management with automatic formatting


### Output Generation

- IEEE-compliant LaTeX formatting with proper image handling
- Automatic PDF compilation with embedded images
- Download options for markdown and PDF formats
- Template support for different IEEE formats
- Base64 image conversion to LaTeX-compatible formats


## 🔧 System Requirements

### Operating System

- Windows 10/11 (64-bit)
- Linux (Ubuntu 20.04+ recommended)
- macOS 10.15+


### Hardware Requirements

- **RAM**: Minimum 8GB, Recommended 16GB (for AI processing and image handling)
- **Storage**: 15GB free space for full installation (increased for LaTeX packages)
- **CPU**: Multi-core processor (for AI processing and image conversion)


### Software Dependencies

- Python 3.8+
- MongoDB 4.4+
- LibreOffice 7.0+
- **MiKTeX 2.9+ (Windows) / TeX Live 2023+ (Linux/macOS)**
- Ollama (for AI features)
- PIL/Pillow (for image processing)


## 📦 Installation Guide

### Phase 1: Core System Setup

#### 1. Python Environment

```bash
# Install Python 3.8+
# On Ubuntu/Debian
sudo apt update
sudo apt install python3.8 python3.8-pip python3.8-venv python3.8-dev

# On Windows - Download from python.org
# On macOS - Use Homebrew
brew install python@3.8
```


#### 2. MongoDB Installation

```bash
# Ubuntu/Debian
wget -qO - https://www.mongodb.org/static/pgp/server-4.4.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/4.4 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.4.list
sudo apt update
sudo apt install -y mongodb-org

# Start MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod

# Windows - Download MongoDB Community Server from mongodb.com
# macOS
brew tap mongodb/brew
brew install mongodb-community@4.4
```


#### 3. LibreOffice Installation

```bash
# Ubuntu/Debian
sudo apt install libreoffice

# Windows - Download from libreoffice.org
# macOS
brew install --cask libreoffice
```


### Phase 2: Enhanced LaTeX Distribution Setup

#### Windows MiKTeX Installation (Complete Package List)

1. Download MiKTeX from https://miktex.org/download
2. Run installer with admin privileges
3. Install comprehensive package set:
```bash
# Core LaTeX packages
miktex-console --admin --install="latex,pdflatex,xelatex,lualatex"

# IEEE and formatting packages
miktex-console --admin --install="IEEEtran,ieeetran,caption,float,graphicx,hyperref,booktabs,adjustbox,collectbox"

# Font packages
miktex-console --admin --install="amsfonts,amsmath,cm,courier,helvetic,times,palatino,avantgar,bookman,ncntrsbk,zapfchan,zapfding,symbol"

# Image and graphics support
miktex-console --admin --install="graphics,graphics-cfg,graphics-def,epstopdf-pkg,xcolor,pgf,pgfplots"

# Advanced formatting
miktex-console --admin --install="tcolorbox,standalone,varwidth,trimspaces,ragged2e,ifoddpage,syntax2"

# Language and hyphenation
miktex-console --admin --install="babel,babel-english,hyph-utf8,dehyph,ukrhyph,ruhyphen,elhyphen"

# Bibliography and references
miktex-console --admin --install="biber,biblatex,bibtex,url,hyperref"

# Math and symbols
miktex-console --admin --install="rsfs,psnfss,textcomp,latexsym"

# Document classes and tools
miktex-console --admin --install="article,book,report,memoir,koma-script"

# Utility packages
miktex-console --admin --install="etoolbox,xkeyval,kvsetkeys,kvdefinekeys,kvoptions,iftex,infwarerr,refcount,rerunfilecheck,uniquecounter"

# Color and positioning
miktex-console --admin --install="xcolor,atbegshi,atveryend,hycolor,bigintcalc,bitset,intcalc,pdfescape,pdftexcmds"

# Advanced text processing
miktex-console --admin --install="stringenc,gettitlestring,blindtext,lipsum,listings,fancyvrb"

# Font configuration
miktex-console --admin --install="fontspec,fontconfig,luaotfload,unicode-data,glyphlist"

# LaTeX3 support
miktex-console --admin --install="l3kernel,l3packages,l3backend,xparse,environ"

# Additional utilities
miktex-console --admin --install="oberdiek,latex-tools,latex-firstaid,tex-ini-files,modes,mptopdf"

# Specialized packages for IEEE formatting
miktex-console --admin --install="threeparttable,multirow,array,longtable,supertabular,xtab"
```


#### Linux TeX Live Installation (Complete)

```bash
# Full installation (recommended)
sudo apt install texlive-full

# Or selective installation
sudo apt install texlive-latex-base texlive-latex-extra texlive-publishers texlive-science texlive-fonts-recommended texlive-fonts-extra texlive-lang-english texlive-lang-european texlive-pictures texlive-plain-generic

# Additional packages for IEEE formatting
sudo apt install texlive-bibtex-extra biber latexmk
```


#### macOS TeX Live Installation

```bash
# Install MacTeX (includes TeX Live)
brew install --cask mactex

# Or use BasicTeX for minimal installation
brew install --cask basictex
sudo tlmgr update --self
sudo tlmgr install collection-latexextra collection-fontsrecommended collection-fontsextra
```


### Phase 3: AI Framework Setup

#### Ollama Installation

```bash
# Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Windows - Download from ollama.ai
# macOS
brew install ollama
```


#### Model Download (Offline Setup)

```bash
# Download phi3:mini model for offline use
ollama pull phi3:mini

# Verify installation
ollama list

# Start Ollama service
ollama serve
```


### Phase 4: Application Setup

#### 1. Clone Repository

```bash
git clone https://github.com/yourusername/ieee-document-formatter.git
cd ieee-document-formatter
```


#### 2. Python Environment

```bash
# Create virtual environment
python -m venv ieee_env

# Activate environment
# Linux/macOS
source ieee_env/bin/activate
# Windows
ieee_env\Scripts\activate
```


#### 3. Install Python Dependencies

```bash
# Upgrade pip first
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# Install additional image processing dependencies
pip install Pillow>=8.0.0
pip install python-magic-bin  # Windows only
```


#### 4. Download Spacy Model

```bash
python -m spacy download en_core_web_sm
```


### Phase 5: Directory Structure Setup

```bash
# Create required directories
mkdir -p uploads temp_data static/images static/temp logs

# Set permissions (Linux/macOS)
chmod 755 uploads temp_data static/images static/temp
```


## ⚙️ Configuration

### 1. MongoDB Configuration

```javascript
// Start MongoDB service
sudo systemctl start mongod

// Connect to MongoDB shell
mongosh

// Create database and user
use authdb
db.createUser({
  user: "ieee_user",
  pwd: "secure_password",
  roles: ["readWrite"]
})

// Create indexes for better performance
db.users.createIndex({"email": 1})
db.users.createIndex({"uploads.temp_id": 1})
```


### 2. Environment Variables

Create `.env` file in project root:

```bash
MONGODB_URI=mongodb://localhost:27017/
SECRET_KEY=your-secret-key-here-93c1745e3f2342c9bfa814bcdf2fd819
OLLAMA_BASE_URL=http://localhost:11434
LATEX_COMPILER=pdflatex
MAX_FILE_SIZE=52428800
IMAGE_UPLOAD_FOLDER=static/images
TEMP_DATA_FOLDER=temp_data
```


### 3. Application Configuration

Edit `config.py`:

```python
class Config:
    SECRET_KEY = 'dev-key-93c1745e3f2342c9bfa814bcdf2fd819'
    MONGODB_URI = 'mongodb://localhost:27017/'
    UPLOAD_FOLDER = 'uploads'
    TEMP_FOLDER = 'temp_data'
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max file size
    IMAGE_FORMATS = ['PNG', 'JPEG', 'JPG', 'GIF', 'BMP']
    LATEX_TIMEOUT = 300  # 5 minutes for LaTeX compilation
```


## 🚀 Usage Guide

### Starting the Application

```bash
# Activate virtual environment
source ieee_env/bin/activate  # Linux/macOS
# or
ieee_env\Scripts\activate     # Windows

# Start MongoDB
sudo systemctl start mongod

# Start Ollama service
ollama serve &

# Run the application
python app.py
```


### Accessing the Application

1. Open browser and navigate to `http://localhost:5000`
2. Create user account or login with existing credentials
3. Upload document for processing

### Enhanced Document Processing Workflow

#### 1. Upload Document

- **Supported formats**: PDF, DOCX, DOC, ZIP
- **Maximum file size**: 50MB
- **Automatic parsing**: Text, images, tables extraction
- **Image processing**: Automatic conversion to PNG format


#### 2. Title \& Abstract Selection

- Review original title and abstract from document
- Choose from AI-generated alternatives (powered by phi3:mini)
- Option to create custom title/abstract
- Real-time preview of selections


#### 3. Advanced Document Editing

- **Left Panel**: Structured content editing with sections management
- **Right Panel**: Real-time LaTeX PDF preview
- **Enhanced Image Support**:
    - Upload images directly via file selector
    - Automatic base64 encoding and conversion
    - Caption editing and size control (small/medium/large)
    - Format conversion (JPEG → PNG for LaTeX compatibility)
- **Table Management**: Edit cells, add/remove rows and columns
- **Section Management**: Add/delete/reorder sections and subsections
- **Reference Management**: Edit and format citations


#### 4. Image Upload Process

1. Click "📷" button on any section
2. Select image file from computer
3. Add caption and choose size
4. Image is automatically:
    - Converted to base64 format
    - Processed for LaTeX compatibility
    - Embedded in PDF output

#### 5. Output Generation

- **IEEE-compliant PDF**: Automatic LaTeX compilation with embedded images
- **Download options**: Markdown format and PDF
- **Save functionality**: Continue editing later
- **Template support**: IEEE conference/journal formatting


### Document Management

- **Dashboard**: View all uploaded documents with titles
- **Resume Editing**: Continue previous work from any point
- **Delete Documents**: Remove unwanted files and cleanup
- **Title Display**: Shows selected or original document title


## 🔍 Troubleshooting

### Common Issues

#### 1. MongoDB Connection Error

```bash
# Check MongoDB status
sudo systemctl status mongod

# Restart MongoDB
sudo systemctl restart mongod

# Check logs
sudo journalctl -u mongod

# Test connection
mongosh --eval "db.runCommand('ping')"
```


#### 2. LaTeX Compilation Errors

```bash
# Check LaTeX installation
pdflatex --version

# Install missing packages (MiKTeX)
miktex-console --admin --install-missing

# Update package database
miktex-console --admin --update-db

# Clear LaTeX cache
rm -rf ~/.texlive/cache

# Test LaTeX compilation
echo '\documentclass{article}\begin{document}Hello World\end{document}' | pdflatex
```


#### 3. Image Processing Issues

```bash
# Check Pillow installation
python -c "from PIL import Image; print('Pillow OK')"

# Reinstall Pillow if needed
pip uninstall Pillow
pip install Pillow>=8.0.0

# Test image processing
python -c "from PIL import Image; img = Image.new('RGB', (100, 100), 'red'); img.save('test.png')"
```


#### 4. Base64 Image Rendering Problems

Common symptoms:

- Images show in left panel but not in PDF
- "Base64 image processing failed" errors
- PDF generation successful but images missing

Solutions:

```bash
# Check image processing function
python -c "import base64; print('Base64 module OK')"

# Clear temp directories
rm -rf temp_data/*
rm -rf static/images/*

# Restart application
python app.py
```


#### 5. Ollama Model Issues

```bash
# Check Ollama service
ollama serve

# List available models
ollama list

# Re-download model if corrupted
ollama rm phi3:mini
ollama pull phi3:mini

# Test model
ollama run phi3:mini "Generate a title for a research paper about machine learning"
```


### Performance Optimization

#### 1. Database Optimization

```javascript
// Connect to MongoDB
mongosh

// Create compound indexes
use authdb
db.users.createIndex({"email": 1, "uploads.temp_id": 1})
db.users.createIndex({"uploads.parsed_on": -1})

// Check index usage
db.users.find({"email": "user@example.com"}).explain("executionStats")
```


#### 2. File System Cleanup

```bash
# Clean temporary files older than 7 days
find temp_data -name "*.json" -mtime +7 -delete
find static/images -type d -empty -delete

# Clean LaTeX temporary files
find . -name "*.aux" -o -name "*.log" -o -name "*.out" -delete

# Monitor disk usage
du -sh temp_data/ static/images/ uploads/
```


#### 3. Memory Management

```python
# Add to app.py for memory monitoring
import psutil
import gc

def cleanup_memory():
    gc.collect()
    return psutil.Process().memory_info().rss / 1024 / 1024  # MB
```


## 📁 File Structure

```
ieee-document-formatter/
├── app.py                 # Main Flask application with image upload support
├── requirements.txt       # Python dependencies (updated)
├── config.py             # Configuration settings
├── README.md             # This documentation
├── .env                  # Environment variables
├── templates/            # HTML templates
│   ├── base_dashboard.html
│   ├── dashboard.html
│   ├── editor.html       # Enhanced with image upload modal
│   ├── index.html
│   ├── login.html
│   ├── signup.html
│   └── title_selection.html
├── static/               # Static files
│   ├── css/
│   ├── js/
│   ├── images/          # Uploaded images (organized by temp_id)
│   │   ├── {temp_id}/   # Individual document image folders
│   │   └── temp.pdf     # Generated PDFs
│   └── temp.pdf         # Current PDF output
├── utils/               # Utility modules
│   ├── parsers.py       # Document parsing
│   ├── pdf_parser.py    # PDF parsing logic
│   ├── word_parser.py   # Word document parsing with table support
│   ├── title_suggested.py # AI title generation
│   ├── llm_formatter.py # LLM formatting
│   └── latex_formatter.py # LaTeX generation with base64 image support
├── uploads/             # Uploaded files
├── temp_data/           # Temporary processing data (JSON files)
├── logs/               # Application logs
└── docs/               # Additional documentation
```


## 🔧 API Documentation

### Authentication Endpoints

#### POST /signup

Register new user account

```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "securepassword",
  "phone": "1234567890"
}
```


#### POST /login

User authentication

```json
{
  "email": "john@example.com",
  "password": "securepassword"
}
```


### Document Processing Endpoints

#### POST /upload

Upload document for processing

- **Content-Type**: multipart/form-data
- **Parameters**: file
- **Returns**: Redirect to title selection
- **Image Processing**: Automatic extraction and PNG conversion


#### GET /title_selection

Display title and abstract selection interface

- **Authentication**: Required
- **Returns**: HTML template with AI-generated suggestions


#### POST /save_title_selection

Save selected title and abstract

```json
{
  "title": "Selected Title",
  "abstract": "Selected Abstract"
}
```


#### GET /editor

Enhanced document editing interface

- **Authentication**: Required
- **Returns**: HTML editor with image upload capabilities


#### POST /generate_pdf

Generate PDF with embedded images

```json
{
  "title": "Document Title",
  "abstract": "Document Abstract",
  "sections": [
    {
      "heading": "Section Title",
      "content": "Section content",
      "images": [
        {
          "path": "data:image/jpeg;base64,/9j/4AAQ...",
          "caption": "Image caption",
          "size": "medium"
        }
      ]
    }
  ],
  "references": [...]
}
```


#### POST /save_document

Save document with images

```json
{
  "title": "Document Title",
  "sections": [...],
  "images": [...]
}
```


### Management Endpoints

#### GET /dashboard

User dashboard with document list

- **Authentication**: Required
- **Returns**: HTML dashboard with document titles


#### GET /resume/<temp_id>

Resume editing existing document

- **Authentication**: Required
- **Parameters**: temp_id
- **Returns**: Redirect to editor with loaded data


#### DELETE /delete_upload/<temp_id>

Delete uploaded document and associated images

- **Authentication**: Required
- **Parameters**: temp_id
- **Returns**: Redirect to dashboard


## 🛠️ Development Setup

### Development Environment

```bash
# Enable debug mode
export FLASK_ENV=development
export FLASK_DEBUG=1

# Run with auto-reload
python app.py

# Enable detailed logging
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```


### Testing Image Processing

```bash
# Test base64 encoding
python -c "
import base64
with open('test.jpg', 'rb') as f:
    data = base64.b64encode(f.read()).decode()
    print(f'data:image/jpeg;base64,{data[:50]}...')
"

# Test LaTeX compilation
cd temp_directory
pdflatex test.tex
```


### Database Development

```bash
# MongoDB development setup
mongosh
use authdb_dev
db.createCollection("users")
db.createCollection("documents")

# Sample data insertion
db.users.insertOne({
  "name": "Test User",
  "email": "test@example.com",
  "uploads": []
})
```


## 🔒 Security Considerations

### Authentication \& Authorization

- BCrypt password hashing (12 rounds)
- Session-based authentication with secure cookies
- CSRF protection enabled
- User isolation for uploads and documents


### File Handling Security

- Secure filename generation using UUID
- File type validation and sanitization
- Size limitations (50MB max)
- Temporary file cleanup with automatic deletion
- Base64 image validation and processing


### Image Security

- File format validation (PNG, JPEG, JPG, GIF, BMP)
- Base64 string validation and sanitization
- Image size limits and compression
- Malicious file detection and prevention


### Database Security

- Input sanitization and validation
- NoSQL injection prevention
- User data isolation with proper indexing
- Regular backup procedures


## 📈 Performance Monitoring

### Logs Location

- Application logs: `logs/app.log`
- MongoDB logs: `/var/log/mongodb/mongod.log`
- LaTeX compilation logs: Temporary directories
- Image processing logs: Included in application logs


### Monitoring Commands

```bash
# Check application status
ps aux | grep python
netstat -tlnp | grep 5000

# Monitor MongoDB
mongosh --eval "db.stats()"
mongosh --eval "db.users.stats()"

# Check disk usage
df -h
du -sh temp_data/ static/images/ uploads/

# Memory usage
free -h
top -p $(pgrep python)
```


### Performance Metrics

- Document processing time: ~30-60 seconds
- Image processing: ~5-10MB/second
- LaTeX compilation: ~10-30 seconds
- Database queries: <100ms average


## 🆘 Support and Maintenance

### Regular Maintenance Tasks

1. **Daily**: Check application logs for errors
2. **Weekly**: Clean temporary files and old uploads
3. **Monthly**: Update dependencies and security patches
4. **Quarterly**: Database optimization and reindexing
5. **Annually**: Security audit and system review

### Backup Procedures

```bash
# MongoDB backup
mongodump --db authdb --out /backup/mongodb/$(date +%Y-%m-%d)

# Application backup
tar -czf ieee_app_backup_$(date +%Y-%m-%d).tar.gz ieee-document-formatter/

# User uploads backup
rsync -av uploads/ /backup/uploads/
rsync -av static/images/ /backup/images/
```


### Update Procedure

```bash
# Pull latest changes
git pull origin main

# Update Python dependencies
pip install --upgrade -r requirements.txt

# Update LaTeX packages
miktex-console --admin --update-packages

# Update AI models
ollama pull phi3:mini

# Restart services
sudo systemctl restart mongod
sudo systemctl restart ollama
```


### System Health Checks

```bash
# Check all services
systemctl status mongod
pgrep -f "ollama serve"
pgrep -f "python app.py"

# Test LaTeX compilation
echo '\documentclass{IEEEtran}\begin{document}Test\end{document}' | pdflatex

# Test image processing
python -c "from PIL import Image; print('Image processing OK')"

# Test MongoDB connection
mongosh --eval "db.runCommand('ping')"
```

**Version**: 2.0.0
**Last Updated**: July 16, 2025
**Support**: Contact system administrator for technical issues
**License**: MIT License

### Key Improvements in Version 2.0.0:

- Enhanced image upload and processing capabilities
- Base64 image support for direct editor uploads
- Improved LaTeX package management
- Better error handling and debugging
- Enhanced security measures
- Comprehensive monitoring and maintenance procedures

