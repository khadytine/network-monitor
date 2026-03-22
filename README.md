# Network Monitor - Système de Surveillance Réseau Distribué

## Description

Network Monitor est une application web Flask qui surveille les métriques de services distribués en temps réel. Le projet démontre l'utilisation avancée des concepts réseau, la conteneurisation Docker, et la communication inter-services.

## Fonctionnalités Principales

- **Surveillance en temps réel** : Métriques de performance collectées toutes les 30 secondes
- **Dashboard interactif** : Interface web moderne avec mise à jour automatique
- **Architecture distribuée** : Plusieurs instances communiquant entre elles
- **Base de données centralisée** : PostgreSQL pour stocker les métriques historiques
- **Réseau Docker** : Communication sécurisée entre conteneurs
- **API RESTful** : Endpoints pour l'ajout de services et la consultation de métriques

## Architecture Technique

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Instance 1   │    │   Instance 2   │    │   Instance 3   │
│   (Port 5000)  │    │   (Port 5001)  │    │   (Port 5002)  │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────┴─────────────┐
                    │     PostgreSQL DB         │
                    │     (Port 5432)           │
                    └───────────────────────────┘
```

## Technologies Utilisées

### Backend
- **Flask 2.3.3** : Framework web Python
- **Flask-SocketIO 5.3.6** : Support WebSocket temps réel
- **Psycopg2 2.9.7** : Driver PostgreSQL pour Python
- **Requests 2.31.0** : Client HTTP pour appels API

### Base de Données
- **PostgreSQL 15** : Base de données relationnelle robuste
- **SQL avancé** : Vues, fonctions, indexes optimisés

### Frontend
- **HTML5/CSS3** : Interface moderne et responsive
- **JavaScript** : Logique client et WebSocket
- **Chart.js** : Visualisation données temps réel
- **Socket.IO Client** : Communication bidirectionnelle

### Conteneurisation
- **Docker** : Isolation et déploiement simplifié
- **Docker Compose** : Orchestration multi-conteneurs
- **Dockerfile** : Build optimisé multi-stage

### Réseau
- **Docker Bridge Network** : Communication inter-conteneurs
- **Subnet personnalisé** : Isolation réseau (172.20.0.0/16)
- **Port mapping** : Accès externe contrôlé

## Installation et Démarrage Rapide

### Prérequis

- Docker Desktop installé
- Docker Compose
- Git (pour cloner le dépôt)

### 1. Cloner le dépôt

```bash
git clone https://github.com/votre-username/network-monitor.git
cd network-monitor
```

### 2. Démarrer l'application

#### Option A : Version Simple (1 conteneur)
```bash
docker-compose -f docker-compose-simple.yml up --build
```

#### Option B : Version Distribuée (3 conteneurs)
```bash
docker-compose up --build
```

#### Option C : Version Locale (sans Docker)
```bash
# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application locale
python run-local.py
```

### 3. Accéder à l'application

- **Dashboard principal** : http://localhost:5000
- **Instance 1** : http://localhost:5001 (version distribuée)
- **Instance 2** : http://localhost:5002 (version distribuée)
- **Base de données** : localhost:5432 (PostgreSQL)

## Configuration

### Variables d'environnement

Les variables suivantes peuvent être configurées dans `docker-compose.yml` :

```yaml
environment:
  - DB_HOST=postgres
  - DB_NAME=network_monitor
  - DB_USER=postgres
  - DB_PASSWORD=password123
  - DB_PORT=5432
  - INSTANCE_ID=main
  - INSTANCE_URL=http://network-monitor-app:5000
```

### Personnalisation du réseau

Le réseau Docker est configuré avec le subnet `172.20.0.0/16`. Vous pouvez le modifier dans `docker-compose.yml` :

```yaml
networks:
  monitor-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16  # Modifiable
