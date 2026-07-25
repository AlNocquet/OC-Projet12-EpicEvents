# Epic Events CRM

## Présentation

Epic Events est une application CRM sécurisée en ligne de commande développée avec Python.

Elle permet aux équipes **gestion**, **commerciale** et **support** de gérer les collaborateurs, les clients, les contrats et les événements de l’entreprise selon des permissions précises.

Le projet met en œuvre :

- une base de données relationnelle SQLite ;
- l’ORM Peewee ;
- une interface en ligne de commande avec Typer ;
- des mots de passe hachés avec bcrypt ;
- une authentification par session JWT ;
- des autorisations par rôle, propriété et affectation ;
- le principe du moindre privilège ;
- la journalisation des erreurs avec Sentry ;
- des tests unitaires, d’intégration et fonctionnels.

---

## Fonctionnalités

### Collaborateurs

- Création du premier compte de gestion
- Connexion par email et mot de passe
- Création d’une session JWT locale après authentification
- Déconnexion et suppression de la session locale
- Création de comptes collaborateurs
- Mise à jour des collaborateurs
- Désactivation logique des comptes afin de préserver les données CRM liées
- Attribution d’un département :
  - `MANAGEMENT`
  - `COMMERCIAL`
  - `SUPPORT`
- Protection du compte de gestion connecté :
  - il ne peut pas se désactiver lui-même ;
  - il ne peut pas retirer son propre département `MANAGEMENT`

### Clients

- Création d’un client par un commercial
- Association automatique du client au commercial connecté
- Lecture des clients par tous les collaborateurs actifs
- Mise à jour d’un client uniquement par son commercial responsable
- Conservation des clients lorsqu’un collaborateur est désactivé

### Contrats

- Création d’un contrat par la gestion
- Association automatique au client et au commercial responsable du client
- Lecture des contrats par tous les collaborateurs actifs
- Mise à jour :
  - par la gestion pour tous les contrats ;
  - par un commercial pour les contrats de ses propres clients
- Filtrage des contrats :
  - non signés ;
  - non entièrement payés
- Validation du montant total et du montant restant à payer

### Événements

- Création d’un événement par le commercial responsable du client
- Création autorisée uniquement pour un contrat signé
- Lecture des événements par tous les collaborateurs actifs
- Liste des événements sans support affecté
- Affectation d’un collaborateur support actif par la gestion
- Liste des événements attribués au support connecté
- Mise à jour d’un événement uniquement par le support affecté
- Validation des dates, du nombre de participants et des champs obligatoires

### Sécurité et supervision

- Hachage des mots de passe avec Passlib et bcrypt
- Saisie masquée des mots de passe
- JWT signé avec l’algorithme HS256
- Expiration du JWT après 60 minutes
- Session locale enregistrée dans `.epic_events_token.json`
- Rechargement de l’utilisateur depuis SQLite à chaque commande protégée
- Refus immédiat d’un compte désactivé ou supprimé, même avec un JWT encore valide
- Permissions appliquées dans la couche service
- Requêtes paramétrées via Peewee
- Validation des données avant enregistrement
- Secrets, base locale et token exclus du dépôt Git
- Journalisation des exceptions inattendues avec Sentry

---

## Architecture

L’application suit une architecture en couches.

```text
Utilisateur
    |
    v
python -m src
    |
    v
src/__main__.py
    |
    +--> src/cli/
    |      auth.py
    |      user.py
    |      client.py
    |      contract.py
    |      event.py
    |      monitoring.py
    |      common.py
    |
    +--> src/core/
    |      auth.py
    |      jwt_auth.py
    |      config.py
    |      database.py
    |      monitoring.py
    |
    +--> src/services/
    |      user_service.py
    |      client_service.py
    |      contract_service.py
    |      event_service.py
    |
    +--> src/models/
           user.py
           client.py
           contract.py
           event.py
               |
               v
          SQLite / epic_events.db
```

### Responsabilités des couches

