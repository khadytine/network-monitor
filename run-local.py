#!/usr/bin/env python3
"""
Version locale du Network Monitor pour démonstration rapide
Utilise SQLite au lieu de PostgreSQL pour éviter les problèmes de connexion
"""

from flask import Flask, render_template, jsonify, request
import sqlite3
import json
import time
import random
import threading
from datetime import datetime

app = Flask(__name__)

# Database setup with SQLite
def init_db():
    conn = sqlite3.connect('network_monitor.db')
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            url TEXT NOT NULL,
            status TEXT DEFAULT 'unknown',
            response_time REAL,
            last_check TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS network_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_service TEXT,
            target_service TEXT,
            event_type TEXT,
            data TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert default instances
    instances = [
        ('main', 'http://localhost:5000'),
        ('instance-1', 'http://localhost:5001'),
        ('instance-2', 'http://localhost:5002')
    ]
    
    for name, url in instances:
        cursor.execute('''
            INSERT OR REPLACE INTO services (name, url, status)
            VALUES (?, ?, 'active')
        ''', (name, url))
    
    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect('network_monitor.db')
    conn.row_factory = sqlite3.Row
    return conn

def log_event(source, target, event_type, data):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO network_events (source_service, target_service, event_type, data)
        VALUES (?, ?, ?, ?)
    ''', (source, target, event_type, json.dumps(data)))
    conn.commit()
    conn.close()

def simulate_monitoring():
    """Background thread to simulate monitoring"""
    while True:
        try:
            conn = get_db()
            cursor = conn.cursor()
            
            # Get all services
            cursor.execute('SELECT * FROM services')
            services = cursor.fetchall()
            
            for service in services:
                # Simulate metrics
                metrics = {
                    'cpu_usage': random.uniform(10, 90),
                    'memory_usage': random.uniform(20, 80),
                    'network_io': random.uniform(100, 10000),
                    'response_time': random.uniform(50, 500)
                }
                
                log_event(service['name'], 'system', 'metrics_collected', metrics)
                
                # Simulate inter-instance discovery
                if service['name'] != 'main':
                    status = 'online' if random.random() > 0.1 else 'offline'
                    log_event('main', service['name'], 'instance_discovery', {'status': status})
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Monitoring error: {e}")
        
        time.sleep(30)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'instance_id': 'main',
        'instance_url': 'http://localhost:5000',
        'timestamp': datetime.now().isoformat(),
        'service': 'network-monitor'
    })

@app.route('/api/services')
def get_services():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM services ORDER BY name')
    services = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(services)

@app.route('/api/instances')
def get_instances():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM services WHERE name LIKE "%instance%" OR name = "main" ORDER BY name')
    instances = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(instances)

@app.route('/api/network-events')
def get_events():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM network_events ORDER BY timestamp DESC LIMIT 50')
    events = []
    for row in cursor.fetchall():
        event = dict(row)
        event['data'] = json.loads(event['data']) if event['data'] else {}
        events.append(event)
    conn.close()
    return jsonify(events)

@app.route('/api/services', methods=['POST'])
def add_service():
    data = request.json
    name = data.get('name')
    url = data.get('url')
    
    if not name or not url:
        return jsonify({'error': 'Name and URL are required'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO services (name, url, status)
        VALUES (?, ?, 'unknown')
    ''', (name, url))
    
    service_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    log_event('dashboard', name, 'service_added', {'url': url})
    
    return jsonify({'id': service_id, 'name': name, 'url': url})

@app.route('/api/communicate', methods=['POST'])
def communicate():
    data = request.json
    target = data.get('target')
    message = data.get('message')
    
    if not target or not message:
        return jsonify({'error': 'Target and message are required'}), 400
    
    print(f"Communication: main -> {target}")
    print(f"Message: {message}")
    
    # Simulate successful communication
    log_event('main', target, 'inter_instance_message', {'message': message, 'status': 'delivered'})
    
    # Simulate receiving message
    log_event('main', 'main', 'message_received', {'message': f"Echo from {target}: {message}"})
    
    return jsonify({'status': 'message sent', 'target': target})

@app.route('/api/message', methods=['POST'])
def receive_message():
    data = request.json
    source = data.get('source')
    message = data.get('message')
    
    print(f"Message received from {source}: {message}")
    
    log_event(source, 'main', 'message_received', {'message': message})
    
    return jsonify({'status': 'message received', 'instance': 'main'})

if __name__ == '__main__':
    print("Demarrage du Network Monitor (version locale)...")
    print("Instance ID: main")
    print("URL: http://localhost:5000")
    
    # Initialize database
    init_db()
    print("Base de donnees initialisee!")
    
    # Start monitoring thread
    monitoring_thread = threading.Thread(target=simulate_monitoring, daemon=True)
    monitoring_thread.start()
    print("Monitoring demarre!")
    
    print("Accedez a http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
