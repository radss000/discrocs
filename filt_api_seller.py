import requests
from datetime import datetime
import csv
import time
import api_front
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import json

from pprint import pprint

def send_email(user_email, output_file_path):
    api_key = '1e011b62826101482c83a897f793e4d4-b02bcf9f-876e81d4'
    domain_name = 'sandbox6dc090ec95f043f2b341cd75ca6a9013.mailgun.org'
    
    # Open the file in a context manager 
    with open(output_file_path, "rb") as attachment:
        response = requests.post(
            f"https://api.mailgun.net/v3/{domain_name}/messages",
            auth=("api", api_key),
            files=[("attachment", (output_file_path, attachment.read()))], # Add the file as an attachment
            data={
                "from": f"Art&Facts <mailgun@{domain_name}>",
                "to": [user_email],
                "subject": "Start digging!",
                "text": "Hey, your file is ready, start digging!"
            }
        )
    
    # Print the status code and the result of the request
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")
    
    return response

def clean_email(user_email):
    return user_email.replace('.', '_')


firebase_credentials = {
    "type": "service_account",
    "project_id": os.environ.get("FIREBASE_PROJECT_ID"),
    "private_key_id": "discogs-d266e",
    "private_key": os.environ.get("FIREBASE_PRIVATE_KEY").replace('\\n', '\n'),
    "client_email": os.environ.get("FIREBASE_CLIENT_EMAIL"),
    "client_id": "110984853127742760045",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "your_client_x509_cert_url"
}

cred = credentials.Certificate(firebase_credentials)
firebase_admin.initialize_app(cred, {
    'databaseURL': os.environ.get("FIREBASE_DATABASE_URL")
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
