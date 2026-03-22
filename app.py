#!/usr/bin/env python3
"""
Application Flask pour le projet d'examen
Système de monitoring réseau distribué avec PostgreSQL
Communication inter-instances via API REST
"""

from flask import Flask, render_template, jsonify, request
import psycopg2
import psycopg2.extras
import json
import time
import random
import os
import requests
import threading
from datetime import datetime

app = Flask(__name__)

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'network_monitor'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'password123'),
    'port': os.getenv('DB_PORT', '5432')
}

# Instance configuration
INSTANCE_ID = os.getenv('INSTANCE_ID', 'unknown')
INSTANCE_URL = os.getenv('INSTANCE_URL', 'http://localhost:5000')

def get_db_connection():
    """Establish database connection"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def init_database():
    """Initialize database and register this instance"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        # Register this instance as a service
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO services (name, url, status)
                VALUES (%s, %s, 'active')
                ON CONFLICT (name) DO UPDATE SET
                url = EXCLUDED.url,
                status = EXCLUDED.status,
                last_check = CURRENT_TIMESTAMP
            """, (INSTANCE_ID, INSTANCE_URL))
            
            # Log instance startup
            cur.execute("""
                INSERT INTO network_events (source_service, target_service, event_type, data)
                VALUES (%s, %s, %s, %s)
            """, (INSTANCE_ID, 'system', 'instance_startup', 
                  json.dumps({'instance_url': INSTANCE_URL})))
        
        conn.commit()
        print(f"✅ Instance {INSTANCE_ID} registered successfully!")
        return True
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        return False
    finally:
        conn.close()

def discover_other_instances():
    """Discover and communicate with other instances"""
    # Use the correct URLs with mapped ports for inter-instance communication
    other_instances = [
        'http://network-monitor-main:5000',
        'http://network-monitor-1:5000', 
        'http://network-monitor-2:5000'
    ]
    
    for instance_url in other_instances:
        if instance_url != INSTANCE_URL:
            try:
                response = requests.get(f"{instance_url}/health", timeout=5)
                if response.status_code == 200:
                    log_network_event(INSTANCE_ID, instance_url, 'instance_discovery', 
                                   {'status': 'online'})
            except Exception as e:
                log_network_event(INSTANCE_ID, instance_url, 'instance_discovery', 
                               {'status': 'offline', 'error': str(e)})

def log_network_event(source, target, event_type, data):
    """Log network events to database"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO network_events (source_service, target_service, event_type, data)
                VALUES (%s, %s, %s, %s)
            """, (source, target, event_type, json.dumps(data)))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error logging network event: {e}")
        return False
    finally:
        conn.close()

def monitoring_loop():
    """Background thread for monitoring and inter-instance communication"""
    while True:
        try:
            # Discover other instances every 30 seconds
            discover_other_instances()
            
            # Simulate metrics collection
            collect_metrics()
            
        except Exception as e:
            print(f"Monitoring loop error: {e}")
        
        time.sleep(30)

def collect_metrics():
    """Simulate metrics collection for this instance"""
    metrics = {
        'cpu_usage': random.uniform(10, 90),
        'memory_usage': random.uniform(20, 80),
        'network_io': random.uniform(100, 10000),
        'response_time': random.uniform(50, 500)
    }
    
    log_network_event(INSTANCE_ID, 'system', 'metrics_collected', metrics)

@app.route('/')
def index():
    """Page principale du dashboard"""
    return render_template('index.html')

@app.route('/api/services')
def get_services():
    """API pour lister tous les services"""
    conn = get_db_connection()
    if not conn:
        return jsonify([])
    
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT * FROM services ORDER BY name")
            services = [dict(row) for row in cur.fetchall()]
        return jsonify(services)
    except Exception as e:
        print(f"Error fetching services: {e}")
        return jsonify([])
    finally:
        conn.close()

@app.route('/api/services', methods=['POST'])
def add_service():
    """API pour ajouter un nouveau service"""
    data = request.json
    name = data.get('name')
    url = data.get('url')
    
    if not name or not url:
        return jsonify({'error': 'Name and URL are required'}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        with conn.cursor() as cur:
            # Insert service
            cur.execute("""
                INSERT INTO services (name, url, status)
                VALUES (%s, %s, 'unknown')
                RETURNING id
            """, (name, url))
            service_id = cur.fetchone()[0]
            
            # Log network event
            cur.execute("""
                INSERT INTO network_events (source_service, target_service, event_type, data)
                VALUES (%s, %s, %s, %s)
            """, ('dashboard', name, 'service_added', json.dumps({'url': url})))
        
        conn.commit()
        
        # Return the created service
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT * FROM services WHERE id = %s", (service_id,))
            service = dict(cur.fetchone())
        
        return jsonify(service)
        
    except Exception as e:
        print(f"Error adding service: {e}")
        return jsonify({'error': 'Failed to add service'}), 500
    finally:
        conn.close()

@app.route('/api/network-events')
def get_network_events():
    """API pour obtenir les événements réseau"""
    conn = get_db_connection()
    if not conn:
        return jsonify([])
    
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT * FROM network_events 
                ORDER BY timestamp DESC 
                LIMIT 50
            """)
            events = [dict(row) for row in cur.fetchall()]
        return jsonify(events)
    except Exception as e:
        print(f"Error fetching events: {e}")
        return jsonify([])
    finally:
        conn.close()

