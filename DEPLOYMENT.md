# Deployment Guide for Flowwer Finance Portal

## 🚀 Deploy to Streamlit Community Cloud

### Step 1: Prepare Your Repository
1. **Push your code to GitHub** (make sure repo is public)
   ```bash
   git add .
   git commit -m "Prepare for deployment"
   git push origin main
   ```

2. **Important**: The `.gitignore` file already excludes `secrets.toml`, so your API key won't be committed.

### Step 2: Deploy on Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click **"New app"**
4. Configure:
   - **Repository**: `naseerahmed599/EnpromFinancePortal`
   - **Branch**: `main`
   - **Main file path**: `project-flowwer/enprom_financial_app.py`
5. Click **"Deploy"**

### Step 3: Add Your Secrets
1. After deployment starts, click **⚙️ Settings** → **Secrets**
2. Paste this configuration:
   ```toml
   [flowwer]
   api_key = "your_API_Key"
   base_url = "https://enprom-gmbh.flowwer.de"
   ```
3. Click **"Save"**
4. Your app will automatically restart with the secrets

### Step 4: Upload Required Files
You need to upload `Financial_Dashboard_Latest.xlsx` since it's not in Git:
- Option A: Add to GitHub (if file isn't too sensitive)
- Option B: Store in cloud (Google Drive, Dropbox) and update the path in code
- Option C: Use Streamlit file uploader to load it dynamically

---

## 🔒 Security Notes

✅ **What's Public:**
- Your Python code
- App UI and functionality
- Package dependencies

🔐 **What's Private:**
- API keys (stored in Streamlit Cloud secrets)
- `Financial_Dashboard_Latest.xlsx` (not in Git)
- Any data loaded through the API

---

## 📝 Local Development

The app now uses secrets for both local and cloud deployment:

**Local**: Reads from `.streamlit/secrets.toml` (not committed to Git)
**Cloud**: Reads from Streamlit Cloud secrets configuration

To run locally:
```bash
cd project-flowwer
streamlit run enprom_financial_app.py
```

---

## 🆘 Troubleshooting

**"Secrets not found" error:**
- Locally: Make sure `.streamlit/secrets.toml` exists
- Cloud: Add secrets in Streamlit Cloud dashboard settings

**App won't start:**
- Check that `requirements.txt` includes all dependencies
- Verify the main file path is correct: `project-flowwer/enprom_financial_app.py`

**Excel file not found:**
- Upload `Financial_Dashboard_Latest.xlsx` to the repo, or
- Modify code to use an alternative data source

---

## 📦 Dependencies

Make sure your `requirements.txt` includes:
```
streamlit
pandas
openpyxl
requests
plotly
```
