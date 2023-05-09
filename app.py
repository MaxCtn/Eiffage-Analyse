import os
import pandas as pd
from flask import Flask, render_template, request, send_file, jsonify
from flask_dropzone import Dropzone
from werkzeug.utils import secure_filename
import numpy as np
import itertools
import Levenshtein
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import re


facture_file = None
membres_file = None

def init_extensions(app):
    dropzone = Dropzone(app)
    app.config.update(
        DROPZONE_ALLOWED_FILE_TYPE=".xlsx",
        DROPZONE_MAX_FILE_SIZE=5,
        DROPZONE_MAX_FILES=2,
        DROPZONE_IN_FORM=True,
        DROPZONE_UPLOAD_ON_CLICK=True,
    )
    return app

def create_app():
    app = Flask(__name__, template_folder="myapp/templates", static_folder="myapp/static")

    # Configuration et initialisation des extensions
    init_extensions(app)
    
    UPLOAD_FOLDER = "uploads"
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    @app.route("/analyze", methods=["POST"])
    def analyze():
        global facture_file, membres_file

        members_file = request.files.get("membersFile")
        invoices_file = request.files.get("invoicesFile")

        if members_file and members_file.filename.endswith(".xlsx"):
            file_path = os.path.join("temp_files", secure_filename(members_file.filename))
            members_file.save(file_path)
            print(f"Uploaded file: {members_file.filename}")
            membres_file = file_path

        if invoices_file and invoices_file.filename.endswith(".xlsx"):
            file_path = os.path.join("temp_files", secure_filename(invoices_file.filename))
            invoices_file.save(file_path)
            print(f"Uploaded file: {invoices_file.filename}")
            facture_file = file_path

        if facture_file and membres_file:
            result_file_path = compare_files(facture_file, membres_file)

            if isinstance(result_file_path, str):
                return result_file_path  # Return the result_file_path directly as text
        else:
            return "En attente d'autres fichiers...", 400  # Return a 400 status code to indicate the request was not successful

    @app.route('/download')
    def download():
        result_file_path = request.args.get('result_file_path', type=str)

        if not result_file_path:
            return jsonify({"error": "Aucun fichier de résultat disponible"})

        return send_file(
            result_file_path, as_attachment=True, download_name="resultat.xlsx"
        )

    @app.route("/", methods=["GET", "POST"])
    def index():
        return render_template("index.html")

    return app




def compare_files(facture_file, membres_file, threshold=80):
    # Read the files into pandas dataframes
    facture_df = pd.read_excel(facture_file)
    membres_df = pd.read_excel(membres_file)

    # Filter out users who start with "FRA_" or "(absent)" or "AMBITION NUMERIQUE ETP GRAND SUD"
    facture_df = facture_df.dropna(subset=['Utilisateur'])
    facture_df = facture_df[~facture_df['Utilisateur'].str.startswith("FRA_")]
    facture_df = facture_df[~facture_df['Utilisateur'].str.contains(r"\(absent\)", na=False, regex=True)]
    facture_df = facture_df[~facture_df['Utilisateur'].str.contains("AMBITION NUMERIQUE ETP GRAND SUD")]

    # Get the names in the membres dataframe
    membres_names = membres_df['Salarié'].tolist()

    # Define a function to clean the name by removing digits and ".EXT"
    def clean_name(name):
        name = re.sub(r'\d', '', name)  # Remove digits
        name = re.sub(r'\.EXT', '', name, flags=re.IGNORECASE)  # Remove ".EXT"
        return name.strip()

    # Clean the names in the membres_names list
    membres_names = [clean_name(name) for name in membres_names]

    # Define a function to find the best match
    def find_best_match(name):
        cleaned_name = clean_name(name)
        best_match = process.extractOne(cleaned_name, membres_names, scorer=fuzz.token_set_ratio)
        if best_match[1] >= threshold:
            return True
        else:
            return False

    # Create a new column in the facture_df to store the best match in the other dataframe
    facture_df['has_match'] = facture_df['Utilisateur'].apply(find_best_match)

    # Get the names that do not have a match in the other file
    result_df = facture_df[~facture_df['has_match']]

    # Write the result to a new file
    result_file_path = 'result.xlsx'
    result_df.to_excel(result_file_path, index=False)

    return result_file_path








if __name__ == "__main__":
    app_instance = create_app()
    app_instance.run(debug=True)