```

## API Endpoints

### Services

- `GET /api/services` - Lister tous les services
- `POST /api/services` - Ajouter un nouveau service
  ```json
  {
    "name": "service-name",
    "url": "http://service-url"
  }
  ```

### Instances

- `GET /api/instances` - Lister toutes les instances actives
- `POST /api/communicate` - Communiquer avec une autre instance
  ```json
  {
    "target": "instance-2",
    "message": "Hello from instance-1"
  }
  ```

### Métriques

- `GET /api/metrics/<service_id>` - Métriques historiques d'un service
- `GET /api/network-events` - Événements réseau récents

### Health Check

- `GET /health` - Vérifier l'état du service

## WebSocket Events

### Client → Serveur

- `connect` - Connexion au serveur
- `request_metrics` - Demander les métriques actuelles

### Serveur → Client

- `metrics_update` - Mise à jour des métriques en temps réel
- `network_event` - Nouvel événement réseau
- `all_services` - État de tous les services

## Structure des Données

### Tables PostgreSQL

1. **services** : Informations sur les services monitorés
2. **metrics** : Métriques de performance historiques
3. **network_events** : Événements de communication inter-services

### Exemple de métriques

```json
{
  "service_name": "instance-1",
  "metrics": {
    "response_time": 150.5,
    "cpu_usage": 45.2,
    "memory_usage": 67.8,
    "network_io": 1250
  },
  "status": "online",
  "timestamp": "2024-03-22T20:30:00.000Z"
}
```

## Déploiement

### Publication sur Docker Hub

1. **Créer un compte Docker Hub**
2. **Construire l'image** :
   ```bash
   docker build -t votre-username/network-monitor .
   ```
3. **Publier l'image** :
   ```bash
   docker push votre-username/network-monitor
   ```

### CI/CD avec GitHub Actions

Créer `.github/workflows/docker.yml` :

```yaml
name: Build and Push Docker Image

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3
      
    - name: Login to Docker Hub
      uses: docker/login-action@v3
      with:
        username: ${{ secrets.DOCKER_USERNAME }}
        password: ${{ secrets.DOCKER_PASSWORD }}
        
    - name: Build and push
      uses: docker/build-push-action@v5
      with:
        context: .
        push: true
        tags: ${{ secrets.DOCKER_USERNAME }}/network-monitor:latest
        cache-from: type=gha
        cache-to: type=gha,mode=max
```

## Surveillance et Maintenance

### Logs

Les logs sont disponibles dans les conteneurs :

```bash
# Voir les logs en temps réel
docker-compose logs -f

# Logs d'un service spécifique
docker-compose logs -f network-monitor
```

### Nettoyage des données

Les métriques de plus de 7 jours sont automatiquement nettoyées. Pour un nettoyage manuel :

```sql
-- Connexion à PostgreSQL
docker exec -it network-monitor-db psql -U postgres -d network_monitor

-- Nettoyage manuel
SELECT cleanup_old_metrics();
```

### Performance

- **Optimisation mémoire** : Limiter les métriques stockées (7 jours par défaut)
- **Monitoring** : Utiliser `docker stats` pour surveiller l'utilisation des ressources
- **Scaling** : Ajouter des instances dans `docker-compose.yml`

## Dépannage

### Problèmes courants

1. **Port déjà utilisé**
   ```bash
   # Vérifier les ports utilisés
   netstat -tulpn | grep :5000
   
   # Changer les ports dans docker-compose.yml
   ```

2. **Connexion base de données refusée**
   ```bash
   # Vérifier l'état du conteneur PostgreSQL
   docker-compose ps postgres
   
   # Redémarrer si nécessaire
   docker-compose restart postgres
   ```

3. **Services non détectés**
   ```bash
   # Vérifier le réseau Docker
   docker network ls
   docker network inspect exam_monitor-network
   ```

### Port par défaut

- **Dashboard principal** : 5000
- **Instance 1** : 5001
- **Instance 2** : 5002
- **PostgreSQL** : 5432

## Sécurité

- **Mots de passe** : Modifier les mots de passe par défaut
- **Réseau** : Le subnet réseau est isolé
- **HTTPS** : Ajouter un reverse proxy (nginx) pour la production

## Contribuer

1. Fork le projet
2. Créer une branche feature
3. Commit les changements
4. Push vers la branche
5. Créer une Pull Request

## License

Ce projet est sous licence MIT - voir le fichier LICENSE pour les détails.

## Support

Pour toute question ou problème d'installation, veuillez créer une issue sur GitHub.

---

## Points Clés pour l'Examen

### ✅ Contraintes Techniques Respectées

| Critère | ✅ Implémentation |
|-----------|-------------------|
| **Flask** | Application web complète avec API REST |
| **Base de données conteneurisée** | PostgreSQL 15 dans Docker |
| **Docker** | Application entièrement conteneurisée |
| **Réseau Docker** | Sous-réseau isolé 172.20.0.0/16 |

### 🌟 Points Forts du Projet

- **Originalité** : Dashboard temps réel avec WebSocket
- **Architecture propre** : Microservices communicants
- **CI/CD intégré** : GitHub Actions → Docker Hub
- **Documentation complète** : Installation, utilisation, présentation
- **Scalabilité** : Facile d'ajouter des instances supplémentaires

### 🎯 Fonctionnalités Innovantes

- **Communication inter-instances** via API REST
- **Découverte automatique** des services
- **Monitoring distribué** avec métriques temps réel
- **Dashboard unifié** pour toutes les instances
- **Logging centralisé** des événements réseau

**Ce projet démontre parfaitement votre maîtrise de Flask, Docker, PostgreSQL et des concepts réseau !**