| Couche | Responsabilité |
|---|---|
| `src/__main__.py` | Compose l’application Typer, initialise Sentry et intercepte les erreurs inattendues |
| `src/cli/` | Collecte les arguments, affiche les résultats et transforme les erreurs attendues en sorties CLI |
| `src/core/auth.py` | Vérifie l’email, le mot de passe bcrypt et les départements autorisés |
| `src/core/jwt_auth.py` | Crée, signe, valide, charge, enregistre et supprime les JWT |
| `src/core/config.py` | Centralise les chemins et les variables d’environnement |
| `src/services/` | Applique les règles métier, les permissions, la propriété et les affectations |
| `src/models/` | Définit les entités Peewee et leurs relations |
| SQLite | Stocke les collaborateurs, clients, contrats et événements |
| Sentry | Reçoit les exceptions inattendues et l’exception contrôlée de démonstration |

### Flux d’authentification JWT

```text
auth login EMAIL
    |
    +--> mot de passe saisi dans un prompt masqué
    +--> vérification bcrypt dans SQLite
    +--> création d’un JWT signé HS256
    +--> expiration fixée à 60 minutes
    +--> enregistrement dans .epic_events_token.json
```

Pour chaque commande protégée :

```text
commande CLI
    |
    +--> chargement du token local
    +--> validation de la signature et de l’expiration
    +--> lecture de l’identifiant utilisateur dans la claim sub
    +--> rechargement de l’utilisateur depuis SQLite
    +--> contrôle de l’existence et de l’état actif du compte
    +--> autorisation finale dans la couche service
```

Le département contenu dans le JWT n’est pas utilisé comme source d’autorisation. La base SQLite et la couche service restent les sources de vérité.

---

## Structure du projet

```text
OC-Projet12-EpicEvents/
├── .env.example
├── .gitignore
├── README.md
├── README_EN.md
├── requirements.txt
├── docs/
│   ├── architecture/
│   ├── decisions/
│   │   ├── ADR-007-test-suite-organization.md
│   │   ├── ADR-008-cli-application-package-reorganization.md
│   │   └── ADR-009-jwt-authentication-and-local-session.md
│   ├── journal/
│   │   ├── Day-07.md
│   │   ├── Day-08.md
│   │   └── Day-09.md
│   └── uml/
│       ├── UML-v0.9.md
│       ├── UML-v1.0.md
│       └── UML-v1.1.md
├── src/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── client.py
│   │   ├── common.py
│   │   ├── contract.py
│   │   ├── event.py
│   │   ├── monitoring.py
│   │   └── user.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── jwt_auth.py
│   │   └── monitoring.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── client.py
│   │   ├── contract.py
│   │   ├── event.py
│   │   └── user.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── client_service.py
│   │   ├── contract_service.py
│   │   ├── event_service.py
│   │   └── user_service.py
│   └── utils/
│       ├── __init__.py
│       ├── create_db.py
│       └── create_user.py
└── tests/
    ├── conftest.py
    ├── functional/
    │   └── test_cli.py
    ├── integration/
    │   ├── test_auth.py
    │   ├── test_client_service.py
    │   ├── test_contract_service.py
    │   ├── test_database.py
    │   ├── test_event_service.py
    │   ├── test_jwt_auth.py
    │   └── test_user_service.py
    └── unit/
        └── test_monitoring.py
```

Les noms des anciens journaux ou UML peuvent légèrement différer dans le dépôt selon leur nom historique. Les versions les plus récentes sont Day 09, ADR-009 et UML v1.1.

---

## Prérequis

- Python 3.9 ou version supérieure
- Git
- PowerShell, un terminal macOS/Linux ou un terminal compatible
- Un compte Sentry facultatif pour tester la supervision

Version utilisée pendant le développement :

```text
Python 3.12.2
```

---

## Installation dans un environnement vierge

### 1. Cloner le dépôt

```powershell
git clone https://github.com/AlNocquet/OC-Projet12-EpicEvents.git
cd OC-Projet12-EpicEvents
```

### 2. Créer un environnement virtuel

```powershell
python -m venv venv
```

### 3. Activer l’environnement virtuel

PowerShell sous Windows :

```powershell
.\venv\Scripts\Activate.ps1
```

