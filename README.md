# 🧾 Court Data Fetcher

A lightweight web app that fetches and displays case metadata and the latest order PDFs for cases listed in the **Faridabad District Court, Haryana** from the eCourts portal. This tool simplifies public access to case information via a user-friendly interface.

---

## 📍 Target Court

This project specifically targets the **District Court of Faridabad, Haryana** using the [eCourts portal](https://services.ecourts.gov.in/ecourtindia_v6/). Court selection is hardcoded into the scraper logic via Selenium.

---

## ⚙️ Setup Instructions

### 1. Clone the Repository

### 2. Create and Activate Virtual Environment

### 3. Install Dependencies

### 4. Add the ChromeDriver
Place `chromedriver.exe` inside the `driver/` folder. Ensure the version matches your installed Chrome browser.

### 5. Set Environment Variables
Create a `.env` file at the root (optional) for configuration:

### 6. Run the App

Then open your browser to:  
[http://localhost:5000](http://localhost:5000)

---

## 🔒 CAPTCHA Strategy (Fully Legal ✅)

This app **does not bypass or solve CAPTCHA automatically**. Instead:
- It **screenshots the CAPTCHA image** from the court’s portal using Selenium
- The **user manually enters** the correct CAPTCHA
- The entered CAPTCHA is submitted via Flask backend to continue scraping

✅ **This approach respects eCourts' legal and ethical constraints.**  
❌ No OCR or automated CAPTCHA solving is involved.

---

## 🗃️ Features

- Select **Case Type**, **Case Number**, and **Filing Year**
- Automatically fills in **State, District, and Court (Faridabad)**
- Displays:
  - Petitioner & Respondent
  - Filing date & Next hearing
  - List of orders (only most recent PDF is downloadable)
- **Logs** every case query to an SQLite database (`case_queries.db`)
- User-friendly **error messages** for:
  - Incorrect CAPTCHA
  - No matching case found
  - Server issues or downtime
- Fully responsive **Bootstrap UI**

---

## 📁 Project Structure
app/
├── templates/ # HTML templates
│ ├── form.html
│ ├── captcha_form.html
│ ├── result.html
│ └── error.html
├── static/
│ └── orders/ # Downloaded PDF files
│ └── captcha.png # CAPTCHA image shown to user
├── driver/
│ └── chromedriver.exe # ChromeDriver (Windows only)
├── app.py # Flask app entrypoint
├── scraper.py # Selenium automation logic
├── database.py # SQLite logging helper
├── case_queries.db # SQLite database
requirements.txt
.env

## 📝 To Do / Enhancements

- Add multi-court or multi-district support
- Add search history UI for logged users
- Add PDF previews for older orders (currently only shows latest)

---

## 📜 License

This project is intended for educational/demo purposes only and is not affiliated with any government body.


