# Résumé d’architecture — Epic Events CRM

Epic Events est une application CRM en ligne de commande développée en **Python**. Elle repose sur une architecture simple et lisible organisée autour de quatre couches principales :

- **CLI (`src/main.py`)** : point d’entrée utilisateur avec les commandes Typer ;
- **Services (`src/services/`)** : logique métier et contrôles d’accès ;
- **Modèles (`src/models/`)** : entités métier persistées avec Peewee ;
- **Configuration / monitoring** : base de données, variables d’environnement et Sentry.

## Modèle métier
Les principales entités sont :

- **User** : collaborateur avec un département (gestion, commercial, support) ;
- **Client** : client suivi par un commercial ;
- **Contract** : contrat rattaché à un client ;
- **Event** : événement rattaché à un client et géré par un support.

Le schéma relationnel permet notamment de représenter :

- un commercial qui gère plusieurs clients ;
- un client qui possède plusieurs contrats ;
- un client qui possède plusieurs événements.

## Sécurité et permissions
L’application met en œuvre :

- une **authentification sécurisée** avec mot de passe haché ;
- des **permissions par rôle / département** ;
- des validations de saisie sur les données sensibles et métier ;
- une séparation entre interface CLI et logique métier.

## Journalisation et supervision
Les erreurs inattendues peuvent être remontées à **Sentry** via des variables d’environnement (`SENTRY_DSN`, `SENTRY_ENVIRONMENT`) sans exposer les secrets dans le code source.

## Tests
Le projet est validé par une suite de tests organisée en :

- **tests unitaires** ;
- **tests d’intégration** ;
- **tests fonctionnels**.

Cette organisation permet de vérifier la logique applicative, les interactions avec la base et le comportement de la CLI.
