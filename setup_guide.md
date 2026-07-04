# Returning Tonight — Continue From Here

You have already completed Steps 1, 2, and 3. Your next step is **Step 4**.

Before continuing, make sure you have the latest code. Open Command Prompt and run:
```
cd Documents\pharmacy-dashboard
git pull
```

Then continue with Step 4 below.

---

# Pharmacy POS Dashboard — Setup Guide

Follow these steps in order. The whole process takes about 15-20 minutes.

---

## Step 1: Install Python on your computer

If you don't already have Python installed:

### Windows:
1. Open your browser and go to https://www.python.org/downloads/
2. Click the big yellow **"Download Python 3.x.x"** button
3. Run the installer
4. **IMPORTANT:** On the first screen, tick the checkbox that says **"Add Python to PATH"** at the bottom
5. Click **"Install Now"**
6. Once finished, open **Command Prompt** (search "cmd" in the Start menu)
7. Type `python --version` and press Enter — you should see a version number

### Mac:
1. Open **Terminal** (search "Terminal" in Spotlight)
2. Type `python3 --version` — if it shows a version, you're good
3. If not, go to https://www.python.org/downloads/ and install it

---

## Step 2: Download the dashboard code

1. Open **Command Prompt** (Windows) or **Terminal** (Mac)
2. Navigate to where you want to keep the dashboard. For example:
   ```
   cd Documents
   ```
3. Clone the repository:
   ```
   git clone https://github.com/Jason-Markey/Jason-Markey.git pharmacy-dashboard
   ```
4. Go into the folder:
   ```
   cd pharmacy-dashboard
   ```

If you don't have git installed, you can also download the code as a ZIP from GitHub and extract it.

---

## Step 3: Install the required Python packages

In the same Command Prompt / Terminal window (inside the pharmacy-dashboard folder):

### Windows:
```
pip install -r requirements.txt
```

### Mac:
```
pip3 install -r requirements.txt
```

This installs Dash (for the dashboard), Plotly (for charts), Pandas (for data), and gspread (for reading Google Sheets). It may take a minute or two.

---

## Step 4: Create a Google Cloud project

This gives you free access to the Google Sheets API (no credit card required).

1. Open your browser and go to: https://console.cloud.google.com/
2. Sign in with the **same Google account** that owns your spreadsheet
3. At the very top of the page, click the project dropdown (it might say "Select a project" or show an existing project name)
4. In the popup, click **"New Project"** in the top right
5. Name it: `Pharmacy Dashboard`
6. Leave the organisation/location as default
7. Click **"Create"**
8. Wait a few seconds, then make sure this new project is selected in the top dropdown

---

## Step 5: Enable the Google Sheets API and Google Drive API

1. In the Google Cloud Console, click the **hamburger menu** (three horizontal lines, top left)
2. Go to **APIs & Services** > **Library**
3. In the search bar, type **Google Sheets API**
4. Click on **Google Sheets API** in the results
5. Click the blue **"Enable"** button
6. Go back to the Library (use the back arrow or navigate again)
7. Search for **Google Drive API**
8. Click on **Google Drive API**
9. Click **"Enable"**

Both APIs should now show as enabled.

---

## Step 6: Create a Service Account

A service account is like a robot user that the dashboard uses to read your spreadsheet. It can only read — it cannot edit or delete anything.

1. In the Google Cloud Console, click the **hamburger menu** (three lines, top left)
2. Go to **APIs & Services** > **Credentials**
3. At the top of the page, click **"+ Create Credentials"**
4. Select **"Service Account"**
5. Fill in:
   - Service account name: `pharmacy-dashboard`
   - Service account ID: (auto-fills, leave it)
   - Description: `Reads pharmacy spreadsheet for dashboard`
6. Click **"Create and Continue"**
7. For "Grant this service account access to project" — **skip this**, just click **"Continue"**
8. For "Grant users access to this service account" — **skip this**, just click **"Done"**

---

## Step 7: Download the credentials file

