# Documentation Technique - Tic Tac Toe en Ligne avec Agent DRL

## 1. Introduction

Ce document détaille l'architecture technique et les choix d'implémentation du projet de jeu Tic Tac Toe en ligne avec un agent DRL. L'objectif était de créer un jeu fonctionnel jouable en réseau local (Humain vs Humain, Humain vs IA) en utilisant Python et des bibliothèques modernes pour le réseau et l'IA.

## 2. Structure du Projet

(Vous pouvez inclure ici la même structure de projet que dans le README pour référence)

*   **`run_game.py`**: Point d'entrée principal offrant un menu CLI pour lancer les différents modes via le module `subprocess`.
*   **`src/`**: Contient le cœur logique et fonctionnel de l'application.
    *   **`server.py`**: Implémente le serveur central asynchrone basé sur `asyncio`. Gère les connexions client, le pairage des joueurs, l'état des parties, la validation des coups et la retransmission des mises à jour.
    *   **`client.py`**: Implémente le client pour un joueur humain. Utilise `pygame` pour l'interface graphique et l'interaction utilisateur. Communique avec le serveur via `asyncio` pour envoyer les coups et recevoir les mises à jour. Accepte l'IP du serveur via un argument `--host`.
    *   **`ai_client.py`**: Implémente le client pour l'agent IA. Similaire au client humain pour le réseau et l'affichage, mais charge un modèle DRL pré-entraîné (`PPO` de Stable Baselines 3) pour décider des coups. Inclut une étape cruciale de canonicalisation de l'observation.
    *   **`tic_tac_toe_logic.py`**: Module contenant la logique pure du jeu Tic Tac Toe (état du plateau, actions valides, vérification de victoire/nul, application d'un coup). Indépendant du réseau ou de l'IA.
    *   **`tic_tac_toe_env.py`**: Définit l'environnement personnalisé compatible `gymnasium` pour l'entraînement de l'agent RL. Il encapsule la logique du jeu et définit les espaces d'observation/action et la fonction de récompense. L'adversaire dans cet environnement est codé pour jouer aléatoirement.
    *   **`train_powerful_agent.py`**: Script utilisant `stable-baselines3` pour entraîner l'agent (modèle PPO) en utilisant l'environnement `TicTacToeEnv`. Sauvegarde le modèle entraîné.
*   **`models/`**: Répertoire destiné à stocker les fichiers `.zip` des modèles IA entraînés. (Ou `src/models/`)
*   **`tests/`**: Contient les tests unitaires, principalement pour valider `tic_tac_toe_logic.py`.

## 3. Architecture Réseau (Client-Serveur)

Le projet utilise une architecture client-serveur centralisée.

*   **Serveur (`server.py`):**
    *   Basé sur `asyncio` pour gérer efficacement plusieurs connexions concurrentes de manière asynchrone.
    *   Utilise `asyncio.start_server` pour écouter les connexions entrantes sur un port défini (8888).
    *   Gère un état global simple : une liste d'attente (`waiting_clients`) et un dictionnaire des parties actives (`games`).
    *   Lorsqu'un client se connecte, il est mis en attente ou apparié avec un client en attente pour démarrer une partie.
    *   Pour chaque partie, le serveur maintient l'état du plateau (`board`) et le joueur courant (`current_turn`).
    *   Valide les coups reçus des clients (`MAKE_MOVE`) en utilisant `tic_tac_toe_logic.py` et en vérifiant si c'est le bon tour du joueur.
    *   Met à jour l'état du jeu et le diffuse aux deux clients concernés via des messages `STATE_UPDATE` ou `GAME_OVER`.
    *   Gère les déconnexions des clients.

*   **Clients (`client.py`, `ai_client.py`):**
    *   Utilisent `asyncio.open_connection` pour se connecter au serveur à une adresse IP et un port spécifiés.
    *   Chaque client gère deux tâches asynchrones principales :
        *   Une boucle d'écoute (`listen_to_server`) qui reçoit les messages du serveur (JSON) et met à jour l'état local du jeu (plateau, tour, messages).
        *   Une boucle de jeu (`game_loop`) qui gère l'interface `pygame` (affichage, événements) et envoie les messages (`MAKE_MOVE`) au serveur (suite à un clic humain ou une décision de l'IA).
    *   L'état affiché par le client est toujours basé sur les informations reçues du serveur (`STATE_UPDATE`, `GAME_OVER`), garantissant la synchronisation.

*   **Protocole de Communication:**
    *   La communication se fait via des flux TCP gérés par `asyncio`.
    *   Les messages sont des objets JSON encodés en UTF-8.
    *   Chaque message JSON est terminé par un caractère newline (`\n`) pour permettre l'utilisation de `reader.readuntil(b'\n')`.
    *   Types de messages principaux :
        *   `WAITING`: Envoyé par le serveur au premier client connecté.
        *   `GAME_START`: Envoyé par le serveur aux deux clients appariés (contient `player_id`).
        *   `STATE_UPDATE`: Envoyé par le serveur pour diffuser le nouvel état du jeu (contient `board`, `current_turn`).
        *   `MAKE_MOVE`: Envoyé par le client au serveur (contient `cell` index 0-8).
        *   `GAME_OVER`: Envoyé par le serveur à la fin du jeu (contient `winner`, `board`).
        *   `INVALID_MOVE`: Envoyé par le serveur si un coup est refusé (contient `message`).
        *   `OPPONENT_DISCONNECTED`: Envoyé par le serveur à un joueur si l'autre se déconnecte.
        *   `ERROR`: Message d'erreur générique.

