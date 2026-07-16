# Epic Events CRM

---

## Présentation

Epic Events est une application CRM sécurisée en ligne de commande développée avec Python.

Elle permet aux équipes **gestion**, **commerciale** et **support** de gérer les collaborateurs, les clients, les contrats et les événements de l’entreprise selon des permissions précises.

Le projet met en œuvre :

- une base de données relationnelle SQLite ;
- l’ORM Peewee ;
- une interface en ligne de commande avec Typer ;
- une authentification sécurisée ;
- des autorisations par rôle ;
- le principe du moindre privilège ;
- la journalisation des erreurs avec Sentry ;
- des tests unitaires, d’intégration et fonctionnels.

---

## Fonctionnalités

### Collaborateurs

- Création du premier compte de gestion
- Authentification par email et mot de passe
- Création de comptes collaborateurs
- Mise à jour des collaborateurs
- Désactivation logique des comptes
- Attribution d’un département :
  - `MANAGEMENT`
  - `COMMERCIAL`
  - `SUPPORT`

### Clients

- Création d’un client par un commercial
- Association automatique du client au commercial connecté
- Lecture des clients par tous les collaborateurs actifs
- Mise à jour d’un client uniquement par son commercial responsable

### Contrats

- Création d’un contrat par la gestion
- Association du contrat au client et à son commercial
- Lecture des contrats par tous les collaborateurs actifs
- Mise à jour :
  - par la gestion pour tous les contrats ;
  - par le commercial pour les contrats de ses propres clients
- Filtrage des contrats :
  - non signés ;
  - non entièrement payés

### Événements

- Création d’un événement par le commercial responsable
- Création autorisée uniquement pour un contrat signé
- Lecture des événements par tous les collaborateurs actifs
- Liste des événements sans support affecté
- Affectation d’un collaborateur support par la gestion
- Liste des événements attribués au support connecté
- Mise à jour d’un événement uniquement par le support affecté

### Sécurité et supervision

- Hachage des mots de passe avec Passlib et bcrypt
- Saisie masquée des mots de passe
- Permissions appliquées dans la couche service
- Requêtes paramétrées via Peewee
- Validation des données avant enregistrement
- Variables sensibles exclues du dépôt Git
- Journalisation des exceptions inattendues avec Sentry

---

## Architecture

L’application suit une architecture en couches :

```text
Utilisateur
    |
    v
CLI Typer
src/main.py
    |
    +--> Authentification et autorisation
    |    src/auth.py
    |
    +--> Services métier
         src/services/
              |
              v
         Modèles Peewee
         src/models/
              |
              v
         Base SQLite

Exceptions inattendues
    |
    v
src/monitoring.py
    |
    v
Sentry
```

Le diagramme des relations est disponible dans :

```text
docs/architecture/diagramme-des-relations.png
```

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
│   │   ├── architecture-summary-fr.md
│   │   ├── architecture-summary-en.md
│   │   ├── EpicEvents-architecture-technique.pdf
│   │   └── diagramme-des-relations.png
│   ├── decisions/
│   ├── journal/
│   └── uml/
├── src/
│   ├── __init__.py
│   ├── auth.py
│   ├── config.py
│   ├── database.py
│   ├── main.py
│   ├── monitoring.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── client.py
│   │   ├── contract.py
│   │   └── event.py
│   └── services/
│       ├── __init__.py
│       ├── user_service.py
│       ├── client_service.py
│       ├── contract_service.py
│       └── event_service.py
└── tests/
    ├── conftest.py
    ├── unit/
    │   └── test_monitoring.py
    ├── integration/
    │   ├── test_auth.py
    │   ├── test_client_service.py
    │   ├── test_contract_service.py
    │   ├── test_database.py
    │   ├── test_event_service.py
    │   └── test_user_service.py
    └── functional/
        └── test_cli.py
```

---

## Prérequis

- Python 3.9 ou version supérieure
- Git
- Un terminal compatible
- Un compte Sentry facultatif pour tester la supervision

Version utilisée pendant le développement :

```text
Python 3.12.2
```

---

## Installation

### 1. Cloner le dépôt

```bash
git clone https://github.com/AlNocquet/OC-Projet12-EpicEvents.git
cd OC-Projet12-EpicEvents
```

### 2. Créer un environnement virtuel

```bash
python -m venv venv
```

### 3. Activer l’environnement virtuel

Git Bash sous Windows :

```bash
source venv/Scripts/activate
```

PowerShell sous Windows :

```powershell
.\venv\Scripts\Activate.ps1
```

macOS ou Linux :

```bash
source venv/bin/activate
```

### 4. Installer les dépendances

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

---

## Initialisation de la base de données

Créer les tables :

```bash
python -m src.main initialize-database
```

Résultat attendu :

```text
Database initialized successfully.
```

Créer le premier compte de gestion :

```bash
python -m src.main create-initial-management-user-command \
  "Morgan Manager" \
  manager@epicevents.com
```

Le mot de passe est demandé et confirmé dans un prompt masqué.

---

## Utilisation

Afficher les commandes disponibles :

```bash
python -m src.main --help
```

Afficher l’aide d’une commande :

```bash
python -m src.main create-client-command --help
```

### Authentification

```bash
python -m src.main authenticate-user-command manager@epicevents.com
```

### Gestion des collaborateurs

Créer un collaborateur :

```bash
python -m src.main create-user-account-command \
  manager@epicevents.com \
  "Camille Martin" \
  camille@epicevents.com \
  COMMERCIAL
