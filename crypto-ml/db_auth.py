import psycopg2
from psycopg2 import pool
import os
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

# Create connection pool
try:
    connection_pool = psycopg2.pool.SimpleConnectionPool(1, 20, DATABASE_URL)
    logger.info("✅ Database connection pool created successfully")
except Exception as e:
    logger.error(f"❌ Error creating connection pool: {e}")
    connection_pool = None

def get_db_connection():
    """Get a connection from the pool"""
    if connection_pool is None:
        raise Exception("Database connection pool not initialized")
    return connection_pool.getconn()

def return_db_connection(conn):
    """Return connection to the pool"""
    if connection_pool:
        connection_pool.putconn(conn)

def init_db():
    """Initialize database with users table"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create users table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                public_key VARCHAR(255) UNIQUE NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Create index on email for faster lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
        """)
        
        # Create index on public_key for faster lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_users_public_key ON users(public_key);
        """)
        
        conn.commit()
        logger.info("✅ Database tables initialized successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Error initializing database: {e}")
        return False
    finally:
        if conn:
            return_db_connection(conn)

def user_exists(email: str) -> bool:
    """Check if user exists by email"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        result = cursor.fetchone()
        return result is not None
    except Exception as e:
        logger.error(f"❌ Error checking user existence: {e}")
        return False
    finally:
        if conn:
            return_db_connection(conn)

def create_user(public_key: str, email: str, password_hash: str) -> dict:
    """Create a new user"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO users (public_key, email, password_hash) VALUES (%s, %s, %s) RETURNING id, public_key, email, created_at",
            (public_key, email, password_hash)
        )
        
        result = cursor.fetchone()
        conn.commit()
        
        if result:
            return {
                "id": result[0],
                "public_key": result[1],
                "email": result[2],
                "created_at": result[3]
            }
        return None
    except psycopg2.IntegrityError as e:
        logger.error(f"❌ Integrity error (duplicate key?): {e}")
        return None
    except Exception as e:
        logger.error(f"❌ Error creating user: {e}")
        return None
    finally:
        if conn:
            return_db_connection(conn)

def get_user_by_email(email: str) -> dict:
    """Get user by email"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id, public_key, email, password_hash, created_at FROM users WHERE email = %s",
            (email,)
        )
        
        result = cursor.fetchone()
        if result:
            return {
                "id": result[0],
                "public_key": result[1],
                "email": result[2],
                "password_hash": result[3],
                "created_at": result[4]
            }
        return None
    except Exception as e:
        logger.error(f"❌ Error getting user: {e}")
        return None
    finally:
        if conn:
            return_db_connection(conn)

def get_user_by_id(user_id: int) -> dict:
    """Get user by ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id, public_key, email, created_at FROM users WHERE id = %s",
            (user_id,)
        )
        
        result = cursor.fetchone()
        if result:
            return {
                "id": result[0],
                "public_key": result[1],
                "email": result[2],
                "created_at": result[3]
            }
        return None
    except Exception as e:
        logger.error(f"❌ Error getting user by ID: {e}")
        return None
    finally:
        if conn:
            return_db_connection(conn)

def close_db_pool():
    """Close all connections in the pool"""
    if connection_pool:
        connection_pool.closeall()
        logger.info("✅ Database connection pool closed")