## 4. Intelligence Artificielle (DRL)

L'IA est basée sur l'apprentissage par renforcement profond (DRL) via la bibliothèque Stable Baselines 3.

*   **Environnement (`TicTacToeEnv`):**
    *   Classe personnalisée héritant de `gymnasium.Env`.
    *   **Espace d'Observation:** `spaces.Box(0, 2, shape=(9,), dtype=np.int8)`. Représente le plateau 3x3 aplati, avec 0 (vide), 1 (Agent/X), 2 (Opposant/O).
    *   **Espace d'Action:** `spaces.Discrete(9)`. Représente le choix d'une des 9 cases (index 0 à 8).
    *   **Fonction de Récompense:** Simple, donnée à la fin d'un coup agent + coup adversaire :
        *   `+1.0` si l'agent gagne.
        *   `-1.0` si l'adversaire (aléatoire) gagne.
        *   `+0.5` en cas de match nul.
        *   `-10.0` si l'agent tente un coup invalide (pour décourager fortement).
        *   `0.0` pour les étapes intermédiaires.
    *   **Logique de l'Opposant:** L'adversaire dans l'environnement d'entraînement est codé pour choisir un coup valide aléatoire parmi les cases vides. L'agent apprend donc à jouer contre cette stratégie spécifique.
    *   **Agent = Joueur X:** L'agent est toujours le joueur qui commence (Player X / 1) dans l'environnement d'entraînement.

*   **Entraînement (`train_powerful_agent.py`):**
    *   **Algorithme:** PPO (Proximal Policy Optimization) a été choisi pour sa robustesse.
    *   **Bibliothèque:** `stable-baselines3`.
    *   **Durée:** Entraîné pour 1 million de timesteps (`TOTAL_TIMESTEPS = 1_000_000`), ce qui s'est avéré suffisant pour atteindre une performance proche de l'optimale (matchs nuls contre un bon joueur) dans ce contexte.
    *   **Hyperparamètres:** Utilisation des hyperparamètres par défaut de PPO dans SB3, avec une politique `MlpPolicy`.
    *   **Résultat:** Le modèle PPO résultant (`tictactoe_ppo_1M.zip`) joue une stratégie très forte, forçant généralement des matchs nuls contre des joueurs compétents.

*   **Intégration (`ai_client.py`):**
    *   **Chargement:** Le modèle PPO entraîné est chargé au démarrage du client AI via `PPO.load(MODEL_PATH)`.
    *   **Décision:** Lorsque c'est le tour de l'IA, la fonction `get_ai_move` est appelée.
    *   **Canonicalisation:** L'observation actuelle du plateau est récupérée. **Crucialement**, si l'IA s'est vu assigner le rôle de Joueur O (2) par le serveur, l'observation est "canonicalisée" : les identifiants des joueurs (1 et 2) sont inversés dans la copie de l'observation fournie au modèle. Cela permet au modèle, qui a été entraîné uniquement comme Joueur X (1), d'interpréter correctement l'état du jeu depuis sa perspective apprise.
    *   **Prédiction:** `model.predict(canonical_observation, deterministic=True)` est appelé pour obtenir l'action jugée optimale par le modèle.
    *   **Envoi:** L'index de l'action choisie est envoyé au serveur via un message `MAKE_MOVE`.

## 5. Interface Utilisateur

L'interface graphique pour les clients humains et IA est réalisée avec **Pygame**. Elle est responsable de :
*   Afficher la grille de jeu et les pions (X et O).
*   Afficher les messages de statut (tour du joueur, résultat de la partie).
*   Capturer les clics de souris pour le joueur humain.

## 6. Dépendances Clés

*   **Python 3:** Langage principal.
*   **Pygame:** Interface graphique et gestion des événements utilisateur.
*   **Asyncio:** Gestion du réseau asynchrone (client/serveur).
*   **NumPy:** Manipulation efficace des tableaux pour l'état du jeu.
*   **Gymnasium:** Framework standard pour définir l'environnement RL.
*   **Stable Baselines 3:** Bibliothèque DRL pour l'entraînement (PPO) et l'utilisation du modèle.
*   **TensorBoard:** (Dépendance pour SB3) Utilisé pour visualiser les logs d'entraînement (optionnel pour l'utilisateur final).

## 7. Limitations et Améliorations Possibles

*   **Robustesse du Réseau:** La gestion des erreurs réseau (déconnexions soudaines, latence) pourrait être améliorée.
*   **Force de l'IA:** Bien que forte, l'IA a été entraînée uniquement contre un adversaire aléatoire. L'implémentation du self-play pendant l'entraînement produirait un agent encore plus robuste et théoriquement imbattable.
*   **Gestion des Processus:** Le script `run_game.py` utilise `subprocess.Popen` de manière simple. Une gestion plus robuste (ex: attendre la fin des processus, les terminer proprement à la sortie du menu) pourrait être ajoutée.
*   **Généralisation:** Le projet est spécifique au Tic Tac Toe. L'architecture pourrait être adaptée à d'autres jeux de plateau simples.
*   **Jouabilité Internet:** Nécessiterait des techniques plus avancées (port forwarding, STUN/TURN, ou services comme ngrok) non implémentées ici.