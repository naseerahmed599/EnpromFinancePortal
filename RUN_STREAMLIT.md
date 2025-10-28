# 🚀 How to Run the Flowwer API Streamlit App

## 📋 Prerequisites

1. Python 3.8 or higher installed
2. pip (Python package manager)

## 🔧 Installation Steps

### 1. Install Required Packages

Open your terminal and navigate to the project folder, then run:

```bash
pip install -r requirements.txt
```

Or install packages individually:

```bash
pip install streamlit requests pandas
```

### 2. Run the Streamlit App

```bash
streamlit run streamlit_flowwer_app.py
```

### 3. Access the App

After running the command, Streamlit will:
- Start a local server
- Automatically open your browser to `http://localhost:8501`

If it doesn't open automatically, manually go to: **http://localhost:8501**

## 🎯 Features

### 📋 All Documents Page
- View all documents from Flowwer
- Filter by Company, Stage, Payment State
- Export to CSV or JSON
- Real-time data refresh

### 🔎 Single Document Page
- Get detailed information about a specific document
- View in organized tabs (General, Invoice Details, Dates, Raw JSON)
- Copy Unique ID for downloads

### 🏢 Companies & Flows Page
- View all companies and their active flows
- Summary statistics

###   Download Document Page
- Download PDF documents
- Get Unique ID helper
- Save to computer

### 📤 Upload Document Page
- Upload PDF files to Flowwer
- Assign to specific Flow and Company
- Custom filename support

### ⚙️ Settings Page
- Manage API keys
- Generate new API keys
- View session information

## 🔑 API Key

The app comes pre-configured with the API key:
```
MXrKdv77r3lTlPzdc8N8mjdT5YzA87iL
```

You can change it in the Settings page.

## 🛑 Stop the App

To stop the Streamlit app:
- Press `Ctrl + C` in the terminal

##    Restart the App

If you make changes to the code:
1. Stop the app (`Ctrl + C`)
2. Run `streamlit run streamlit_flowwer_app.py` again

Or use the "Rerun" button in the Streamlit UI (top-right corner).

## 💡 Tips

1. **Always start fresh:** Click the "Refresh" buttons to get latest data
2. **Use filters:** On the All Documents page, use filters to find specific documents
3. **Export data:** Download CSV or JSON for further analysis
4. **Get Unique ID:** Use Single Document page to get the UUID needed for downloads

## 🐛 Troubleshooting

### Port Already in Use
If you see "Address already in use" error:
```bash
streamlit run streamlit_flowwer_app.py --server.port 8502
```

### Module Not Found
Make sure you're in the correct directory:
```bash
cd /Users/naseer/Documents/ENPROM/Work-ED/project-flowwer
```

### API Errors
- Check your internet connection
- Verify the API key is correct in Settings
- Check if Flowwer API is accessible

## 📱 Access from Other Devices

To access from another device on the same network:
```bash
streamlit run streamlit_flowwer_app.py --server.address 0.0.0.0
```

Then access via: `http://YOUR_IP:8501`

## 🎨 Customization

The app is fully customizable. Edit `streamlit_flowwer_app.py` to:
- Add new pages
- Modify filters
- Change colors and layout
- Add new API endpoints

---

**Enjoy exploring the Flowwer API! 🎉**
