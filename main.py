import streamlit as st
import csv
import requests
import os
import pandas as pd
from urllib.parse import urlparse
import tempfile
import io

def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

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
    try:
        # Lire le contenu du fichier en mémoire
        csv_content = csv_file.getvalue().decode('utf-8')
        
        # Vérifier si le fichier est vide
        if not csv_content.strip():
            st.error("Le fichier CSV est vide.")
            return

        # Créer un DataFrame à partir du contenu CSV
        df = pd.read_csv(io.StringIO(csv_content))
        
        # Vérifier si le DataFrame est vide
        if df.empty:
            st.error("Le fichier CSV ne contient pas de données valides.")
            return

        # Vérifier si les colonnes requises sont présentes
        required_columns = ['nom_fichier', 'url_pdf']
        if not all(col in df.columns for col in required_columns):
            st.error("Le fichier CSV doit contenir les colonnes 'nom_fichier' et 'url_pdf'.")
            return

        # Créer un dossier temporaire pour les PDFs
        with tempfile.TemporaryDirectory() as temp_dir:
            total_files = len(df)
            progress_bar = st.progress(0)
            status_text = st.empty()

            successful_downloads = 0
            failed_downloads = 0

            for index, row in df.iterrows():
                nom_fichier = str(row['nom_fichier'])
                url_pdf = str(row['url_pdf'])

                if pd.isna(nom_fichier) or pd.isna(url_pdf) or not is_valid_url(url_pdf):
                    status_text.text(f"URL invalide ignorée: {url_pdf}")
                    failed_downloads += 1
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
                    successful_downloads += 1
                else:
                    status_text.text(f"Échec du téléchargement: {nom_fichier}")
                    failed_downloads += 1

                # Mise à jour de la barre de progression
                progress_bar.progress((index + 1) / total_files)

            status_text.text("Téléchargement terminé!")
            st.success(f"Téléchargements réussis: {successful_downloads}, Échecs: {failed_downloads}")
            st.info(f"Les PDFs ont été téléchargés dans le dossier temporaire : {temp_dir}")

    except Exception as e:
        st.error(f"Une erreur s'est produite lors du traitement du fichier CSV: {str(e)}")

def main():
    st.title("Téléchargeur de PDFs à partir d'un CSV")
    
    st.write("Veuillez télécharger un fichier CSV contenant deux colonnes : 'nom_fichier' et 'url_pdf'.")
    
    uploaded_file = st.file_uploader("Choisissez un fichier CSV", type="csv")
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.write("Aperçu du fichier CSV:")
            st.dataframe(df.head())
            
            if st.button("Lancer le téléchargement des PDFs"):
                process_csv(uploaded_file)
        except pd.errors.EmptyDataError:
            st.error("Le fichier CSV est vide ou ne contient pas de données valides.")
        except Exception as e:
            st.error(f"Une erreur s'est produite lors de la lecture du fichier CSV: {str(e)}")

if __name__ == "__main__":
    main()