```

Mettre à jour un collaborateur :

```bash
python -m src.main update-user-account-command \
  manager@epicevents.com \
  2 \
  "Camille Dupont" \
  camille.dupont@epicevents.com \
  COMMERCIAL
```

Désactiver un collaborateur :

```bash
python -m src.main delete-user-account-command \
  manager@epicevents.com \
  2
```

### Gestion des clients

Créer un client :

```bash
python -m src.main create-client-command \
  camille@epicevents.com \
  "Kevin Casey" \
  kevin@startup.io \
  "+33 6 12 34 56 78" \
  "Cool Startup LLC"
```

Lister les clients :

```bash
python -m src.main list-clients-command manager@epicevents.com
```

Mettre à jour un client :

```bash
python -m src.main update-client-command \
  camille@epicevents.com \
  1 \
  "Kevin Casey" \
  kevin@startup.io \
  "+33 6 98 76 54 32" \
  "Cool Startup LLC"
```

### Gestion des contrats

Créer un contrat :

```bash
python -m src.main create-contract-command \
  manager@epicevents.com \
  1 \
  10000.00 \
  4000.00 \
  true
```

Lister les contrats :

```bash
python -m src.main list-contracts-command manager@epicevents.com
```

Lister les contrats non signés :

```bash
python -m src.main list-unsigned-contracts-command camille@epicevents.com
```

Lister les contrats non entièrement payés :

```bash
python -m src.main list-unpaid-contracts-command camille@epicevents.com
```

Mettre à jour un contrat :

```bash
python -m src.main update-contract-command \
  manager@epicevents.com \
  1 \
  10000.00 \
  0.00 \
  true
```

### Gestion des événements

Créer un événement :

```bash
python -m src.main create-event-command \
  camille@epicevents.com \
  1 \
  "Conférence annuelle" \
  "Paris" \
  100 \
  "2026-09-10T14:00" \
  "2026-09-10T18:00" \
  "Accueil à partir de 13 h 30."
```

Lister tous les événements :

```bash
python -m src.main list-events-command manager@epicevents.com
```

Lister les événements sans support :

```bash
python -m src.main list-unassigned-events-command manager@epicevents.com
```

Affecter un support :

```bash
python -m src.main assign-support-to-event-command \
  manager@epicevents.com \
  1 \
  3
```

Lister les événements du support connecté :

```bash
python -m src.main list-my-events-command support@epicevents.com
```

Mettre à jour un événement attribué :

```bash
python -m src.main update-event-command \
  support@epicevents.com \
  1 \
  "Conférence annuelle" \
  "Paris - Salle Horizon" \
  110 \
  "2026-09-10T14:00" \
  "2026-09-10T18:30" \
  "Accueil à 13 h 30 et contrôle du matériel."
```

---

## Permissions

| Action | Gestion | Commercial | Support |
|---|:---:|:---:|:---:|
| Lire les clients, contrats et événements | Oui | Oui | Oui |
| Créer, modifier ou désactiver un collaborateur | Oui | Non | Non |
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

## Configuration Sentry

Aucun DSN réel ne doit être enregistré dans le dépôt.

Variables d’environnement :

```text
SENTRY_DSN
SENTRY_ENVIRONMENT
```

Git Bash :

```bash
export SENTRY_DSN="votre-dsn-sentry"
export SENTRY_ENVIRONMENT="development"

python -m src.main test-sentry-command manager@epicevents.com
```

PowerShell :

```powershell
$env:SENTRY_DSN="votre-dsn-sentry"
$env:SENTRY_ENVIRONMENT="development"

python -m src.main test-sentry-command manager@epicevents.com
```

Exception de démonstration attendue :

```text
Epic Events controlled Sentry demonstration error.
```

---

## Tests

La suite est organisée en trois catégories.

### Tests unitaires

```bash
python -m pytest tests/unit -v
```

Résultat validé :

```text
4 tests réussis
```

### Tests d’intégration

```bash
python -m pytest tests/integration -v
```

Résultat validé :

```text
134 tests réussis
```

### Tests fonctionnels

```bash
python -m pytest tests/functional -v
```

Résultat validé :

```text
9 tests réussis
```

### Suite complète

```bash
python -m pytest -v
```

Résultat validé :

```text
147 tests réussis
0 échec
```

---

## Couverture

Générer le rapport de couverture :

```bash
python -m pytest \
  --cov=src \
  --cov-report=term-missing \
  --cov-report=html
```

Résultat validé :

```text
TOTAL 76%
Coverage HTML written to dir htmlcov
```

Le rapport HTML est disponible dans :

```text
htmlcov/index.html
```

---

## Sécurité

- Mots de passe hachés avec Passlib et bcrypt
- Mots de passe saisis dans un prompt masqué
- Comptes inactifs refusés à l’authentification
- Permissions appliquées selon le rôle, la propriété ou l’affectation
- Validation des montants, dates, emails et champs obligatoires
- Requêtes paramétrées par Peewee
- Désactivation logique des collaborateurs
- Base locale, fichiers `.env` et rapports générés exclus du dépôt
- Données personnelles désactivées par défaut dans Sentry
- Tests exécutés sur une base SQLite en mémoire

---

## Documentation

- `docs/architecture/architecture-summary-fr.md`
- `docs/architecture/architecture-summary-en.md`
- `docs/architecture/EpicEvents-architecture-technique.pdf`
- `docs/architecture/diagramme-des-relations.png`

Les décisions techniques, journaux de développement et versions UML sont disponibles dans les autres sous-dossiers de `docs/`.

---

## Auteur

Alice Nocquet
