from flask import Flask, render_template, request, session, redirect, url_for
from scraper import navigate_to_captcha, extract_case_details
from database import init_db, log_case_query
init_db()  # Called on app startup

import uuid

app = Flask(__name__)
app.secret_key = "secret123"  # required for session

# Global store for webdriver instances (keyed by session id)
drivers = {}

@app.route('/')
def home():
    return render_template('form.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    case_type = request.form['case_type']
    case_number = request.form['case_number']
    filing_year = request.form['filing_year']

    # Start browser and get CAPTCHA
    driver, captcha_path = navigate_to_captcha(case_type, case_number, filing_year)

    if not captcha_path:
        return "Failed to load CAPTCHA."

    # Create unique ID for this session (stored in cookie)
    user_id = str(uuid.uuid4())
    session['user_id'] = user_id

    # Store driver instance in memory
    drivers[user_id] = driver

    # Store form data (used only for reference or retry)
    session['case_type'] = case_type
    session['case_number'] = case_number
    session['filing_year'] = filing_year

    return render_template('captcha_form.html', captcha_path=captcha_path)

@app.route('/verify', methods=['POST'])
def verify():
    captcha_input = request.form['captcha']
    user_id = session.get('user_id')

    if not user_id or user_id not in drivers:
        return "⚠️ Session expired or invalid. Please try again."

    driver = drivers.pop(user_id)  # remove from memory after use

    # Read form data again for logging
    case_type = session.get('case_type', '')
    case_number = session.get('case_number', '')
    filing_year = session.get('filing_year', '')

    result = extract_case_details(driver, captcha_input)

    status = "success" if result else "fail"
    import json
    log_case_query(case_type, case_number, filing_year, captcha_input, status, json.dumps(result, indent=2))

    

    if result:
        return render_template('result.html', result=result)
    else:
        return "❌ Failed to extract case data. Try again."

if __name__ == '__main__':
    app.run(debug=True)