@app.route('/health')
def health_check():
    """Health check endpoint for inter-instance communication"""
    return jsonify({
        'status': 'healthy',
        'instance_id': INSTANCE_ID,
        'instance_url': INSTANCE_URL,
        'timestamp': datetime.now().isoformat(),
        'service': 'network-monitor'
    })

@app.route('/api/instances')
def get_instances():
    """API pour lister toutes les instances actives"""
    conn = get_db_connection()
    if not conn:
        return jsonify([])
    
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT * FROM services 
                WHERE name LIKE '%instance%' OR name = 'main'
                ORDER BY name
            """)
            instances = [dict(row) for row in cur.fetchall()]
        return jsonify(instances)
    except Exception as e:
        print(f"Error fetching instances: {e}")
        return jsonify([])
    finally:
        conn.close()

@app.route('/api/communicate', methods=['POST'])
def communicate_with_instance():
    """API pour communication inter-instances"""
    data = request.json
    target_instance = data.get('target')
    message = data.get('message')
    
    print(f"🔵 Communication demandée: {INSTANCE_ID} -> {target_instance}")
    print(f"📨 Message: {message}")
    
    if not target_instance or not message:
        return jsonify({'error': 'Target and message are required'}), 400
    
    # Get target instance URL
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT url FROM services WHERE name = %s", (target_instance,))
            result = cur.fetchone()
            
        if not result:
            print(f"❌ Instance {target_instance} non trouvée dans la base de données")
            return jsonify({'error': 'Target instance not found'}), 404
        
        target_url = result['url']
        print(f"🎯 URL cible: {target_url}")
        
        # Send message to target instance
        try:
            print(f"📤 Envoi de la requête POST à {target_url}/api/message")
            response = requests.post(f"{target_url}/api/message", 
                                  json={'source': INSTANCE_ID, 'message': message}, 
                                  timeout=5)
            
            print(f"📥 Réponse reçue: {response.status_code}")
            if response.status_code == 200:
                # Log successful communication
                log_network_event(INSTANCE_ID, target_instance, 'inter_instance_message', 
                                 {'message': message, 'status': 'delivered'})
                return jsonify({'status': 'message sent', 'target': target_instance})
            else:
                raise Exception(f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            # Log failed communication
            print(f"❌ Erreur de communication: {str(e)}")
            log_network_event(INSTANCE_ID, target_instance, 'inter_instance_message', 
                             {'message': message, 'status': 'failed', 'error': str(e)})
            return jsonify({'error': f'Failed to communicate with {target_instance}: {str(e)}'}), 500
            
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        return jsonify({'error': 'Communication failed'}), 500
    finally:
        conn.close()

@app.route('/api/message', methods=['POST'])
def receive_message():
    """API pour recevoir des messages d'autres instances"""
    data = request.json
    source = data.get('source')
    message = data.get('message')
    
    print(f"📨 Message reçu de {source}: {message}")
    
    # Log received message
    log_network_event(source, INSTANCE_ID, 'message_received', {'message': message})
    
    return jsonify({'status': 'message received', 'instance': INSTANCE_ID})

if __name__ == '__main__':
    print("🚀 Démarrage de l'application Flask distribuée...")
    print(f"📋 Instance ID: {INSTANCE_ID}")
    print(f"🌐 Instance URL: {INSTANCE_URL}")
    print("Initialisation de la base de données...")
    
    if init_database():
        print("✅ Base de données connectée avec succès!")
        
        # Start monitoring thread
        monitoring_thread = threading.Thread(target=monitoring_loop, daemon=True)
        monitoring_thread.start()
        print("🔄 Thread de monitoring démarré")
        
        print(f"🌐 Accédez à http://localhost:5000 (Instance: {INSTANCE_ID})")
        app.run(host='0.0.0.0', port=5000, debug=True)
    else:
        print("❌ Erreur de connexion à la base de données")
        print("🐳 Démarrez avec: docker-compose up --build")