1. You should now see your service account listed on the Credentials page
2. Click on the service account name (e.g. `pharmacy-dashboard@pharmacy-dashboard-xxxxx.iam.gserviceaccount.com`)
3. Click the **"Keys"** tab at the top
4. Click **"Add Key"** > **"Create New Key"**
5. Select **"JSON"** and click **"Create"**
6. A `.json` file will automatically download to your Downloads folder
7. **IMPORTANT:** Note the **email address** shown for this service account (something like `pharmacy-dashboard@pharmacy-dashboard-xxxxx.iam.gserviceaccount.com`). You'll need this in Step 9.

---

## Step 8: Store the credentials file securely

The credentials file must be stored in a specific location so the dashboard can find it.

### Windows:
1. Open **File Explorer**
2. Navigate to your user folder (usually `C:\Users\YourName\`)
3. Create a new folder called `.pharmacy-dashboard` (note the dot at the start)
   - If Windows won't let you name a folder starting with a dot, open Command Prompt and type:
     ```
     mkdir %USERPROFILE%\.pharmacy-dashboard
     ```
4. Move the downloaded JSON file into this folder
5. Rename it to `credentials.json`

The final path should be: `C:\Users\YourName\.pharmacy-dashboard\credentials.json`

### Mac:
Open Terminal and run:
```
mkdir -p ~/.pharmacy-dashboard
mv ~/Downloads/*.json ~/.pharmacy-dashboard/credentials.json
```

---

## Step 9: Share your Google Sheet with the service account

This is how the dashboard gets permission to read your spreadsheet.

1. Open your pharmacy spreadsheet in **Google Sheets** in your browser
2. Click the **"Share"** button (top right, green button)
3. In the "Add people" field, paste the **service account email address** from Step 7
   (e.g. `pharmacy-dashboard@pharmacy-dashboard-xxxxx.iam.gserviceaccount.com`)
4. Change the permission to **"Viewer"** (it only needs to read, not edit)
5. Uncheck "Notify people" (it's a robot, no need to email it)
6. Click **"Share"**

---

## Step 10: Set your spreadsheet name in the config

1. In Google Sheets, look at the **name of your spreadsheet** at the very top left of the page (e.g. it might be called "Pacific Fair POS Data" or similar)
2. Open the file `config.py` in the dashboard folder with any text editor (Notepad, TextEdit, VS Code, etc.)
3. Find this line near the top:
   ```python
   SPREADSHEET_NAME = "YOUR_SPREADSHEET_NAME_HERE"
   ```
4. Replace `YOUR_SPREADSHEET_NAME_HERE` with the exact name of your spreadsheet. For example:
   ```python
   SPREADSHEET_NAME = "Pacific Fair POS Data"
   ```
5. Save the file

---

## Step 11: Run the dashboard

1. Open **Command Prompt** (Windows) or **Terminal** (Mac)
2. Navigate to the dashboard folder:
   ```
   cd Documents/pharmacy-dashboard
   ```
3. Start the dashboard:

   **Windows:**
   ```
   python app.py
   ```

   **Mac:**
   ```
   python3 app.py
   ```

4. You should see something like:
   ```
   Dash is running on http://127.0.0.1:8050/
   ```
5. Open your browser and go to: **http://127.0.0.1:8050**
6. Your dashboard should load with your data!

---

## Step 12: Using the dashboard day-to-day

- **To open the dashboard:** Run `python app.py` from the dashboard folder, then open http://127.0.0.1:8050 in your browser
- **Data refreshes automatically** every 5 minutes while the dashboard is open
- **To stop the dashboard:** Go back to the Command Prompt / Terminal and press `Ctrl + C`
- **You do NOT need to export anything** from Google Sheets — the dashboard reads it directly

---

## Troubleshooting

**"ModuleNotFoundError: No module named 'dash'"**
- You need to install the requirements. Run: `pip install -r requirements.txt`

**"FileNotFoundError: credentials.json"**
- The credentials file is not in the right location. Check Step 8.

**"gspread.exceptions.SpreadsheetNotFound"**
- The spreadsheet name in `config.py` doesn't match exactly. Check Step 10.
- Make sure you shared the sheet with the service account email (Step 9).

**"gspread.exceptions.APIError: 403"**
- The Google Sheets API or Google Drive API may not be enabled. Check Step 5.

**Dashboard loads but shows "No data"**
- Check that your year tab names in the spreadsheet match the ones in `config.py` (25/26, 24/25, etc.)
- Make sure the data starts at row 185 in each year tab
