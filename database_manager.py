import sqlite3
import pandas as pd
from datetime import datetime
import os

DB_FILENAME = "health_data.db"

class DatabaseManager:
    """
    Handles all interactions with the SQLite database.
    """
    def __init__(self, db_path=DB_FILENAME):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        """Creates the necessary tables if they don't exist."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Metrics table - stores periodic system health snapshots
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                cpu_load REAL,
                memory_usage REAL,
                battery_percentage INTEGER,
                is_charging INTEGER,
                top_process_name TEXT,
                top_process_cpu REAL
            )
        ''')
        
        # Events table - stores alerts and app lifecycle events (for future use)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                event_type TEXT,
                message TEXT
            )
        ''')
        
        conn.commit()
        conn.close()

    def insert_metric(self, data):
        """
        Inserts a single metric record.
        data: dict containing keys matching the CSV header.
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO metrics (timestamp, cpu_load, memory_usage, battery_percentage, is_charging, top_process_name, top_process_cpu)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('timestamp'),
            data.get('cpu_load'),
            data.get('memory_usage'),
            data.get('battery_percentage') if data.get('battery_percentage') != "N/A" else None,
            1 if data.get('is_charging') == True else 0, # Convert bool to int
            data.get('top_process_name'),
            data.get('top_process_cpu')
        ))
        
        conn.commit()
        conn.close()

    def get_recent_history(self, limit=1000):
        """
        Returns the last 'limit' records as a pandas DataFrame.
        Used by the GraphWindow.
        """
        try:
            conn = self._get_connection()
            query = f"SELECT * FROM metrics ORDER BY id DESC LIMIT {limit}"
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            # Sort by timestamp ascending for the graph
            if not df.empty:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df = df.sort_values(by='timestamp')
                
            return df
        except Exception as e:
            print(f"Error fetching history: {e}")
            return pd.DataFrame()

    def migrate_from_csv(self, csv_path):
        """
        One-time utility to import data from the old CSV file.
        """
        if not os.path.exists(csv_path):
            return 0
            
        print(f"Migrating data from {csv_path}...")
        try:
            df = pd.read_csv(csv_path)
            conn = self._get_connection()
            
            # Simple bulk insert using pandas
            # Rename cols to match DB schema if needed (they match mostly)
            # Handle "N/A" in battery
            df['battery_percentage'] = pd.to_numeric(df['battery_percentage'], errors='coerce')
            df['is_charging'] = df['is_charging'].apply(lambda x: 1 if str(x).lower() == 'true' else 0)
            
            df.to_sql('metrics', conn, if_exists='append', index=False)
            conn.close()
            
            # Rename existing CSV to standard backup name to prevent re-import
            backup_name = f"{csv_path}.bak"
            if os.path.exists(backup_name):
                os.remove(backup_name)
            os.rename(csv_path, backup_name)
            
            return len(df)
        except Exception as e:
            print(f"Migration error: {e}")
            return 0
