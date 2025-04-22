# Projet Tic Tac Toe en Ligne avec Agent DRL

Ce projet a été réalisé dans le cadre du cours "Fondement des Réseaux" à l'École Supérieure d'Économie Numérique (ESEN), Université de la Manouba (A.U 2024-2025).

## Objectif

L'objectif est de développer un jeu de Tic Tac Toe (Morpion) en ligne jouable en réseau, intégrant une intelligence artificielle (IA) basée sur l'apprentissage par renforcement profond (Deep Reinforcement Learning - DRL) comme l'un des joueurs possibles. Le projet combine des concepts de communication réseau (via `asyncio`) et d'IA (via `stable-baselines3` et `gymnasium`).

## Fonctionnalités

*   **Jeu Local (Test Initial):** Un mode pour tester la logique du jeu entre deux humains sur la même machine (non inclus dans le menu principal final).
*   **Joueur contre Joueur (LAN):** Permet à deux joueurs humains sur le même réseau local de jouer l'un contre l'autre.
*   **Joueur contre IA:** Permet à un joueur humain de jouer contre une IA entraînée (un agent PPO entraîné pour ~1 million de timesteps).
*   **Menu de Lancement:** Un script principal (`run_game.py`) offre un menu pour lancer facilement les différents modes de jeu.

## Prérequis

*   Python 3.9+
*   `pip` (gestionnaire de paquets Python)
*   Git (pour cloner le dépôt, optionnel si vous téléchargez le code)

## Installation

1.  **Cloner le dépôt (si applicable):**
    ```bash
    git clone https://github.com/Strategic-minds/tic-tac-toe.git
    cd tic-tac-toe # Ex: cd tic-tac-toe
    ```
    Ou téléchargez et extrayez le code source dans un dossier.

2.  **Naviguer vers le dossier du projet:**
    Ouvrez un terminal ou une invite de commande et déplacez-vous dans le dossier racine du projet.
    ```bash
    cd chemin/vers/le/dossier/tic-tac-toe
    ```

3.  **Créer un environnement virtuel (Recommandé):**
    ```bash
    python -m venv .venv
    ```
    (Utilisez `python3` si `python` ne fonctionne pas sur macOS/Linux)

4.  **Activer l'environnement virtuel:**
    *   **Windows (cmd/powershell):** `.\.venv\Scripts\activate`
    *   **macOS/Linux (bash/zsh):** `source .venv/bin/activate`
    Votre invite de commande devrait maintenant afficher `(.venv)` au début.

5.  **Installer les dépendances:**
    ```bash
    pip install -r requirements.txt
    ```

## Lancer le Jeu

Utilisez le script `run_game.py` depuis le dossier racine du projet (assurez-vous que l'environnement virtuel est activé).

```bash
python run_game.py

Cela affichera le menu principal :
--- Tic Tac Toe Menu ---
1. Play vs AI (Runs Server, AI Client, Human Client)
2. Host LAN Game (Starts Server only, plus your client)
3. Join LAN Game (Connects as Human Client)
4. Quit
------------------------
Enter your choice (1-4):

Explication des Options:
Option 1: Jouer contre l'IA
Lance automatiquement le serveur en arrière-plan.
Lance le client IA (ai_client.py) qui se connectera en premier (sera Joueur X).
Après une courte pause (pour laisser l'IA charger), lance votre client humain (client.py) qui se connectera en second (sera Joueur O).
Deux fenêtres Pygame apparaîtront (une pour l'IA, une pour vous). Jouez dans votre fenêtre lorsque c'est votre tour.
Option 2: Héberger une partie en LAN
Lance le serveur en arrière-plan.
Affiche votre adresse IP locale approximative. Communiquez cette adresse IP à l'autre joueur.
Lance automatiquement votre client humain (client.py) qui se connecte à votre propre serveur (via 127.0.0.1).
Votre fenêtre Pygame s'ouvrira et attendra qu'un autre joueur rejoigne.
Important: Le pare-feu de votre ordinateur (celui qui héberge) doit autoriser les connexions entrantes sur le port TCP 8888 pour que l'autre joueur puisse se connecter.
Option 3: Rejoindre une partie en LAN
Demande l'adresse IP de la personne qui a choisi l'Option 2 (l'hôte).
Entrez l'adresse IP fournie par l'hôte.
Lance votre client humain (client.py) qui tente de se connecter au serveur de l'hôte.
Si la connexion réussit, le jeu commence.
Option 4: Quitter
Ferme le menu. Notez que les processus serveur/client lancés en arrière-plan pourraient ne pas se fermer automatiquement. Fermez les fenêtres Pygame et arrêtez manuellement le serveur (Ctrl+C dans son terminal s'il est visible, ou via le gestionnaire de tâches) si nécessaire.
Structure du Projet
tic-tac-toe/
├── .venv/              # Environnement virtuel (ignoré par Git)
├── models/             # Modèles IA entraînés (.zip) - (Ou dans src/models/)
│   └── tictactoe_ppo_1M.zip
├── src/                # Code source principal
│   ├── __init__.py
│   ├── ai_client.py    # Client pour l'IA (charge le modèle PPO)
│   ├── client.py       # Client pour le joueur humain
│   ├── server.py       # Serveur central du jeu (asyncio)
│   ├── tic_tac_toe_env.py # Environnement Gym/Gymnasium pour l'entraînement IA
│   ├── tic_tac_toe_logic.py # Logique de base du jeu Tic Tac Toe
│   └── train_powerful_agent.py # Script pour entraîner l'agent PPO (optionnel à exécuter)
├── tests/              # Tests unitaires (principalement pour la logique)
│   ├── __init__.py
│   └── test_tic_tac_toe_logic.py
├── .gitignore          # Fichiers ignorés par Git
├── README.md           # Ce fichier
├── requirements.txt    # Liste des dépendances Python
└── run_game.py         # Script principal du menu de lancement