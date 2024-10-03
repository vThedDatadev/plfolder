import streamlit as st
import csv
import requests
import os
import pandas as pd
from urllib.parse import urlparse
import tempfile

def download_pdf(url, filename):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        with open(filename, 'wb') as f:
            f.write(response.content)
        return True
    except requests.RequestException as e:
        st.error(f"Erreur lors du téléchargement de {url}: {str(e)}")
        return False

def process_csv(csv_file):
    # Créer un dossier temporaire pour les PDFs
    with tempfile.TemporaryDirectory() as temp_dir:
        df = pd.read_csv(csv_file)
        total_files = len(df)
        progress_bar = st.progress(0)
        status_text = st.empty()

        for index, row in df.iterrows():
            nom_fichier = row[0]
            url_pdf = row[1]

            if pd.isna(nom_fichier) or pd.isna(url_pdf):
                continue

            # Nettoyer le nom de fichier
            nom_fichier = ''.join(c for c in nom_fichier if c.isalnum() or c in (' ', '.', '_')).rstrip()
            nom_fichier = nom_fichier.replace(' ', '_')

            # Ajouter l'extension .pdf si elle n'est pas présente
            if not nom_fichier.lower().endswith('.pdf'):
                nom_fichier += '.pdf'

            # Chemin complet du fichier
            chemin_fichier = os.path.join(temp_dir, nom_fichier)

            # Télécharger et sauvegarder le PDF
            if download_pdf(url_pdf, chemin_fichier):
                status_text.text(f"Téléchargé: {nom_fichier}")
            else:
                status_text.text(f"Échec du téléchargement: {nom_fichier}")

            # Mise à jour de la barre de progression
            progress_bar.progress((index + 1) / total_files)

        status_text.text("Téléchargement terminé!")
        st.success(f"Tous les PDFs ont été téléchargés dans le dossier temporaire : {temp_dir}")

def main():
    st.title("Téléchargeur de PDFs à partir d'un CSV")

    uploaded_file = st.file_uploader("Choisissez un fichier CSV", type="csv")
    
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.write("Aperçu du fichier CSV:")
        st.dataframe(df.head())

        if st.button("Lancer le téléchargement des PDFs"):
            process_csv(uploaded_file)

if __name__ == "__main__":
    main()