Invite de commandes Windows :

```bat
venv\Scripts\activate.bat
```

macOS ou Linux :

```bash
source venv/bin/activate
```

### 4. Installer les dépendances

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 5. Créer le fichier `.env`

PowerShell :

```powershell
Copy-Item .env.example .env
```

macOS ou Linux :

```bash
cp .env.example .env
```

Générer une clé JWT aléatoire :

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Copier la valeur générée dans `.env` :

```text
SENTRY_DSN=
SENTRY_ENVIRONMENT=development
JWT_SECRET_KEY=COLLER_ICI_LA_CLE_GENEREE
```

Règles importantes :

- ne jamais publier la vraie valeur de `JWT_SECRET_KEY` ;
- ne jamais publier un vrai `SENTRY_DSN` ;
- ne jamais ajouter `.env` à Git ;
- utiliser une clé JWT longue et aléatoire.

Sentry est facultatif. L’application fonctionne avec un `SENTRY_DSN` vide, mais la commande de démonstration Sentry nécessite un DSN valide.

### 6. Créer la base de données

```powershell
python -m src.utils.create_db
```

Résultat attendu :

```text
Database initialized successfully.
```

### 7. Créer le premier compte de gestion

Cette commande fonctionne uniquement lorsque la base ne contient encore aucun collaborateur.

```powershell
python -m src.utils.create_user "Morgan Manager" manager@epicevents.com
```

Le mot de passe est demandé et confirmé dans un prompt masqué.

Résultat attendu :

```text
Initial management user created successfully. User ID: 1.
```

### 8. Vérifier l’installation

```powershell
python -m src --help
```

Les groupes suivants doivent apparaître :

```text
auth
user
client
contract
event
monitoring
```

---

## Utilisation

### Principe général

1. Se connecter une seule fois avec `auth login`.
2. Exécuter les commandes métier sans ressaisir l’email ni le mot de passe.
3. Se déconnecter avec `auth logout`.

La session expire automatiquement après 60 minutes.

### Afficher l’aide

```powershell
python -m src --help
python -m src auth --help
python -m src user --help
python -m src client --help
python -m src contract --help
python -m src event --help
python -m src monitoring --help
```

Afficher l’aide d’une commande précise :

```powershell
python -m src client create --help
```

---

## Authentification JWT

### Se connecter

```powershell
python -m src auth login manager@epicevents.com
```

Le mot de passe est demandé dans un prompt masqué.

Une connexion réussie crée le fichier local suivant :

```text
.epic_events_token.json
```

Ce fichier contient un token d’accès, pas le mot de passe.

### Vérifier l’accès gestion

```powershell
python -m src auth check-management
```

### Se déconnecter

```powershell
python -m src auth logout
```

La déconnexion supprime le fichier local de session.

### Commande protégée sans session

Lorsqu’aucun token n’est disponible, l’application répond :

```text
No authentication token found. Please log in.
```

---

## Gestion des collaborateurs

Connexion requise : collaborateur `MANAGEMENT`.

### Créer un collaborateur

```powershell
python -m src user create "Camille Martin" camille@epicevents.com COMMERCIAL
```

Le nouveau mot de passe est demandé et confirmé dans un prompt masqué.

### Mettre à jour un collaborateur

```powershell
python -m src user update 2 "Camille Dupont" camille.dupont@epicevents.com COMMERCIAL
```

### Désactiver un collaborateur

```powershell
python -m src user delete 2
```

La suppression est logique : le compte devient inactif, mais ses clients, contrats et événements restent dans le CRM.

---

## Gestion des clients

### Créer un client

Connexion requise : collaborateur `COMMERCIAL`.

```powershell
python -m src client create "Kevin Casey" kevin@startup.io "+33 6 12 34 56 78" "Cool Startup LLC"
```

Le client est automatiquement associé au commercial connecté.

### Lister les clients

Connexion requise : tout collaborateur actif.

```powershell
python -m src client list
```

### Mettre à jour un client

Connexion requise : commercial responsable du client.

