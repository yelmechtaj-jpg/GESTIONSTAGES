# Documentation technique

## Vue d'ensemble

La plateforme est une application web Symfony 6 pour la gestion des stages EMSI Casablanca. Elle suit une architecture MVC classique :

- Controllers pour les flux HTTP et la sécurité
- Entities pour les données métier
- Repositories pour les requêtes Doctrine
- Services pour les traitements transverses
- Templates Twig pour l'affichage

## Modules fonctionnels

- Authentification et RBAC
- Gestion des offres de stage
- Gestion des candidatures
- Gestion documentaire
- Tableau de bord par rôle
- Planification des soutenances
- Réinitialisation du mot de passe
- Notifications email pour les soutenances

## Modèle de données

Principales entités :

- `User` : comptes, rôles, profil, mot de passe
- `Offer` : offres de stage
- `Application` : candidatures des étudiants
- `Document` : rapports déposés et avis d'encadrants
- `Defense` : soutenances planifiées
- `ResetPasswordRequest` : jetons de réinitialisation de mot de passe

Relations clés :

- Un étudiant peut avoir plusieurs candidatures, documents et soutenances
- Une candidature référence une offre et un étudiant
- Une soutenance référence une candidature, un étudiant et un encadrant
- Un document peut être lié à une candidature

## Sécurité

- Connexion par formulaire Symfony avec CSRF
- Mots de passe hashés
- Accès protégé par rôles
- Flux de réinitialisation de mot de passe avec jeton temporaire

## Configuration

### Variables principales

- `DATABASE_URL` : connexion MySQL
- `MAILER_DSN` : transport email
- `APP_SECRET` : secret Symfony
- `uploads_dir` : dossier de stockage des fichiers déposés

### Commandes utiles

- `php bin/console doctrine:migrations:migrate`
- `php bin/console cache:clear --no-warmup`
- `php bin/console app:defense:send-reminders`

## Fichiers de configuration

- `config/packages/security.yaml` : authentification et accès
- `config/packages/framework.yaml` : framework et mailer
- `config/services.yaml` : paramètres applicatifs
- `public/css/app.css` : styles globaux

## Déploiement local

1. Installer les dépendances Composer
2. Configurer `.env`
3. Lancer les migrations Doctrine
4. Vider le cache
5. Démarrer le serveur web

## Points de vigilance

- Vérifier que le transport mail est adapté à l'environnement
- Vérifier la présence du dossier `public/uploads`
- Exécuter les migrations après toute évolution du schéma
