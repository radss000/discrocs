
# Discrocs - Discogs Data Scraper and Analyzer

Discrocs est une application web développée en Python avec le framework Flask. Elle permet de récupérer et d'analyser des données sur des vinyles à partir de l'API de Discogs, puis de les classer en les notant à partir des champs scrapés. L'utilisateur peut soumettre une requête pour récupérer des informations sur des articles spécifiques, et l'application effectue une analyse en utilisant des techniques de machine learning pour évaluer et prédire des caractéristiques pertinentes.

## Fonctionnalités

- Scraper des données d'inventaire de Discogs chez un vendeur en utilisant un token d'authentification.
- Filtrer les résultats en fonction des styles de musique spécifiés par l'utilisateur.
- Analyser les données collectées pour calculer un "score final" pour chaque vinyle.
- Permettre le téléchargement des résultats suite à la réception d'un mail automatique reçu à la fin du process.

## Comment ça marche

1. L'utilisateur entre le nom d'utilisateur du vendeur chez lequel il souhaite analyser certaines releases sur Discogs, son token d'API, et les styles de musique qu'il souhaite filtrer.
2. L'application interroge l'API de Discogs et récupère les données correspondantes.
3. Ces données sont ensuite analysées pour calculer un score final basé sur le rating, le nombre de personnes voulant l'article (wantlist), le nombre de personnes possédant l'article (collection), le prix le plus bas et l'année de sortie avec une régression.
4. Les résultats sont sauvegardés dans un fichier Excel, que l'utilisateur peut télécharger directement en checkant sa boîte mail.


## Machine Learning dans Discrocs

L'application Discrocs utilise un modèle de régression pour analyser et prédire la popularité et la rareté potentielle d'un vinyle basée sur des données historiques. Voici un aperçu du processus :

### Algorithme

Nous utilisons un modèle de régression de forêt aléatoire (`RandomForestRegressor`) de la bibliothèque `scikit-learn` pour notre analyse prédictive. Cet algorithme est choisi pour sa capacité à gérer des jeux de données complexes et à fournir des prédictions fiables.

### Caractéristiques (Features)

Pour chaque vinyle, les caractéristiques suivantes sont extraites et utilisées pour l'entraînement et les prédictions du modèle :

- `rating` : La note moyenne du vinyle donnée par les utilisateurs de Discogs.
- `wantlist` : Le nombre d'utilisateurs qui ont ajouté le vinyle à leur liste de souhaits.
- `collection` : Le nombre d'utilisateurs qui possèdent le vinyle.
- `lowest_price` : Le prix le plus bas auquel le vinyle a été vendu.
- `release_year` : L'année de sortie du vinyle.

### Traitement des données

Avant de les fournir à l'algorithme, les données subissent plusieurs étapes de prétraitement :

1. **Nettoyage des données** : Les données manquantes ou erronées sont corrigées ou supprimées.
2. **Création de nouvelles caractéristiques** : Un ratio entre `wantlist` et `collection` est calculé pour estimer la demande par rapport à la disponibilité.
3. **Normalisation** : Les caractéristiques numériques sont normalisées pour éviter que certaines d'entre elles ne dominent indûment les autres dans le processus d'apprentissage.

### Entraînement et évaluation du modèle

Le modèle est entraîné sur un ensemble de données historiques et évalué à l'aide de la méthode de la validation croisée. Le Mean Squared Error (MSE) est utilisé comme métrique pour évaluer la précision des prédictions du modèle.

### Utilisation du modèle

Une fois entraîné, le modèle est utilisé pour prédire le `final_grade` de nouveaux vinyles non vus, qui est un score calculé pouvant aider les utilisateurs à déterminer quels vinyles pourraient être intéressants à acheter ou à vendre.

## Utilisation
Pour démarrer le processus de scraping et d'analyse, accédez à l'adresse suivante dans votre navigateur après avoir lancé l'application : (Pour l'instant, une URL dédiée sera bientôt disponible)

http://localhost:5000/
Entrez les informations requises dans le formulaire et cliquez sur le bouton pour commencer le processus. Vous serez notifié une fois que le fichier Excel sera prêt à être téléchargé.

## Installation

Pour installer et exécuter ce projet localement, suivez ces étapes :

```bash
git clone https://github.com/radss000/discrocs
cd discrocs
pip install -r requirements.txt
flask run
'''


