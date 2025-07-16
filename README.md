<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" class="logo" width="120"/>

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

The IEEE Document Formatter is a comprehensive offline application designed to convert various document formats (PDF, DOCX, DOC, ZIP) into properly formatted IEEE-style papers. The application features AI-powered title and abstract suggestions, real-time document editing, and automatic PDF generation using LaTeX.

### Key Capabilities

- **Multi-format Support**: PDF, DOCX, DOC, ZIP file parsing
- **AI-Powered Suggestions**: Generate title and abstract alternatives using local LLM
- **Real-time Editing**: Live preview with synchronized editing
- **IEEE Compliance**: Generate IEEE-standard formatted papers
- **Offline Operation**: Complete functionality without internet connection
- **User Management**: Secure authentication and document history


## ✨ Features

### Document Processing

- Parse PDF documents with text and image extraction
- Convert DOCX/DOC files with table and image preservation
- Extract academic content (abstract, sections, references)
- Handle ZIP archives with multiple documents


### AI Integration

- Local LLM integration via Ollama
- Generate multiple title suggestions
- Create abstract alternatives
- Maintain document context and academic tone


### Document Editor

- Real-time synchronized editing
- Image inclusion with caption management
- Table editing and formatting
- Section and subsection management
- Reference management


### Output Generation

- IEEE-compliant LaTeX formatting
- Automatic PDF compilation
- Download options for markdown and PDF
- Template support for different IEEE formats


## 🔧 System Requirements

### Operating System

- Windows 10/11 (64-bit)
- Linux (Ubuntu 20.04+ recommended)
- macOS 10.15+


### Hardware Requirements

- **RAM**: Minimum 8GB, Recommended 16GB
- **Storage**: 10GB free space for full installation
- **CPU**: Multi-core processor (for AI processing)


### Software Dependencies

- Python 3.8+
- MongoDB 4.4+
- LibreOffice 7.0+
- MiKTeX/TeX Live (LaTeX distribution)
- Ollama (for AI features)


## 📦 Installation Guide

### Phase 1: Core System Setup

#### 1. Python Environment

```bash
# Install Python 3.8+
# On Ubuntu/Debian
sudo apt update
sudo apt install python3.8 python3.8-pip python3.8-venv

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


### Phase 2: LaTeX Distribution (MiKTeX)

#### Windows MiKTeX Installation

1. Download MiKTeX from https://miktex.org/download
2. Run installer with admin privileges
3. Install required packages:
```bash
# Core packages installation
miktex-console --admin --install="uniquecounter,syntax2,stringenc,ruhyphen,sfs,refcount,psnfss,pdfescape"
miktex-console --admin --install="kvdefinekeys,intcalc,infwarerr,hycolor,graphics-cfg,gettitlestring,float"
miktex-console --admin --install="ec,dehyph,csfonts,courier,cm,booktabs,bitset,bigintcalc"
miktex-console --admin --install="IEEEtran,amsmath,graphicx,caption,hyperref,enumitem"
```


#### Linux TeX Live Installation

```bash
sudo apt install texlive-full
# Or for minimal installation
sudo apt install texlive-latex-base texlive-latex-extra texlive-publishers
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
pip install -r requirements.txt
```


#### 4. Download Spacy Model

```bash
python -m spacy download en_core_web_sm
```


### Phase 5: Directory Structure Setup

```bash
# Create required directories
mkdir -p uploads temp_data static/images static/temp
```


## ⚙️ Configuration

### 1. MongoDB Configuration

```javascript
// Start MongoDB service
sudo systemctl start mongod

// Connect to MongoDB shell
mongo

// Create database and user
use authdb
db.createUser({
  user: "ieee_user",
  pwd: "secure_password",
  roles: ["readWrite"]
})
```


### 2. Environment Variables

Create `.env` file in project root:

```bash
MONGODB_URI=mongodb://localhost:27017/
SECRET_KEY=your-secret-key-here
OLLAMA_BASE_URL=http://localhost:11434
LATEX_COMPILER=pdflatex
```


### 3. Application Configuration

Edit `config.py`:

```python
class Config:
    SECRET_KEY = 'your-secret-key'
    MONGODB_URI = 'mongodb://localhost:27017/'
    UPLOAD_FOLDER = 'uploads'
    TEMP_FOLDER = 'temp_data'
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max file size
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
2. Create user account or login
3. Upload document for processing

### Document Processing Workflow

#### 1. Upload Document

- Supported formats: PDF, DOCX, DOC, ZIP
- Maximum file size: 50MB
- Automatic parsing and content extraction


#### 2. Title \& Abstract Selection

- Review original title and abstract
- Choose from AI-generated alternatives
- Option to create custom title/abstract
- Real-time preview of selections


#### 3. Document Editing

- **Left Panel**: Structured content editing
- **Right Panel**: Real-time PDF preview
- Edit sections, subsections, and references
- Manage images with captions and sizing
- Table editing capabilities


#### 4. Output Generation

- Generate IEEE-compliant PDF
- Download markdown version
- Save document for future editing


