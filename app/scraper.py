from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from urllib.parse import urljoin, unquote
import re
import time
import requests
import os, traceback



def navigate_to_captcha(case_type, case_number, filing_year):
    service = Service(executable_path="../driver/chromedriver.exe")
    driver = webdriver.Chrome(service=service)
    driver.get("https://services.ecourts.gov.in/ecourtindia_v6/?p=casestatus/index")

    # Close validation popup (robust version)
    try:
        print("⏳ Waiting for validation popup...")

        # Wait for popup to appear (up to 5s)
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "validateError"))
        )

        # Now wait until the close button is clickable
        for _ in range(3):  # try up to 3 times
            try:
                close_btn = WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable((By.XPATH, '//div[@id="validateError"]//button[contains(@class, "btn-close")]'))
                )
                driver.execute_script("arguments[0].click();", close_btn)

                # Wait for style to become display: none
                WebDriverWait(driver, 5).until(
                    lambda d: d.execute_script(
                        "return document.getElementById('validateError')?.style.display === 'none'"
                    )
                )
                print("✅ Validation popup closed.")
                break
            except Exception as popup_try_error:
                print("🔁 Retry closing popup...")
                time.sleep(1)
        else:
            print("❌ Popup could not be closed after retries.")

    except TimeoutException:
        print("✅ No validation popup appeared.")
    except Exception as e:
        print("❌ Unexpected error while closing popup:", e)



    # Select Haryana and Faridabad
    Select(driver.find_element(By.ID, "sess_state_code")).select_by_value("14")
    time.sleep(1)
    Select(driver.find_element(By.ID, "sess_dist_code")).select_by_value("5")
    time.sleep(1)
    court_dropdown = Select(driver.find_element(By.ID, "court_complex_code"))
    for option in court_dropdown.options:
        if "District Court, Faridabad" in option.text:
            court_dropdown.select_by_visible_text(option.text)
            break

    time.sleep(1)
    driver.find_element(By.ID, "casenumber-tabMenu").click()
    time.sleep(2)

    # Fill the case form
    Select(driver.find_element(By.ID, "case_type")).select_by_value(case_type)
    driver.find_element(By.ID, "search_case_no").send_keys(case_number)
    driver.find_element(By.ID, "rgyear").send_keys(filing_year)

    from io import BytesIO

    # Save CAPTCHA image using Selenium's screenshot functionality
    captcha_img = driver.find_element(By.ID, "captcha_image")
    captcha_bytes = captcha_img.screenshot_as_png  # Get raw PNG bytes

    # Save to static folder
    static_path = os.path.join("static", "captcha.png")
    with open(static_path, "wb") as f:
        f.write(captcha_bytes)

    print("✅ CAPTCHA saved to", static_path)

    # Return driver and URL for use in HTML
    return driver, "/static/captcha.png"


def extract_case_details(driver, captcha_text):
    try:
        print("🧠 Filling CAPTCHA...")

        # Fill in CAPTCHA
        captcha_input = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "case_captcha_code"))
        )
        captcha_input.clear()
        captcha_input.send_keys(captcha_text)

        # Click the "Go" button
        go_button = WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable((By.XPATH, '//button[@onclick="submitCaseNo();"]'))
        )
        go_button.click()
        print("⏳ Submitted CAPTCHA... waiting for result list...")

        # Wait for the result summary table to appear
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "dispTable"))
        )
        time.sleep(3)

        # Click the first "View" link to open detailed view
        print("👁️ Clicking 'View' to load case details...")
        view_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//table[@id="dispTable"]//a[contains(text(), "View")]'))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", view_button)
        driver.execute_script("arguments[0].click();", view_button)
        time.sleep(5)

        # Wait for detailed case info to appear
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "Petitioner_Advocate_table"))
        )

        # Petitioner/Respondent
        pet_table = driver.find_element(By.XPATH, '//table[@class="table table-bordered Petitioner_Advocate_table"]')
        resp_table = driver.find_element(By.XPATH, '//table[@class="table table-bordered Respondent_Advocate_table"]')
        petitioner_raw = pet_table.text.strip()
        respondent_raw = resp_table.text.strip()

        pet_lines = petitioner_raw.split("\n")
        petitioner = pet_lines[0] if pet_lines else "Not found"
        pet_advocate = pet_lines[1].replace("Advocate-", "").strip() if len(pet_lines) > 1 else "Not found"
        respondent = respondent_raw

        # Filing Date
        filing_date = driver.find_element(
            By.XPATH,
            '//table[@class="table case_details_table table-bordered"]//td[label[contains(text(), "Filing Date")]]/following-sibling::td[1]'
        ).text.strip()

        # Next Hearing Date
        try:
            next_hearing_date = driver.find_element(
                By.XPATH, '//*[@id="CScaseNumber"]/table[2]/tbody/tr[2]/td[2]'
            ).text.strip()
        except:
            next_hearing_date = "Not found"

        # Orders
        order_entries = []
        order_rows = driver.find_elements(By.XPATH, '//table[contains(@class, "order_table")]//tr[position()>1]')
        for row in order_rows:
            tds = row.find_elements(By.TAG_NAME, 'td')
            if len(tds) >= 3:
                order_date = tds[1].text.strip()
                anchor = tds[2].find_element(By.TAG_NAME, 'a')
                onclick = anchor.get_attribute("onclick")
                match = re.search(r"filename=(/[^&'\"]+)", onclick)
                if match:
                    url = urljoin("https://services.ecourts.gov.in/ecourtindia_v6/", unquote(match.group(1)))
                    order_entries.append({"date": order_date, "url": url})

        latest_order_url = order_entries[-1]["url"] if order_entries else None

        print("✅ Final case data extracted.")
        return {
            "petitioner": petitioner,
            "petitioner_advocate": pet_advocate,
            "respondent": respondent,
            "filing_date": filing_date,
            "next_hearing_date": next_hearing_date,
            "latest_order_url": latest_order_url,
            "all_orders": order_entries
        }

    except Exception as e:
        import traceback
        print("❌ Error during case extraction:", str(e))
        traceback.print_exc()
        return None

    finally:
        driver.quit()


