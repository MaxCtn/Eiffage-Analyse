import os
from flask import Flask, render_template, request, send_file, jsonify
from flask_dropzone import Dropzone
from werkzeug.utils import secure_filename
import pandas as pd
import openpyxl
from openpyxl import Workbook

def init_extensions(app):
    dropzone = Dropzone(app)
    app.config.update(
        UPLOADED_PATH=os.path.join(app.root_path, "uploads"),
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
    result_file_path = None
    RESULT_FILE = "resultat.xlsx"

    UPLOAD_FOLDER = "uploads"
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

    TEMP_FOLDER = "temp_files"
    if not os.path.exists(TEMP_FOLDER):
        os.makedirs(TEMP_FOLDER)

    facture_file = None
    membres_file = None

    def compare_files(facture_path, membres_path):
        if not os.path.isfile(facture_path):
            return f"Facture file not found: {facture_path}"
        if not os.path.isfile(membres_path):
            return f"Membres file not found: {membres_path}"
        
        facture_df = pd.read_excel(facture_path, header=[0, 1], skiprows=[1])
        membres_df = pd.read_excel(membres_path, skiprows=[1])

        user_column = None
        for col in facture_df.columns:
            if (
                "Utilisateur" in col[0]
                or "User" in col[0]
                or "Utilisateur" in col[1]
                or "User" in col[1]
            ):
                user_column = col
                break

        if user_column is None:
            return "No user column found in facture.xlsx"

        if isinstance(facture_df.columns, pd.MultiIndex):
            facture_df.columns = facture_df.columns.get_level_values(1) if not facture_df.columns.get_level_values(1).isna().any() else facture_df.columns.get_level_values(0)
        facture_df = facture_df.iloc[2:]
        
        facture_df["Nom"] = facture_df[user_column].apply(lambda x: x.split(",")[0].strip())
        facture_df["Prénom"] = facture_df[user_column].apply(lambda x: x.split(",")[1].strip())

        facture_df.drop(columns=[user_column], inplace=True)

        membres_df["Nom"] = membres_df["Salarié"]
        membres_df["Prénom"] = membres_df.iloc[:, 3].str.strip()
        membres_df.drop(columns=["Salarié"], inplace=True)

        facture_nom_prenom = set(facture_df["Nom"] + ", " + facture_df["Prénom"])
        membres_nom_prenom = set(membres_df["Nom"] + ", " + membres_df["Prénom"])

        difference = facture_nom_prenom.difference(membres_nom_prenom)

        result_df = facture_df[
            facture_df.apply(
                lambda row: row["Nom"] + ", " + row["Prénom"] in difference, axis=1
            )
        ]

        result_df.to_excel(result_file, index=False)
        return result_file

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Une erreur interne s'est produite. Veuillez réessayer."}), 500

    @app.route("/analyze", methods=["POST"])
    def analyze():
        uploaded_files = request.files.getlist("file")
        print("Received files:", [f.filename for f in uploaded_files])
        uploaded_files = request.files.getlist("file")
        file_paths = []

        for uploaded_file in uploaded_files:
            print(f"Processing file: {uploaded_file.filename}")
            file_path = os.path.join("temp_files", secure_filename(uploaded_file.filename))
            uploaded_file.save(file_path)
            file_paths.append(file_path)

        return jsonify({"result_file_path": file_paths})

    @app.route("/download")
    def download():
        file_paths = request.args.get("file_paths").split(",")

        if not file_paths:
            return jsonify({"error": "Aucun fichier de résultat disponible"})

        facture_file_path = file_paths[0]
        membres_file_path = file_paths[1]

        print(f"Facture file path: {facture_file_path}")
        print(f"Membres file path: {membres_file_path}")

        result = compare_files(facture_file_path, membres_file_path)

        if isinstance(result, str):
            return jsonify({"error": result})

        result_file_path = result

        # Supprimer les fichiers temporaires après les avoir utilisés
        os.remove(facture_file_path)
        os.remove(membres_file_path)

        return send_file(
            result_file_path, as_attachment=True, download_name="resultat.xlsx"
        )

    @app.route("/", methods=["GET", "POST"])
    def index():
        global facture_file, membres_file
        if request.method == "POST":
            file = request.files.get("file")    
            if file.filename.endswith(".xlsx"):
                file_path = os.path.join(app.config["UPLOADED_PATH"], file.filename)
                file.save(file_path)
                print(f"Uploaded file: {file.filename}")
                if "facture" in file.filename.lower():
                    facture_file = file_path
                elif "membres" in file.filename.lower():
                    membres_file = file_path
                if facture_file and membres_file:
                    print(f"Facture file: {facture_file}")
                    print(f"Membres file: {membres_file}")
                    compare_files(facture_file, membres_file)
                    facture_file = None
                    membres_file = None
        return render_template("index.html")

    init_extensions(app)
    return app

if __name__ == "__main__":
    app_instance = create_app()
    app_instance.run(debug=True)

