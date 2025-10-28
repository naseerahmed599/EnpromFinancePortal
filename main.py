
import os
import csv
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Dynamischen Importpfad für login_to_flowwer manuell setzen
module_path = os.path.join(os.path.dirname(__file__), 'load_data_to_flowwer', 'modules')
sys.path.append(module_path)

# Debug: Module überprüfen
print(f"🐞 DEBUG >>> Modulpfad: {module_path}")
if os.path.exists(module_path):
    print("📁 Modulordner gefunden.")
    print("📄 Inhalt des Ordners:", os.listdir(module_path))
else:
    print("❌ Modulordner NICHT gefunden.")

# Modul importieren
try:
    from login_to_flowwer import perform_login
    print("✅ Import erfolgreich!")
except ImportError as e:
    print(f"❌ Fehler beim Import: {e}")

# Eingaben abfragen
steuer = input("📊 Bitte Steuersatz eingeben (19 oder 0): ").strip()
dokumenten_id = input("🆔 Bitte Dokumenten-ID eingeben: ").strip()

# Datei überprüfen
file_path = r'C:\Users\o.heinke\OneDrive - ENPROM\M365_Finance-Financial Statements - Dokumente\Financial Dashboard\Reports\UTA\Import\aggregated_data.csv'
if os.path.exists(file_path):
    print(f"📄 Datei gefunden: {file_path}")
else:
    print(f"❌ Datei NICHT gefunden: {file_path}")

# Ziel-URL vorbereiten
base_url = "https://enprom-gmbh.flowwer.de/unassigneddocuments/document"
print(f"🌐 Ziel-URL: {base_url}")

# Login und Upload starten
perform_login(base_url, file_path, steuer, dokumenten_id)
