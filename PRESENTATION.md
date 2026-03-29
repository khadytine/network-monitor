# Network Monitor - Support de Présentation

## 📋 Table des Matières

1. [Problème Résolu](#1-problème-résolu)
2. [Architecture du Système](#2-architecture-du-système)
3. [Aspect Réseau du Projet](#3-aspect-réseau-du-projet)
4. [Technologies Utilisées](#4-technologies-utilisées)
5. [Fonctionnement de l'Application](#5-fonctionnement-de-lapplication)
6. [Guide de Démonstration](#6-guide-de-démonstration)

---

## 1. Problème Résolu

### 🎯 Contexte
Dans les architectures microservices et systèmes distribués modernes, les administrateurs système font face à des défis critiques :

- **Visibilité limitée** : Difficulté à surveiller l'état de santé des services distribués
- **Détection tardive** : Les pannes sont découvertes tardivement, impactant les utilisateurs
- **Absence de centralisation** : Pas de vue unifiée sur les métriques de performance
- **Communication opaque** : Les interactions inter-services ne sont pas traçables

### 💡 Solution Proposée
**Network Monitor** fournit une solution complète de surveillance réseau distribué avec :

- **Dashboard temps réel** : Visualisation centralisée de tous les services
- **Collecte automatique** : Métriques de performance collectées toutes les 30 secondes
- **Architecture scalable** : Facile ajout de nouvelles instances de monitoring
- **Communication sécurisée** : API REST pour interconnexion des services
- **Base de données centralisée** : PostgreSQL pour stockage historique

### 🎨 Originalité du Projet
- **Pas une application de chat** : Solution professionnelle de monitoring
- **Architecture distribuée native** : Conçue pour la scalabilité
- **Monitoring bidirectionnel** : Services se surveillent mutuellement
- **Dashboard interactif** : Interface moderne avec WebSocket

---

## 2. Architecture du Système

### 🏗️ Vue d'ensemble

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Network                           │
│                  (monitor-network)                          │
│  Subnet: 172.20.0.0/16                                     │
├─────────────────┬─────────────────┬─────────────────────────┤
│   Instance 1     │   Instance 2     │      Instance 3         │
│   (Port: 5000)   │   (Port: 5001)   │      (Port: 5002)      │
│                 │                 │                         │
│ • Flask App     │ • Flask App     │ • Flask App            │
│ • Socket.IO     │ • Socket.IO     │ • Socket.IO            │
│ • Metrics       │ • Metrics       │ • Metrics              │
│ • Health Check  │ • Health Check  │ • Health Check         │
└─────────┬───────┴─────────┬───────┴─────────┬───────────────┘
          │                 │                 │
          └─────────────────┼─────────────────┘
                            │
                ┌───────────┴───────────┐
                │   PostgreSQL DB      │
                │   (Port: 5432)        │
                │                     │
                │ • services table    │
                │ • metrics table     │
                │ • network_events    │
                └─────────────────────┘
```

### 🧩 Composants Principaux

#### 1. **Application Flask (app.py)**
- **Framework web** : Flask 2.3.3 avec Socket.IO pour temps réel
- **Base de données** : Connexion PostgreSQL avec Psycopg2
- **API RESTful** : Endpoints pour services et communication
- **Monitoring** : Thread background pour collecte métriques

#### 2. **Base de Données PostgreSQL**
- **services** : Information sur les services monitorés
- **metrics** : Métriques de performance historiques
- **network_events** : Événements de communication inter-services

#### 3. **Frontend (templates/index.html)**
- **Dashboard interactif** avec Chart.js
- **WebSocket** pour mises à jour live
- **Design responsive** moderne
- **API calls** pour communication backend

#### 4. **Conteneurisation Docker**
- **Dockerfile** : Build optimisé multi-stage
- **docker-compose.yml** : Orchestration multi-conteneurs
- **Réseau isolé** : Bridge network avec subnet personnalisé

#### 5. **Réseau et Communication**
- **Docker Bridge Network** : Communication inter-conteneurs
- **API REST** : Communication HTTP entre services
- **WebSocket** : Mise à jour temps réel dashboard
- **Health Checks** : Surveillance automatique

---

## 3. Aspect Réseau du Projet

### 🌐 Configuration Réseau

#### Docker Network Personnalisé
```yaml
networks:
  monitor-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

#### Mapping des Ports
- **Instance principale** : Port 5000 → 5000
- **Instance 1** : Port 5001 → 5000 (interne)
- **Instance 2** : Port 5002 → 5000 (interne)
- **PostgreSQL** : Port 5432 → 5432

### 🔄 Communication Inter-Services

#### 1. **Découverte Automatique**
```python
def discover_other_instances():
    other_instances = [
        'http://network-monitor-main:5000',
        'http://network-monitor-1:5000', 
        'http://network-monitor-2:5000'
    ]
    # Vérification santé de chaque instance
```

#### 2. **API REST Communication**
```python
@app.route('/api/communicate', methods=['POST'])
def communicate_with_instance():
    # Envoi message vers autre instance
    response = requests.post(f"{target_url}/api/message", json=data)
```

#### 3. **WebSocket Temps Réel**
```python
@socketio.on('connect')
def handle_connect():
    # Envoi métriques en temps réel
    socketio.emit('metrics_update', metrics_data)
```

### 📊 Monitoring Réseau

#### Types de Métriques Collectées
- **Response Time** : Temps de réponse HTTP (ms)
- **CPU Usage** : Utilisation processeur (%)
- **Memory Usage** : Utilisation mémoire (%)
- **Network I/O** : Trafic réseau (bytes/s)

#### Événements Réseau Loggués
- **instance_discovery** : Découverte nouveaux services
- **inter_instance_message** : Communication inter-services
- **health_check** : Vérification santé
- **metrics_collected** : Collecte métriques

---

## 4. Technologies Utilisées

### 🐍 Backend

#### Flask Ecosystem
- **Flask 2.3.3** : Framework web Python léger
- **Flask-SocketIO 5.3.6** : Support WebSocket temps réel
- **Psycopg2 2.9.7** : Driver PostgreSQL pour Python
- **Requests 2.31.0** : Client HTTP pour appels API

#### Python Standard Library
- **Threading** : Background monitoring
- **JSON** : Sérialisation données
- **OS** : Variables environnement
- **Time/Random** : Gestion temporelle et simulation

### 🗄️ Base de Données

#### PostgreSQL 15
- **ACID compliant** : Transactions fiables
- **Performance** : Indexes optimisés
- **Features avancées** : Vues, fonctions, triggers
- **Scalabilité** : Support gros volumes

#### Schema Design
```sql
CREATE TABLE services (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    url TEXT NOT NULL,
    status TEXT DEFAULT 'unknown',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE metrics (
    id SERIAL PRIMARY KEY,
    service_id INTEGER REFERENCES services(id),
    response_time REAL,
    cpu_usage REAL,
    memory_usage REAL,
    network_io REAL,
    timestamp TIMESTAMP DEFAULT NOW()
);
```

### 🌐 Frontend

#### HTML5/CSS3/JavaScript
- **HTML5 sémantique** : Structure moderne
- **CSS3 responsive** : Design adaptatif
- **JavaScript ES6+** : Logique client moderne

#### Bibliothèques Frontend
- **Chart.js** : Visualisation données temps réel
- **Socket.IO Client** : Communication bidirectionnelle
- **Bootstrap** : Framework CSS (optionnel)

### 🐳 Conteneurisation

#### Docker Technologies
- **Docker Engine** : Runtime conteneurs
- **Docker Compose** : Orchestration multi-conteneurs
- **Dockerfile** : Build optimisé multi-stage

#### Build Optimisé
```dockerfile
# Multi-stage build
FROM python:3.11-slim as base
# Installation dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Copie code
COPY . .
# User non-root
RUN useradd app && chown -R app:app /app
USER app
```

### 🔄 CI/CD

#### GitHub Actions
- **Build automatique** : À chaque push
- **Test automatique** : Validation code
- **Publication Docker Hub** : Push automatique
- **SBOM generation** : Sécurité transparence

---

## 5. Fonctionnement de l'Application

### 🚀 Cycle de Vie

#### 1. **Initialisation**
```python
if __name__ == '__main__':
    init_database()          # Création tables
    register_instance()      # Enregistrement service
    start_monitoring()       # Thread background
    app.run(host='0.0.0.0') # Démarrage Flask
```

#### 2. **Monitoring Continu**
```python
def monitoring_loop():
    while True:
        collect_metrics()      # Collecte métriques
        discover_instances()   # Découverte services
        log_network_events()   # Logging événements
        time.sleep(30)         # Toutes les 30 secondes
```

#### 3. **Communication Temps Réel**
```python
@socketio.on('request_metrics')
def handle_metrics_request():
    metrics = get_current_metrics()
    emit('metrics_update', metrics)
```

### 📊 Flux de Données

```
1. Collecte (toutes les 30s)
   ↓
2. Stockage (PostgreSQL)
   ↓
3. Diffusion (WebSocket)
   ↓
4. Visualisation (Dashboard)
   ↓
5. Nettoyage (après 7 jours)
```

### 🔄 Interactions Utilisateur

#### Dashboard Features
- **Vue services** : État de tous les services monitorés
- **Ajout service** : Formulaire pour nouveaux services
- **Métriques temps réel** : Graphiques auto-actualisés
- **Communication inter-services** : Interface messagerie
- **Événements réseau** : Journal des communications

#### API Endpoints
- `GET /api/services` : Lister tous les services
- `POST /api/services` : Ajouter nouveau service
- `GET /api/instances` : Lister instances actives
- `POST /api/communicate` : Envoyer message inter-service
- `GET /health` : Health check service

---

## 6. Guide de Démonstration

### 🎯 Scénario de Démonstration Complète

#### Étape 1 : Démarrage des Conteneurs Docker
```bash
# Vérifier Docker
docker --version
docker-compose --version

# Lancer l'application
docker-compose -f docker-compose-simple.yml up --build

# Vérifier l'état
docker-compose -f docker-compose-simple.yml ps
```

**À montrer :**
- Build des images Docker
- Création du réseau personnalisé
- Démarrage des conteneurs PostgreSQL et Flask
- Health checks automatiques

#### Étape 2 : Accès au Dashboard
```bash
# Vérifier l'accessibilité
curl http://localhost:5000
# Ou ouvrir navigateur sur http://localhost:5000
```

**À montrer :**
- Dashboard principal avec services actifs
- Interface moderne et responsive
- Métriques en temps réel
- Graphiques dynamiques

#### Étape 3 : Communication Réseau Inter-Services
```bash
# Vérifier le réseau Docker
docker network ls
docker network inspect exam_monitor-network

# Logs de communication
docker-compose -f docker-compose-simple.yml logs -f network-monitor
```

**À montrer :**
- Configuration réseau Docker
- Communication entre conteneurs
- Logs des appels API
- Health checks automatiques

#### Étape 4 : Utilisation de la Base de Données
```bash
# Connexion à PostgreSQL
docker exec -it network-monitor-db psql -U postgres -d network_monitor

# Vérifier les tables
\dt
SELECT * FROM services;
SELECT * FROM metrics ORDER BY timestamp DESC LIMIT 10;
SELECT * FROM network_events ORDER BY timestamp DESC LIMIT 5;
```

**À montrer :**
- Structure de la base de données
- Données insérées automatiquement
- Requêtes SQL complexes
- Performance des indexes

#### Étape 5 : Fonctionnalités Avancées

##### 5.1 Ajout de Service
```bash
# Via API
curl -X POST http://localhost:5000/api/services \
  -H "Content-Type: application/json" \
  -d '{"name": "web-server", "url": "http://localhost:8080"}'
```

##### 5.2 Communication Inter-Instances
```bash
# Test communication
curl -X POST http://localhost:5000/api/communicate \
  -H "Content-Type: application/json" \
  -d '{"target": "instance-1", "message": "Hello from main"}'
```

##### 5.3 Monitoring des Conteneurs
```bash
# Statistiques ressources
docker stats

# Surveillance réseau
docker exec network-monitor-app netstat -tulpn
```

#### Étape 6 : Déploiement et CI/CD

##### 6.1 Repository GitHub
```bash
# Montrer le repository
git remote -v
git log --oneline -5
```

##### 6.2 Image Docker Hub
```bash
# Montrer l'image publiée
docker pull khadytine/network-monitor
docker images | grep network-monitor
```

##### 6.3 Pipeline CI/CD
```bash
# Montrer le workflow GitHub Actions
cat .github/workflows/docker.yml
```

### 🎪 Points Clés à Mettre en Évidence

#### 1. **Architecture Distribuée**
- Plusieurs instances Flask communiquant
- Base de données centralisée
- Réseau Docker isolé

#### 2. **Monitoring Temps Réel**
- WebSocket pour mises à jour instantanées
- Graphiques dynamiques avec Chart.js
- Collecte automatique des métriques

#### 3. **Communication Réseau**
- API REST entre services
- Health checks automatiques
- Logging des événements réseau

#### 4. **Conteneurisation**
- Build Docker optimisé
- Orchestration avec docker-compose
- Réseau personnalisé sécurisé

#### 5. **Déploiement Moderne**
- CI/CD avec GitHub Actions
- Publication Docker Hub automatique
- Code versionné et documenté

### 📝 Checklist de Démonstration

- [ ] **Docker** : Build et lancement des conteneurs
- [ ] **Dashboard** : Accès et navigation
- [ ] **Réseau** : Communication inter-services
- [ ] **Base de données** : PostgreSQL et requêtes
- [ ] **API** : Endpoints REST fonctionnels
- [ ] **Monitoring** : Métriques temps réel
- [ ] **GitHub** : Repository et code source
- [ ] **Docker Hub** : Image publiée
- [ ] **CI/CD** : Pipeline automatique

### 🎯 Questions Anticipées

#### Q : Pourquoi PostgreSQL plutôt que MongoDB ?
**R** : PostgreSQL offre des requêtes SQL complexes, des transactions ACID, et une meilleure intégration avec Flask pour ce cas d'usage de monitoring structuré.

#### Q : Comment assurez-vous la scalabilité ?
**R** : Architecture permet d'ajouter facilement des instances dans docker-compose.yml, avec découverte automatique et load balancing potentiel.

#### Q : Quelle est la latence de monitoring ?
**R** : 30 secondes entre chaque collecte, avec WebSocket pour diffusion instantanée au dashboard.

#### Q : Comment gérez-vous la sécurité ?
**R** : Réseau Docker isolé, variables d'environnement pour secrets, user non-root dans conteneurs.

---

## 🏆 Conclusion

Network Monitor démontre avec succès l'intégration des concepts réseau dans une application Flask moderne :

- **Architecture distribuée** fonctionnelle et scalable
- **Monitoring temps réel** performant et intuitif  
- **Conteneurisation complète** avec Docker
- **Réseau sécurisé** et optimisé
- **Déploiement automatisé** via CI/CD

Le projet répond parfaitement aux exigences de l'examen tout en apportant une solution innovante et professionnelle à un problème réel de surveillance réseau.

**Points forts pour l'évaluation :**
- ✅ Respect des contraintes techniques
- ✅ Originalité et complexité
- ✅ Qualité du code et documentation
- ✅ Déploiement professionnel
- ✅ Démonstration complète

---

*Ce support de présentation accompagne le projet Network Monitor pour l'examen de développement web Flask.*
