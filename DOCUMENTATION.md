# Documentation Technique - NetMon

## 📋 Table des Matières

1. [Vue d'Ensemble](#1-vue-densemble)
2. [Architecture Détaillée](#2-architecture-détaillée)
3. [Installation](#3-installation)
4. [Configuration](#4-configuration)
5. [Utilisation](#5-utilisation)
6. [API REST](#6-api-rest)
7. [Base de Données](#7-base-de-données)
8. [Dépannage](#8-dépannage)

---

## 1. Vue d'Ensemble

### 🎯 Objectif
NetMon est une solution de monitoring réseau distribué qui permet de surveiller en temps réel les performances et la disponibilité des services dans une architecture microservices.

### 🏗️ Architecture Principale
- **3 instances** : main (5000), instance-1 (5001), instance-2 (5002)
- **Base de données** : PostgreSQL centralisée pour stockage des métriques
- **Communication** : API REST entre instances
- **Interface web** : Dashboard Flask avec mise à jour temps réel

---

## 2. Architecture Détaillée

### Schéma Technique
```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Flask)                        │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐  │
│  │   Dashboard │ │   Formulaire│ │    Graphiques       │  │
│  │   Principal │ │  Ajout Svc  │ │   Temps Réel        │  │
│  └─────────────┘ └─────────────┘ └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend (Python/Flask)                  │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐  │
│  │   API REST  │ │  Monitoring │ │  Communication     │  │
│  │  Endpoints  │ │   Thread    │ │   Inter-Instances  │  │
│  └─────────────┘ └─────────────┘ └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Base de Données                         │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐  │
│  │   Services  │ │   Metrics   │ │   Network_Events    │  │
│  │    Table    │ │    Table    │ │      Table          │  │
│  └─────────────┘ └─────────────┘ └─────────────────────┘  │
│                 PostgreSQL (Port 5432)                    │
└─────────────────────────────────────────────────────────────┘
```

### Flux de Données
1. **Collecte** : Thread background collecte métriques toutes les 30s
2. **Stockage** : Métriques sauvegardées dans PostgreSQL
3. **Communication** : Instances échangent données via API REST
4. **Affichage** : Dashboard mis à jour en temps réel

---

## 3. Installation

### Prérequis
- Python 3.11+
- PostgreSQL 15+
- Docker (optionnel)

### Installation Locale
```bash
# 1. Cloner le dépôt
git clone https://github.com/khadytine/network-monitor.git
cd network-monitor

# 2. Installer dépendances Python
pip install -r requirements.txt

# 3. Configurer PostgreSQL
createdb network_monitor
psql -d network_monitor -f init.sql

# 4. Lancer l'application
python app.py
```

### Installation avec Docker
```bash
# 1. Lancer tous les services
docker-compose up -d

# 2. Accéder au dashboard
http://localhost:5000
```

### Mode Démo (Recommandé)
```bash
# 1. Installer dépendances minimales
pip install Flask requests

# 2. Lancer la version démo
python run-local.py

# 3. Accéder au dashboard
http://localhost:5000
```

---

## 4. Configuration

### Variables d'Environnement
```bash
# Base de données
DB_HOST=localhost
DB_NAME=network_monitor
DB_USER=postgres
DB_PASSWORD=password123
DB_PORT=5432

# Instance
INSTANCE_ID=main
INSTANCE_URL=http://localhost:5000
```

### Configuration Docker
```yaml
# docker-compose.yml
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: network_monitor
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password123
  
  network-monitor-main:
    build: .
    ports:
      - "5000:5000"
    depends_on:
      - postgres
```

---

## 5. Utilisation

### Interface Web
1. **Accueil** : Vue d'ensemble des services monitorés
2. **Ajout Service** : Formulaire pour ajouter un nouveau service
3. **Graphiques** : Visualisation temps réel des métriques
4. **Événements** : Journal des communications inter-services

### Fonctionnalités Principales
- **Monitoring automatique** : Toutes les 30 secondes
- **Alertes** : Détection de pannes et lenteurs
- **Historique** : 7 jours de métriques conservées
- **Multi-instances** : Communication entre instances

---

## 6. API REST

### Endpoints Disponibles

#### Services
```http
GET  /api/services              # Lister tous les services
POST /api/services              # Ajouter un service
GET  /api/services/<id>         # Détails d'un service
PUT  /api/services/<id>         # Mettre à jour un service
DELETE /api/services/<id>        # Supprimer un service
```

#### Métriques
```http
GET /api/metrics/<service_id>    # Métriques d'un service
GET /api/metrics/summary        # Résumé des métriques
```

#### Communication
```http
POST /api/communicate           # Message entre instances
GET /api/network-events         # Événements réseau
```

### Exemple d'Utilisation
```python
# Ajouter un service
import requests

service_data = {
    "name": "API Backend",
    "url": "https://api.example.com",
    "description": "API principale"
}

response = requests.post(
    "http://localhost:5000/api/services",
    json=service_data
)
```

---

## 7. Base de Données

### Schéma PostgreSQL
```sql
-- Table des services
CREATE TABLE services (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    url VARCHAR(500) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'unknown',
    created_at TIMESTAMP DEFAULT NOW(),
    last_check TIMESTAMP
);

-- Table des métriques
CREATE TABLE metrics (
    id SERIAL PRIMARY KEY,
    service_id INTEGER REFERENCES services(id),
    response_time INTEGER,
    cpu_usage FLOAT,
    memory_usage FLOAT,
    network_io FLOAT,
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Table des événements réseau
CREATE TABLE network_events (
    id SERIAL PRIMARY KEY,
    source_instance VARCHAR(100),
    target_instance VARCHAR(100),
    event_type VARCHAR(100),
    data JSONB,
    timestamp TIMESTAMP DEFAULT NOW()
);
```

### Requêtes Utiles
```sql
-- Services actifs
SELECT name, status, last_check FROM services WHERE status = 'active';

-- Métriques récentes
SELECT * FROM metrics WHERE timestamp > NOW() - INTERVAL '1 hour';

-- Événements réseau
SELECT * FROM network_events ORDER BY timestamp DESC LIMIT 10;
```

---

## 8. Dépannage

### Problèmes Courants

#### Erreur de connexion PostgreSQL
```
connection to server at "localhost" failed
```
**Solution** : Vérifiez que PostgreSQL est démarré :
```bash
# Windows
net start postgresql-x64-15

# Linux/macOS
sudo systemctl start postgresql
```

#### Port déjà utilisé
```
Address already in use
```
**Solution** : Changez de port ou tuez le processus :
```bash
# Trouver le processus
netstat -ano | findstr :5000

# Tuer le processus
taskkill /PID <PID> /F
```

#### Erreur d'encodage
```
UnicodeEncodeError: 'charmap' codec can't encode
```
**Solution** : Utilisez `run-local.py` qui n'a pas d'emojis.

### Logs et Debugging
```bash
# Logs de l'application
python app.py --debug

# Logs Docker
docker-compose logs -f network-monitor-main

# Logs PostgreSQL
tail -f /var/log/postgresql/postgresql-15-main.log
```

### Performance
- **Nettoyage automatique** : Métriques de plus de 7 jours supprimées
- **Optimisation mémoire** : Limite de 1000 métriques par service
- **Monitoring** : Utiliser `docker stats` pour surveiller les ressources

---

## 📞 Support

Pour toute question ou problème :
- **GitHub** : https://github.com/khadytine/network-monitor/issues
- **Documentation** : Voir `README.md` et `PRESENTATION.md`
- **Démonstration** : Utiliser `python run-local.py`

---

*Auteur : Khady Tine*  
*Projet : Network Monitor - Examen L3 RI*  
*Date : Mars 2026*
