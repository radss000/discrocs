from flask import Flask, request, jsonify, render_template, send_from_directory
import threading
import filt_api_seller as scraper
import ml_discogs_stats as ml
import json
import os
from firebase_admin import db
import pandas as pd

app = Flask(__name__)

process_complete = False
process_complete_path = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/discrocs/<path:filename>')
def download_file(filename):
    # Use the global variable to construct the file path
    file_path = os.path.join(os.getcwd(), 'discrocs', process_complete_path)

    # Serve the file
    return send_from_directory(directory=os.path.dirname(file_path), filename=os.path.basename(file_path), as_attachment=True)

@app.route('/check_process_status')
def check_process_status():
    return jsonify({'process_complete': process_complete})

@app.route('/submit_data', methods=['POST'])
def submit_data():
    username = request.form['username']
    token = request.form['token']
    styles = request.form['styles'].split(',')
    user_email = request.form['user_email']

    # Lancer le processus dans un thread pour ne pas bloquer l'application
    thread = threading.Thread(target=run_process, args=(user_email, username, token, styles))
    thread.start()


    # Récupérer le nom de fichier généré
    output_file_path = thread.get_result()

    # Stocker le nom de fichier généré dans une variable globale
    global process_complete_path
    process_complete_path = output_file_path

    # Retourner le nom de fichier généré dans la réponse JSON
    return jsonify({"message": "Processus terminé. Les résultats sont prêts à être téléchargés.", "filename": output_file_path})

def clean_email(user_email):
    return user_email.replace('.', '_')

def export_user_data_to_json(user_email, username):
    cleaned_email = clean_email(user_email)
    user_ref = db.reference(f'/user_data/{cleaned_email}/{username}')
    user_data = user_ref.get()
    json_data = json.dumps(user_data)
    json_file_path = f"{cleaned_email}_{username}_data.json"
    with open(json_file_path, 'w') as json_file:
        json_file.write(json_data)
    return json_file_path

from concurrent.futures import ThreadPoolExecutor

# Votre fonction run_process doit retourner output_file_path

@app.route('/submit_data', methods=['POST'])
def submit_data():
    username = request.form['username']
    token = request.form['token']
    styles = request.form['styles'].split(',')
    user_email = request.form['user_email']

    # Lancer le processus dans un thread pour ne pas bloquer l'application
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(run_process, user_email, username, token, styles)
        output_file_path = future.result()  # Attend que le thread soit terminé et récupère le résultat

    # Stocker le nom de fichier généré dans une variable globale
    global process_complete_path
    process_complete_path = output_file_path

    # Marquer le processus comme terminé
    global process_complete
    process_complete = True

    # Retourner le nom de fichier généré dans la réponse JSON
    return jsonify({"message": "Processus terminé. Les résultats sont prêts à être téléchargés.", "filename": output_file_path})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
