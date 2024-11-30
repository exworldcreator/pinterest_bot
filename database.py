import asyncpg
import asyncio
from dotenv import load_dotenv
import os

load_dotenv()

async def connect_to_db():
    try:
        connection = await asyncpg.connect(
            user=os.getenv("POSTGRES_USERNAME"),         
            password=os.getenv("POSTGRES_PASSWORD"),     
            database=os.getenv("POSTGRES_DATABASE"),
            host=os.getenv("POSTGRES_HOST"),           
            port="5432"               
        )
        print("Database connection successful")
        return connection
    except Exception as e:
        print(f"Connection error: {e}")
        return None
    
async def create_user_table(connection):
    try:
        await connection.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                telegram_id BIGINT NOT NULL UNIQUE,
                username VARCHAR(255)
            );
        """)
        print("Users table created or already exists.")
    except Exception as e:
        print(f"Creating table error: {e}")
        
async def add_user_to_db(connection, telegram_id, username):
    try:
        await connection.execute("""
            INSERT INTO users (telegram_id, username)
            VALUES ($1, $2)
            ON CONFLICT (telegram_id) DO NOTHING;
        """, telegram_id, username)
        print(f"User {username} added successfully.")
    except Exception as e:
        print(f"Adding user error: {e}")
        
async def get_all_user_ids(connection):
    result = await connection.fetch("SELECT telegram_id FROM users")
    return [row['telegram_id'] for row in result]