```powershell
python -m src client update 1 "Kevin Casey" kevin@startup.io "+33 6 98 76 54 32" "Cool Startup LLC"
```

---

## Gestion des contrats

### Créer un contrat

Connexion requise : collaborateur `MANAGEMENT`.

```powershell
python -m src contract create 1 10000.00 4000.00 true
```

Ordre des arguments :

```text
CLIENT_ID TOTAL_AMOUNT AMOUNT_DUE IS_SIGNED
```

### Lister les contrats

Connexion requise : tout collaborateur actif.

```powershell
python -m src contract list
```

### Lister les contrats non signés

Connexion requise : collaborateur `COMMERCIAL`.

```powershell
python -m src contract list-unsigned
```

### Lister les contrats non entièrement payés

Connexion requise : collaborateur `COMMERCIAL`.

```powershell
python -m src contract list-unpaid
```

### Mettre à jour un contrat

Connexion requise :

- gestion pour tous les contrats ;
- commercial pour les contrats de ses propres clients.

```powershell
python -m src contract update 1 10000.00 0.00 true
```

Ordre des arguments :

```text
CONTRACT_ID TOTAL_AMOUNT AMOUNT_DUE IS_SIGNED
```

---

## Gestion des événements

Les dates utilisent le format ISO suivant :

```text
YYYY-MM-DDTHH:MM
```

### Créer un événement

Connexion requise : commercial responsable du client lié à un contrat signé.

```powershell
python -m src event create 1 "Conférence annuelle" "Paris" 100 "2026-09-10T14:00" "2026-09-10T18:00" "Accueil à partir de 13 h 30."
```

Ordre des arguments :

```text
CONTRACT_ID EVENT_NAME LOCATION ATTENDEES EVENT_START EVENT_END [NOTES]
```

### Lister tous les événements

Connexion requise : tout collaborateur actif.

```powershell
python -m src event list
```

### Lister les événements sans support affecté

Connexion requise : collaborateur `MANAGEMENT`.

```powershell
python -m src event list-unassigned
```

### Affecter un support à un événement

Connexion requise : collaborateur `MANAGEMENT`.

```powershell
python -m src event assign-support 1 3
```

Ordre des arguments :

```text
EVENT_ID SUPPORT_USER_ID
```

### Lister les événements du support connecté

Connexion requise : collaborateur `SUPPORT`.

```powershell
python -m src event list-mine
```

### Mettre à jour un événement attribué

Connexion requise : support affecté à l’événement.

```powershell
python -m src event update 1 "Conférence annuelle" "Paris - Salle Horizon" 110 "2026-09-10T14:00" "2026-09-10T18:30" "Accueil à 13 h 30 et contrôle du matériel."
```

Ordre des arguments :

```text
EVENT_ID EVENT_NAME LOCATION ATTENDEES EVENT_START EVENT_END [NOTES]
```

---

## Permissions

| Action | Gestion | Commercial | Support |
|---|:---:|:---:|:---:|
| Lire les clients, contrats et événements | Oui | Oui | Oui |
| Créer, modifier ou désactiver un collaborateur | Oui | Non | Non |
| Se désactiver soi-même | Non | Non | Non |
| Créer un client | Non | Oui | Non |
| Modifier un client | Non | Ses clients | Non |
| Créer un contrat | Oui | Non | Non |
| Modifier un contrat | Tous | Contrats de ses clients | Non |
| Filtrer les contrats non signés ou non payés | Non | Oui | Non |
| Créer un événement | Non | Client propre et contrat signé | Non |
| Voir les événements sans support | Oui | Non | Non |
| Affecter un support | Oui | Non | Non |
| Voir ses événements attribués | Non | Non | Oui |
| Modifier un événement | Non | Non | Événements attribués |
| Envoyer l’exception de démonstration Sentry | Oui | Non | Non |

---

## Configuration et démonstration Sentry

Aucun DSN réel ne doit être enregistré dans le dépôt.

Variables du fichier `.env` :

```text
SENTRY_DSN
SENTRY_ENVIRONMENT
```

Exemple :

