# Pharmacy POS Dashboard — Setup Guide

## 1. Install Python dependencies

```bash
pip install -r requirements.txt
```

## 2. Create a Google Cloud project and enable APIs

1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project (or use an existing one).
3. Navigate to **APIs & Services > Library**.
4. Enable **Google Sheets API** and **Google Drive API**.

## 3. Create a service account

1. Go to **APIs & Services > Credentials**.
2. Click **Create Credentials > Service Account**.
3. Give it a name (e.g. `pharmacy-dashboard`), click **Done**.
4. Click the new service account, go to the **Keys** tab.
5. Click **Add Key > Create New Key > JSON**. A `credentials.json` file will download.

## 4. Store the credentials file

```bash
mkdir -p ~/.pharmacy-dashboard
mv ~/Downloads/credentials.json ~/.pharmacy-dashboard/credentials.json
```

## 5. Share the Google Sheet

Open your pharmacy spreadsheet in Google Sheets. Click **Share** and add the service account email address (found in the JSON file under `client_email`, e.g. `pharmacy-dashboard@project.iam.gserviceaccount.com`). Grant **Viewer** access.

## 6. Configure the spreadsheet name

Open `config.py` and set `SPREADSHEET_NAME` to the exact name of your Google Sheet.

## 7. Run the dashboard

```bash
python app.py
```

The dashboard will start at [http://127.0.0.1:8050](http://127.0.0.1:8050).

For production use:

```bash
gunicorn app:server -b 0.0.0.0:8050
```
