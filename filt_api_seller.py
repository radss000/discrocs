import requests
from datetime import datetime
import csv
import time
import api_front
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import json

import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from pprint import pprint

# Configuration de la clé API
configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = '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'

# Création d'une instance de l'API avec la configuration
api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

def send_email(user_email, output_file_path):

    
    # Définition de l'expéditeur et du destinataire
    sender = {"email":"art.fact.06@gmail.com", "name":"Art&Facts"}
    recipients = [{"email":user_email}]
    
    # Sujet de l'email
    subject = "Your file is ready, start digging!"
    
    # Corps de l'email en HTML
    html_content = "<html><body><h1>Voici votre fichier de données traitées.</h1><p>Vous trouverez ci-joint le fichier avec les données traitées.</p></body></html>"
    
    # Pièce jointe - Assurez-vous que le chemin est correct
    attachment = [{"url": f"file://{output_file_path}", "name": "ProcessedData.xlsx"}]
    
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(to=recipients, html_content=html_content, sender=sender, subject=subject, attachment=attachment)
    
    try:
        # Envoi de l'email
        api_response = api_instance.send_transac_email(send_smtp_email)
        pprint(api_response)
    except ApiException as e:
        print("Exception lors de l'envoi de l'email via Sendinblue: %s\n" % e)


def clean_email(user_email):
    return user_email.replace('.', '_')


# Initialize Firebase
cred = credentials.Certificate('C:/Users/radia/Downloads/discogs-d266e-firebase-adminsdk-c62xu-80f2507093.json')  # Update path
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://discogs-d266e-default-rtdb.europe-west1.firebasedatabase.app/'  # Update URL
})


# Correction de la signature de la fonction pour accepter une liste de vinyl_records
def save_to_firebase(user_email, username, vinyl_records):
    cleaned_email = clean_email(user_email)
    ref = db.reference(f'/user_data/{cleaned_email}/{username}')

    for vinyl_record in vinyl_records:
        if vinyl_record is not None:  # Vérifiez que vinyl_record n'est pas None
            ref.push(vinyl_record)
        else:
            print("Attempted to save None record to Firebase, skipping...")



def fetch_and_filter_inventory(user_email, username, token, styles):
    url = f"https://api.discogs.com/users/{username}/inventory"
    headers = {'Authorization': f'Discogs token={token}'}

    while url:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print("Failed to fetch inventory:", response.status_code)
            break

        data = response.json()
        inventory = data.get('listings', [])
        url = data.get('pagination', {}).get('urls', {}).get('next')

        for item in inventory:
            release_id = item['release']['id']
            print(f"Processing release ID: {release_id}")
            vinyl_record = process_release(release_id, token, styles)

            if vinyl_record:
                vinyl_data.append(vinyl_record)
                save_to_firebase(user_email, username, [vinyl_record])
  
                print(f"Added record: {vinyl_record}")
            else:
                print(f"No matching style found for release ID: {release_id}")

            time.sleep(1)

def set_scraping_complete(user_email, username):
    cleaned_email = clean_email(user_email)
    # Référence à l'utilisateur spécifique dans la base de données Firebase
    ref = db.reference(f'/user_data/{cleaned_email}/{username}')
    # Écrire l'indicateur que le scraping est complet
    ref.update({'scraping_complete': True})

    print(f"Scraping complet pour l'utilisateur {username}")
def export_user_data_to_json(user_email, username):
    cleaned_email = clean_email(user_email)
    user_ref = db.reference(f'/user_data/{cleaned_email}/{username}')
    user_data = user_ref.get()
    json_data = json.dumps(user_data)
    json_file_path = f"{cleaned_email}_{username}_data.json"
    with open(json_file_path, 'w') as json_file:
        json_file.write(json_data)
    return json_file_path
def process_release(release_id, token, styles):
    release_info = get_release_info(release_id, token)

    if release_info:
        print("API Response Styles:", release_info.get('styles', []))
        if any(style in release_info.get('styles', []) for style in styles):
            final_grade = calculate_final_grade(
                release_info.get('community', {}).get('rating', {}).get('average', 0),
                release_info.get('community', {}).get('want', 0),
                release_info.get('community', {}).get('have', 0),
                release_info.get('lowest_price', 0),
                release_info.get('year', datetime.now().year)
            )

            vinyl_record = {
                "title": release_info.get('title', ''),
                "artist": ', '.join(artist['name'] for artist in release_info.get('artists', [])),
                "rating": release_info.get('community', {}).get('rating', {}).get('average', 0),
                "wantlist": release_info.get('community', {}).get('want', 0),
                "collection": release_info.get('community', {}).get('have', 0),
                "styles": release_info.get('styles', []),
                "url": release_info.get('uri', ''),
                "lowest_price": release_info.get('lowest_price', 0),
                "release_year": release_info.get('year', datetime.now().year),
                "final_grade": final_grade
            }

            print(f"Processed record: {vinyl_record}")
            return vinyl_record
        else:
            print("Style not matched.")
            return None
    else:
        print("Failed to get release info")
        return None

def get_release_info(release_id, token):
    url = f"https://api.discogs.com/releases/{release_id}"
    headers = {'Authorization': f'Discogs token={token}'}
    response = requests.get(url, headers=headers)

    if response.status_code == 429:
        print("Rate limit exceeded, waiting for 2 seconds...")
        time.sleep(2)
        return get_release_info(release_id, token)
    elif response.status_code == 200:
        return response.json()
    else:
        return None

def calculate_final_grade(rating, wantlist, collection, price, release_year):
    weight_rating = 4
    weight_ratio = 10  # Weight for the wantlist/collection ratio
    weight_price = 1
    weight_release_year = 5

    current_year = datetime.now().year
    rating_score = rating * weight_rating

    # Calculate the ratio and handle the case where collection is 0 to avoid division by zero
    ratio_score = 0 if collection == 0 else (wantlist / collection) * weight_ratio

    price_score = price * weight_price
    release_year_score = (current_year - release_year) * weight_release_year

    # Assuming a lower score is better, we might not need to subtract ratio_score from some base value
    return rating_score + ratio_score + price_score + release_year_score



vinyl_data = []