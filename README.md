# Rapport de projet — BIG DATA PROJECT

Date : 11 mai 2026

Auteur : yassine  sinif - azzouz  

Résumé
-------
Ce document présente le rapport technique et fonctionnel du projet « BIG DATA PROJECT ». L'objectif du projet est de mettre en place une chaîne de traitement de données financières (données boursières) comprenant : collecte, streaming via Kafka, stockage MySQL, transformations (ETL) et une interface de visualisation interactive (Streamlit). Le présent rapport décrit l'architecture, l'installation, les composants développés, les tests effectués, les résultats obtenus, les limites et les pistes d'amélioration.

This project implements a modern event-driven Big Data architecture inspired by real-world financial data platforms such as trading systems and market analytics engines. It combines batch processing and real-time streaming to simulate scalable data pipelines used in fintech industries.

1. Introduction
---------------
Le projet vise à démontrer une pipeline de données temps réel et batch pour l'analyse de données boursières. Les composants principaux sont :

- Un producteur Kafka qui récupère des cours de marché (via `yfinance`) et publie des messages sur un topic `stock_topic`.
- Un consommateur Kafka minimal pour démontrer la réception en temps réel des messages.
- Une base MySQL (XAMPP) pour persistance et consultation via SQL.
- Des scripts de transformations (bronze → silver → gold) et un loader vers MySQL.
- Un tableau de bord Streamlit pour visualiser les indicateurs et séries temporelles.

Le projet a été conçu pour être reproductible sur une machine de développement (Windows) avec Docker Desktop pour Kafka/Zookeeper, un environnement Python local (virtualenv) et XAMPP pour MySQL.

2. Objectifs pédagogiques
-------------------------
- Mettre en place un pipeline de collecte et diffusion de données en temps réel.
- Manipuler Kafka pour produire et consommer des événements.
- Stocker et interroger des données dans MySQL.
- Construire une interface interactive pour l'analyse (visualisations, KPI).
- Respecter un cahier des charges donné par l'enseignant et documenter le travail.

3. Architecture du système
-------------------------
Schéma logique :

Scraper (yfinance) → Kafka Producer → Kafka Topic (`stock_topic`) → Kafka Consumer
                                                          ↓
                                                     ETL scripts
                                                          ↓
                                                    MySQL (bigdata_project)
                                                          ↓
                                                   Streamlit Dashboard

Composants et fichiers principaux :

- `scraper/kafka_producer.py` : producteur Kafka continu, multi-tickers, publie toutes les 5 secondes.
- `scraper/kafka_consumer.py` : consommateur Kafka résilient, affiche les messages en temps réel.
- `transformations/load_to_mysql.py` : script d'injection/chargement dans MySQL (utilise SQLAlchemy).
- `dashboards/app.py` : application Streamlit améliorée (sélecteur multi-stock, KPIs, chandeliers, volumes).
- `docker/docker-compose.yml` : configuration Docker Compose pour Zookeeper et Kafka (Confluent images).