### Document Management

- **Dashboard**: View all uploaded documents
- **Resume Editing**: Continue previous work
- **Delete Documents**: Remove unwanted files
- **Title Display**: Shows selected/original title


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
```


#### 2. LaTeX Compilation Error

```bash
# Install missing packages
miktex-console --admin --install-missing

# Check LaTeX installation
pdflatex --version

# Clear LaTeX cache
rm -rf ~/.texlive/cache
```


#### 3. Ollama Model Issues

```bash
# Check Ollama service
ollama serve

# Verify model availability
ollama list

# Re-download model if needed
ollama pull phi3:mini
```


#### 4. Python Dependencies

```bash
# Update requirements
pip install --upgrade -r requirements.txt

# Reinstall specific packages
pip uninstall package_name
pip install package_name
```


### Performance Optimization

#### 1. MongoDB Indexing

```javascript
// Connect to MongoDB
mongo

// Create indexes for better performance
use authdb
db.users.createIndex({"email": 1})
db.users.createIndex({"uploads.temp_id": 1})
```


#### 2. File Cleanup

```bash
# Clean temporary files
find temp_data -name "*.json" -mtime +7 -delete
find static/images -type d -empty -delete
```


## 📁 File Structure

```
ieee-document-formatter/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── config.py             # Configuration settings
├── README.md             # This documentation
├── .env                  # Environment variables
├── templates/            # HTML templates
│   ├── base_dashboard.html
│   ├── dashboard.html
│   ├── editor.html
│   ├── index.html
│   ├── login.html
│   ├── signup.html
│   └── title_selection.html
├── static/               # Static files
│   ├── css/
│   ├── js/
│   ├── images/          # Uploaded images
│   └── temp.pdf         # Generated PDFs
├── utils/               # Utility modules
│   ├── parsers.py       # Document parsing
│   ├── pdf_parser.py    # PDF parsing logic
│   ├── word_parser.py   # Word document parsing
│   ├── title_suggested.py # AI title generation
│   ├── llm_formatter.py # LLM formatting
│   └── latex_formatter.py # LaTeX generation
├── uploads/             # Uploaded files
├── temp_data/           # Temporary processing data
└── logs/               # Application logs
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
- **Parameters**: file, template
- **Returns**: Redirect to title selection


#### GET /title_selection

Display title and abstract selection interface

- **Authentication**: Required
- **Returns**: HTML template with suggestions


#### POST /save_title_selection

Save selected title and abstract

```json
{
  "title": "Selected Title",
  "abstract": "Selected Abstract"
}
```


#### GET /editor

Document editing interface

- **Authentication**: Required
- **Returns**: HTML editor with parsed content


#### POST /generate_pdf

Generate PDF from document data

```json
{
  "title": "Document Title",
  "abstract": "Document Abstract",
  "sections": [...],
  "references": [...]
}
```


### Management Endpoints

#### GET /dashboard

User dashboard with document list

- **Authentication**: Required
- **Returns**: HTML dashboard


#### GET /resume/<temp_id>

Resume editing existing document

- **Authentication**: Required
- **Parameters**: temp_id
- **Returns**: Redirect to editor


#### POST /delete_upload/<temp_id>

Delete uploaded document

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
```


### Database Development

```bash
# MongoDB development setup
mongosh
use authdb_dev
db.createCollection("users")
db.createCollection("documents")
```


### Testing

```bash
# Run unit tests
python -m pytest tests/

# Run integration tests
python -m pytest tests/integration/
```


## 🔒 Security Considerations

### Authentication

- BCrypt password hashing
- Session-based authentication
- CSRF protection enabled
- Secure session cookies


### File Handling

- Secure filename generation
- File type validation
- Size limitations
- Temporary file cleanup


### Database Security

- Input sanitization
- SQL injection prevention
- User data isolation
- Regular backup procedures


## 📈 Performance Monitoring

### Logs Location

- Application logs: `logs/app.log`
- MongoDB logs: `/var/log/mongodb/mongod.log`
- LaTeX logs: Temporary compilation directory


### Monitoring Commands

```bash
# Check application status
ps aux | grep python

# Monitor MongoDB
mongo --eval "db.stats()"

# Check disk usage
df -h
du -sh temp_data/ static/images/
```


## 🆘 Support and Maintenance

### Regular Maintenance

1. **Weekly**: Clean temporary files
2. **Monthly**: Update dependencies
3. **Quarterly**: Database optimization
4. **Annually**: Security audit

### Backup Procedures

```bash
# MongoDB backup
mongodump --db authdb --out /backup/mongodb/

# Application backup
tar -czf ieee_app_backup.tar.gz ieee-document-formatter/
```


### Update Procedure

```bash
# Update application
git pull origin main
pip install -r requirements.txt

# Update models
ollama pull phi3:mini

# Restart services
sudo systemctl restart mongod
```

**Version**: 1.0.0
**Last Updated**: 16 July 2025 2025
**Support**: Contact system administrator for technical issues

