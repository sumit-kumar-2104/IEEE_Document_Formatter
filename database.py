import sqlite3
import bcrypt
from datetime import datetime
import json

DATABASE = 'authdb.db'

def init_db():
    """Initialize the SQLite database with required tables"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password BLOB NOT NULL,
            phone TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create uploads table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS uploads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT NOT NULL,
            file_name TEXT NOT NULL,
            temp_id TEXT UNIQUE NOT NULL,
            title TEXT,
            parsed_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_email) REFERENCES users (email)
        )
    ''')
    
    conn.commit()
    conn.close()

def get_db_connection():
    """Get database connection with row factory"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def create_user(name, email, password, phone):
    """Create a new user"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if user already exists
        cursor.execute('SELECT email FROM users WHERE email = ?', (email,))
        if cursor.fetchone():
            conn.close()
            return False, "User already exists"
        
        # Hash password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Insert user
        cursor.execute('''
            INSERT INTO users (name, email, password, phone)
            VALUES (?, ?, ?, ?)
        ''', (name, email, hashed_password, phone))
        
        conn.commit()
        conn.close()
        return True, "Signup successful"
    except Exception as e:
        return False, str(e)

def authenticate_user(email, password):
    """Authenticate user login"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        conn.close()
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
            return True, dict(user)
        else:
            return False, None
    except Exception as e:
        return False, None

def get_user_by_email(email):
    """Get user by email"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        conn.close()
        return dict(user) if user else None
    except Exception as e:
        return None

def add_upload(user_email, file_name, temp_id, title=None):
    """Add upload record"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO uploads (user_email, file_name, temp_id, title)
            VALUES (?, ?, ?, ?)
        ''', (user_email, file_name, temp_id, title))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error adding upload: {e}")
        return False

def get_user_uploads(user_email):
    """Get all uploads for a user"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM uploads 
            WHERE user_email = ? 
            ORDER BY parsed_on DESC
        ''', (user_email,))
        
        uploads = cursor.fetchall()
        conn.close()
        
        return [dict(upload) for upload in uploads]
    except Exception as e:
        print(f"Error getting uploads: {e}")
        return []

def update_upload_title(user_email, temp_id, title):
    """Update upload title"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE uploads 
            SET title = ? 
            WHERE user_email = ? AND temp_id = ?
        ''', (title, user_email, temp_id))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error updating upload title: {e}")
        return False

def delete_upload(user_email, temp_id):
    """Delete upload record"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM uploads 
            WHERE user_email = ? AND temp_id = ?
        ''', (user_email, temp_id))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error deleting upload: {e}")
        return False
