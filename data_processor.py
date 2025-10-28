import pandas as pd
import numpy as np

def process_invoice_data(uta_invoice_no_filter, vat_rate_de_filter):
    # Define paths to Excel files
    file_path = r"N:\05_DE Finanzabteilung\Enprom GmbH\Accounting\KFZ\UTA\Enprom GmbH\EN_UTA_MSTR.xlsx"
    #file_path = r"C:\Users\k.zasacki\OneDrive - ENPROM\Dokumenty\temp\EN_UTA_MSTR.xlsx"
    equipment_ids_file_path = r"C:\Users\k.zasacki\OneDrive - ENPROM\Dokumenty\ENPROM\DATABASE\cost_centers\equipment_ids.xlsx"
    uta_invoice_no_file_path = r"C:\Users\k.zasacki\OneDrive - ENPROM\Dokumenty\ENPROM\DATABASE\dictionaries\uta_invoice_no.xlsx"
    output_csv_path = r"C:\Users\k.zasacki\OneDrive - ENPROM\Dokumenty\ENPROM\GIT\pythonClicker\load_data_to_flowwer\data\aggregated_data.csv"

    # Load the data from the specified sheets
    try:
        uta_data = pd.read_excel(file_path, sheet_name='Data', header=1)
        equipment_ids = pd.read_excel(equipment_ids_file_path, sheet_name='equipment_ids (2)')
        uta_invoice_no = pd.read_excel(uta_invoice_no_file_path, sheet_name='uta_invoices')
        print("Data loaded successfully from all files.")
    except Exception as e:
        print("Error loading Excel files:", e)
        return

    # Rename and prepare data
    uta_data.rename(columns={
        'Rechn.datum': 'uta_invoice_date',
        'USt.-Satz': 'vat_rate',
        'Land': 'country_code',
        'Kfz-Kennz.': 'plate_no',
        'Umsatz Brutto': 'gross_value'
    }, inplace=True)

    # Convert date columns to datetime
    uta_data['uta_invoice_date'] = pd.to_datetime(uta_data['uta_invoice_date'])
    uta_invoice_no['uta_invoice_date'] = pd.to_datetime(uta_invoice_no['uta_invoice_date'])

    # Process 'plate_no' by removing spaces in equipment_ids
    equipment_ids['plate_no'] = equipment_ids['plate_no'].str.replace(" ", "", regex=True)

    # Merge operations
    uta_data = pd.merge(uta_data, equipment_ids[['plate_no', 'cost_center']], on='plate_no', how='left')
    uta_data = pd.merge(uta_data, uta_invoice_no[['uta_invoice_no', 'uta_invoice_date']], on='uta_invoice_date', how='left')
    uta_data['vat_rate_de'] = np.where(uta_data['vat_rate'] == 19.00, uta_data['vat_rate'], 0)
    #uta_data['vat_rate_de'] = np.where(uta_data['country_code'] == 'DEU', uta_data['vat_rate'], 0)

    # Aggregate the data
    aggregated_data = uta_data.groupby(['uta_invoice_no', 'cost_center', 'vat_rate_de']).agg({
        'gross_value': 'sum'
    }).reset_index()

    # Convert data types and format
    aggregated_data['uta_invoice_no'] = pd.to_numeric(aggregated_data['uta_invoice_no'], errors='coerce').fillna(0).astype(int)
    aggregated_data['cost_center'] = pd.to_numeric(aggregated_data['cost_center'], errors='coerce').fillna(0).astype(int)
    aggregated_data['gross_value'] = aggregated_data['gross_value'].round(2)

    # Filter the final aggregated data by specific variables
    final_data = aggregated_data[
        (aggregated_data['uta_invoice_no'] == uta_invoice_no_filter) &
        (aggregated_data['vat_rate_de'] == vat_rate_de_filter)
    ]

    # Save the final filtered data to a CSV file
    try:
        final_data.to_csv(output_csv_path, index=False)
        print(f"Filtered data successfully written to {output_csv_path}")
    except Exception as e:
        print("Failed to write data to CSV:", e)


