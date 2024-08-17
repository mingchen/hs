#!/usr/bin/env python3

import os
import sqlite3
from typing import List


def db_connect(db_file: str):
    """Connect to the SQLite database and create the table if it doesn't exist"""
    connection = sqlite3.connect(db_file)

    cursor = connection.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS host (host TEXT PRIMARY KEY)')
    connection.commit()

    return connection


def db_insert_hosts(connection: sqlite3.Connection, hosts: List[str], batch_size: int = 500):
    cursor = connection.cursor()
    for i in range(0, len(hosts), batch_size):
        batch = hosts[i:i + batch_size]
        cursor.executemany('INSERT INTO host (host) VALUES (?)', [(host.lower(),) for host in batch])
        connection.commit()


def read_hosts(file_path: str) -> List[str]:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f'File {file_path} not found')

    with open(file_path, 'r') as file:
        hosts = [line.lower().strip() for line in file]
        # sort and remove duplicates
        return sorted(list(set(hosts)))


def db_compact(connection: sqlite3.Connection):
    """Compact the database to reduce disk usage"""
    cursor = connection.cursor()
    cursor.execute('VACUUM')
    connection.commit()


def main():
    input_file = os.environ.get("INPUT_FILE", 'result.txt')
    db_file = os.environ.get("DB_FILE", 'http2https.db')

    # hosts = ['example.com', 'example.org', 'example.net']
    hosts = read_hosts(input_file)

    connection = db_connect(db_file)

    db_insert_hosts(connection, hosts)

    db_compact(connection)

    connection.close()


if __name__ == '__main__':
    main()