```text
SENTRY_DSN=VOTRE_DSN_SENTRY
SENTRY_ENVIRONMENT=development
JWT_SECRET_KEY=VOTRE_CLE_JWT
```

Après avoir ajouté un DSN valide et s’être connecté avec un compte de gestion :

```powershell
python -m src monitoring test-sentry
```

Exception contrôlée envoyée :

```text
Epic Events controlled Sentry demonstration error.
```

Résultat CLI attendu :

```text
Sentry test exception sent successfully. Event ID: <event-id>.
```

Si aucun DSN n’est configuré :

```text
Sentry is not configured. Set the SENTRY_DSN environment variable.
```

---

## Tests

La suite est organisée en trois catégories.

### Tests unitaires

```powershell
python -m pytest tests/unit -v
```

Résultat validé :

```text
4 tests réussis
```

### Tests d’intégration

```powershell
python -m pytest tests/integration -v
```

Résultat validé :

```text
143 tests réussis
```

Ces tests couvrent notamment les services métier, l’authentification, la base et le moteur JWT.

### Tests fonctionnels

```powershell
python -m pytest tests/functional -v
```

Résultat validé :

```text
9 tests réussis
```

### Suite complète

```powershell
python -m pytest -q
```

Résultat validé :

```text
156 tests réussis
0 échec
```

---

## Couverture

Générer le rapport de couverture dans le terminal :

```powershell
python -m pytest --cov=src --cov-report=term-missing
```

Générer également le rapport HTML :

```powershell
python -m pytest --cov=src --cov-report=term-missing --cov-report=html
```

Résultat validé :

```text
TOTAL 77%
src/core/jwt_auth.py 96%
Coverage HTML written to dir htmlcov
```

Le rapport HTML est disponible dans :

```text
htmlcov/index.html
```

---

## Sécurité

- Mots de passe hachés et salés avec bcrypt
- Mots de passe saisis dans des prompts masqués
- JWT signé avec HS256
- Clé JWT lue depuis l’environnement
- Expiration du JWT après 60 minutes
- Token stocké localement sans mot de passe
- Utilisateur rechargé depuis SQLite à chaque commande protégée
- Comptes absents ou inactifs refusés
- Permissions appliquées selon le rôle, la propriété ou l’affectation
- Principe du moindre privilège
- Validation des montants, dates, emails, identifiants et champs obligatoires
- Requêtes paramétrées par Peewee contre les injections SQL
- Désactivation logique des collaborateurs
- Relations protégées par les contraintes de clés étrangères SQLite
- `.env`, `.epic_events_token.json`, la base locale et les rapports générés exclus du dépôt
- Données personnelles désactivées par défaut dans Sentry
- Tests exécutés sur une base SQLite isolée en mémoire
- Secrets et token de test isolés dans des répertoires temporaires

---

## Fichiers locaux à ne jamais publier

```text
.env
.epic_events_token.json
epic_events.db
.coverage
htmlcov/
```

Vérification recommandée avant un commit :

```powershell
git status --short
git ls-files .env .epic_events_token.json epic_events.db
```

La seconde commande ne doit retourner aucun fichier.

---

## Installation propre : contrôle final

Pour valider le projet comme un nouvel utilisateur :

```text
cloner le dépôt
→ créer et activer le venv
→ installer requirements.txt
→ copier .env.example vers .env
→ générer JWT_SECRET_KEY
→ créer les tables
→ créer le premier compte de gestion
→ lancer python -m src --help
→ se connecter avec auth login
→ exécuter une commande protégée
→ se déconnecter avec auth logout
→ lancer les tests
```

---

## Documentation

Documentation actuelle :

- `docs/journal/Day-09.md`
- `docs/decisions/ADR-009-jwt-authentication-and-local-session.md`
- `docs/uml/UML-v1.1.md`

Documents d’architecture et historique :

- `docs/architecture/`
- `docs/decisions/`
- `docs/journal/`
- `docs/uml/`

Les ADR expliquent les décisions techniques. Les journaux retracent la progression. Les versions UML documentent l’évolution de l’architecture et du flux d’authentification.

---

## Auteur

Alice Nocquet
