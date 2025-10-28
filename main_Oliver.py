from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tkinter import Tk, filedialog
import time
import csv

# === 1. Dokumenten-ID abfragen ===
document_id = input("📌 Bitte gib die Dokumenten-ID ein: ").strip()
url = f"https://enprom-gmbh.flowwer.de/signabledocuments/document/{document_id}"

# === 2. CSV-Datei auswählen ===
Tk().withdraw()
csv_path = filedialog.askopenfilename(
    title="📂 Bitte wähle die CSV-Datei aus",
    filetypes=[("CSV-Dateien", "*.csv")]
)

if not csv_path:
    print("❌ Keine Datei ausgewählt. Vorgang abgebrochen.")
    exit()

print(f"📄 Ausgewählte Datei: {csv_path}")

# === 3. Zugangsdaten ===
USERNAME = "o.heinke@enprom.com"
PASSWORD = "MasterHuman_2025"

# === 4. Selenium Setup ===
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)

def open_vat_group(driver, wait, rate):
    print(f"🔽 Öffne Mehr-Dropdown für {rate}%")

    try:
        # 1. Dropdown „Mehr“ öffnen
        mehr_button = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(@class, 'dropdown-toggle') and contains(text(), 'Mehr')]")
        ))
        driver.execute_script("arguments[0].scrollIntoView(true);", mehr_button)
        mehr_button.click()
        print("✅ Dropdown geöffnet")
        time.sleep(1.5)

        # 2. Auswahl z. B. „19% auswählen“
        selection_xpath = f"//button[contains(@class, 'dropdown-item') and contains(normalize-space(.), '{rate}% auswählen')]"
        selection_button = wait.until(EC.element_to_be_clickable((By.XPATH, selection_xpath)))
        driver.execute_script("arguments[0].scrollIntoView(true);", selection_button)
        selection_button.click()
        print(f"✅ Steuersatzgruppe {rate}% ausgewählt")
        time.sleep(2)

    except Exception as e:
        print(f"❌ Fehler beim Öffnen von {rate}% Steuergruppe: {e}")
        raise

try:
    print(f"🌐 Öffne: {url}")
    driver.get(url)
    wait = WebDriverWait(driver, 20)

    wait.until(EC.presence_of_element_located((By.ID, "Input_UserName"))).send_keys(USERNAME)
    wait.until(EC.presence_of_element_located((By.ID, "Input_Password"))).send_keys(PASSWORD)
    driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

    wait.until(EC.url_contains(f"/signabledocuments/document/{document_id}"))
    print(f"✅ Erfolgreich eingeloggt und auf Dokument {document_id}.")

    # === 6. CSV lesen ===
    invoice_split_data_19 = []
    invoice_split_data_0 = []

    with open(csv_path, mode='r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            cost_center = row['cost_center']
            vat_rate = int(float(row['vat_rate_de']))
            gross_value = row['gross_value'].replace('.', ',')  # Punkt durch Komma ersetzen

            if vat_rate == 19:
                invoice_split_data_19.append((cost_center, gross_value))
            elif vat_rate == 0:
                invoice_split_data_0.append((cost_center, gross_value))
            else:
                print(f"⚠️ Unbekannter Steuersatz {vat_rate} – übersprungen.")

    # === 7. Verarbeitung pro Steuersatz ===
    def process_vat_entries(data, rate):
        if not data:
            return

        print(f"➡️ Starte Eingabe für {rate}% MwSt mit {len(data)} Zeilen")

        open_vat_group(driver, wait, rate)

        for i, (cost_center, gross_value) in enumerate(data):
            try:
                # === Eingabe Kostenstelle
                cost_input = wait.until(EC.presence_of_element_located(
                    (By.XPATH, "//input[@name='entry.CostCenter']")))
                cost_input.clear()
                cost_input.send_keys(cost_center)

                # === Eingabe Bruttobetrag
                brutto_input = wait.until(EC.presence_of_element_located(
                    (By.XPATH, "//input[@placeholder='Brutto']")))
                brutto_input.clear()
                brutto_input.send_keys(gross_value)

                print(f"✅ Eingetragen: {cost_center} / {gross_value}")

                # === "+" Button nur wenn weitere Einträge folgen
                if i != len(data) - 1:
                    plus_button = wait.until(EC.element_to_be_clickable((
                        By.XPATH, "//button[contains(@class, 'btn-outline-success') and @title]"
                    )))
                    driver.execute_script("arguments[0].scrollIntoView(true);", plus_button)
                    plus_button.click()
                    time.sleep(2)

            except Exception as e:
                print(f"❌ Fehler beim Eintrag {i + 1}: {e}")
                break

    # === 8. Ausführen für beide Steuersätze ===
    process_vat_entries(invoice_split_data_19, 19)
    process_vat_entries(invoice_split_data_0, 0)

    input("⏸️ Prüfung beendet – Enter zum Speichern drücken...")

    # === 9. Speichern
    save_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[text()="Speichern"]')))
    save_button.click()
    print("💾 Split gespeichert. Fertig.")

except Exception as e:
    print(f"❌ Fehler: {e}")
finally:
    driver.quit()