4. Installation et exécution
----------------------------
Prérequis : Docker Desktop, Python 3.10+ (ou 3.13 dans l'environnement utilisé), XAMPP (MySQL), un environnement virtuel Python.

Étapes rapides :

1. Cloner le dépôt et se placer dans le dossier du projet.
2. Créer et activer un virtualenv :

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

3. Lancer Kafka et Zookeeper via Docker Compose (depuis `docker/`) :

```powershell
cd docker
docker compose up -d
```

4. Configurer MySQL (XAMPP) : s'assurer que MySQL est accessible sur `127.0.0.1:3307` (ou adapter `MYSQL_PORT`), base `bigdata_project` existante.

5. Lancer le producteur Kafka (optionnel) :

```powershell
python scraper\kafka_producer.py
```

6. Lancer le consommateur pour observation :

```powershell
python scraper\kafka_consumer.py
```

7. Lancer l'application Streamlit :

```powershell
streamlit run dashboards\app.py
```

Remarques :
- Les variables d'environnement MySQL peuvent être passées à la session si nécessaire : `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_DATABASE`.

5. Détails d'implémentation
---------------------------
5.1 Kafka — distributed event streaming system

Kafka is used as a distributed event streaming platform to enable real-time data processing. It acts as a central message broker between the producer and consumer, allowing decoupled and scalable data flow.

The producer continuously publishes stock market events, while the consumer subscribes to the topic and processes messages in real time. This architecture simulates real-world financial streaming systems used in trading platforms and market monitoring systems.

5.2 Producteur et consommateur (implémentation)

- Producteur : boucle continue, envoi de messages toutes les 5 secondes pour plusieurs tickers (`AAPL`, `TSLA`, `MSFT` par défaut). Chaque message inclut un horodatage UTC et les valeurs OHLCV extraites par `yfinance`.
- Consommateur : abonné au topic `stock_topic`, décode JSON et affiche les messages en temps réel. Gestion des erreurs et tentatives de reconnexion.

5.3 Loader MySQL & ETL

- `transformations/load_to_mysql.py` lit les fichiers JSON dans `data/gold/` et écrit la table `stock_analytics` via SQLAlchemy.
- Attention : dans l'état actuel, la table `stock_analytics` est une table d'agrégats (colonnes : `average_close`, `highest_price`, `lowest_price`, `total_volume`). Si vous souhaitez stocker des séries par ticker/date, il faudra adapter le pipeline ETL pour inclure les colonnes `ticker` et `date`.

5.4 Dashboard Streamlit

- Interface professionnelle améliorée : large layout, sélecteur multi-stock, bouton "Refresh Data", affichage des KPIs en 4 colonnes, chandeliers (candlestick), graphiques de volume, tableau de données en pleine largeur.
- Comportement adaptatif : si la table MySQL contient des lignes par ticker, le dashboard filtre par ticker ; si la table n'a qu'un agrégat, le dashboard utilise par défaut les données live récupérées via `yfinance` (fallback).

6. Tests et validation
----------------------
Tests réalisés :

- Connexion MySQL : test `SELECT 1` effectué via SQLAlchemy (succès avec la configuration XAMPP/port 3307).
- Kafka : démarrage via Docker Compose, producteur envoie des messages ; consommateur les reçoit et les affiche. Test manuel envoyé (un message unique) et réception confirmée.
- Dashboard : vérifié en local, sélection des actions met à jour les KPIs (si données live disponibles), les graphiques s'affichent correctement.

7. Résultats observés
---------------------

- Pipeline Kafka fonctionnel en local (Zookeeper + Kafka via Docker).
- Producteur résilient et consommateur simple opérationnel.
- Dashboard Streamlit prêt pour une démonstration orale : KPIs, chandeliers, volumes et table.

8. Limites connues
-------------------

- La table `stock_analytics` fournie est, à ce stade, une table d'agrégats. Pour un vrai historique multi-ticker, il faut modifier les transformations pour enregistrer des lignes par ticker et par date.
- Le système de fichiers de test contient des JSON d'exemple (dans `data/`) — il faudra automatiser la transformation en fonction des besoins de l'évaluation.
- Ce projet est conçu pour un environnement de démonstration local ; en production il faudrait ajouter la surveillance, la persistance durable et la gestion sécurisée des secrets.

9. Conformité avec l'instruction du professeur
----------------------------------------------

Consigne typique (exemple fourni) : construire un pipeline de données boursières avec ingestion, streaming, stockage et visualisation.

- Ingestion/streaming (Kafka) : FAIT — producteur et consommateur opérationnels.
- Stockage (MySQL) : FAIT — table `stock_analytics` écrite par le loader (format agrégé selon l'ETL actuel).
- ETL (transformations) : PARTIEL — scripts de transformation existent (`transformations/`), mais pour un stockage historique par ticker il faut les étendre.
- Visualisation (Streamlit) : FAIT — dashboard interactif et prêt pour présentation.

Conclusion sur la conformité : la majorité des exigences pédagogiques sont respectées. Les principaux travaux restants concernent l'enrichissement de l'ETL pour produire un historique multi-ticker complet si nécessaire.

---

Pourquoi Big Data ?
-------------------
Business relevance:
The system simulates real-time financial market analysis, where data is continuously generated and must be processed with low latency. Such architectures are widely used in stock trading platforms, risk analysis systems, and financial dashboards.

Conclusion
----------
This project demonstrates the implementation of a complete end-to-end Big Data architecture combining batch processing, real-time streaming, and interactive analytics.

It highlights key concepts used in modern data engineering systems including data ingestion, distributed messaging (Kafka), ETL processing, data warehousing, and visualization.

The system is scalable in design and can be extended to cloud environments, real financial APIs, and machine learning prediction models.

10. Recommandations et travaux futurs
-----------------------------------

- Étendre l'ETL pour stocker des enregistrements `ticker,date,open,high,low,close,volume` dans MySQL.
- Ajouter des tests automatisés et des CI basiques (lint, tests unitaires pour les transformations).
- Ajouter un petit dashboard de monitoring pour Kafka et la consommation (délais, backlog, tailles de topic).
- Sécuriser les connexions (ne pas stocker de mots de passe en clair, utiliser des variables d'environnement et secrets manager).

11. Annexes
-----------

Commandes utiles :

```powershell
# Démarrer Kafka/Zookeeper
cd docker
docker compose up -d

# Lancer le producteur
python scraper\kafka_producer.py

# Lancer le consommateur
python scraper\kafka_consumer.py

# Charger les données vers MySQL
python transformations\load_to_mysql.py

# Lancer le dashboard Streamlit
streamlit run dashboards\app.py
```

Structure de fichiers (principale) :

- docker/
- dashboards/app.py
- data/ (bronze/silver/gold)
- scraper/kafka_producer.py
- scraper/kafka_consumer.py
- transformations/*.py
- README.md (ce fichier)



