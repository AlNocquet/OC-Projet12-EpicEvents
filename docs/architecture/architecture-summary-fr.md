# Résumé d’architecture - Epic Events CRM

Epic Events est un CRM sécurisé en ligne de commande développé avec Python 3.12. L’application est lancée avec `python -m src` et son architecture sépare clairement la CLI, les fonctions transverses, les services métier et la persistance.

## Architecture actuelle

- **Point d’entrée (`src/__main__.py`)** : compose les groupes Typer avec `app.add_typer`, initialise Sentry et capture les exceptions inattendues.
- **CLI (`src/cli/`)** : groupes `auth`, `user`, `client`, `contract`, `event` et `monitoring`. La CLI collecte les arguments et affiche les réponses ; elle ne porte pas les règles métier.
- **Core (`src/core/`)** : authentification bcrypt, configuration, base SQLite, cycle de vie JWT et supervision Sentry.
- **Services (`src/services/`)** : validations, permissions, propriété des clients et contrats, affectation des événements et principe du moindre privilège.
- **Modèles (`src/models/`)** : entités Peewee `User`, `Client`, `Contract` et `Event`.
- **Utilitaires (`src/utils/`)** : création des tables et du premier compte de gestion.

## Authentification JWT

La commande `python -m src auth login EMAIL` vérifie le mot de passe dans un prompt masqué, crée un JWT signé HS256 valable 60 minutes et l’enregistre dans `.epic_events_token.json`.

Chaque commande protégée :

1. charge et valide le token ;
2. vérifie sa signature et son expiration ;
3. lit l’identifiant dans la claim `sub` ;
4. recharge l’utilisateur depuis SQLite ;
5. refuse un compte absent ou inactif ;
6. délègue l’autorisation à la couche service.

Le département contenu dans le JWT n’est donc pas la source de vérité des permissions.

## Modèle relationnel

- un `User` commercial peut être responsable de plusieurs `Client` et `Contract` ;
- un `Client` peut posséder plusieurs `Contract` ;
- un `Contract` peut couvrir plusieurs `Event` ;
- un `Event` peut avoir zéro ou un support, tandis qu’un support peut gérer plusieurs événements ;
- les relations sensibles utilisent `RESTRICT` et le support optionnel utilise `SET NULL` ;
- la désactivation logique d’un collaborateur préserve les données CRM.

## Sécurité

- mots de passe hachés avec Passlib et bcrypt ;
- JWT signé, expirant et secret lu depuis l’environnement ;
- `.env`, `.epic_events_token.json` et `epic_events.db` exclus de Git ;
- requêtes paramétrées par Peewee contre l’injection SQL ;
- permissions selon le département, la propriété et l’affectation ;
- revalidation SQLite à chaque commande ;
- Sentry configuré avec `send_default_pii=False` et `include_local_variables=False`.

## Validation

- **156 tests réussis**, 0 échec ;
- **4 tests unitaires**, **143 tests d’intégration**, **9 tests fonctionnels** ;
- **77 % de couverture globale** ;
- **96 % de couverture pour `src/core/jwt_auth.py`** ;
- base SQLite de test isolée en mémoire et tokens de test stockés dans des répertoires temporaires.

## Commandes principales

```powershell
python -m src.utils.create_db
python -m src.utils.create_user "Morgan Manager" manager@epicevents.com
python -m src auth login manager@epicevents.com
python -m src client list
python -m src monitoring test-sentry
python -m src auth logout
python -m pytest -q
python -m pytest --cov=src --cov-report=term-missing
```
