import time
import re
import json
import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image
import pytesseract
import platform

# Set path to Tesseract for Windows, otherwise skip
if platform.system().lower() == 'windows':
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def capture_screenshot(username):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    if platform.system() != 'Windows':
        options.binary_location = "/usr/bin/chromium"
        
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        profile_url = f"https://www.kaggle.com/{username}/competitions"
        driver.get(profile_url)
        time.sleep(5)  # Wait for full load

        screenshot_path = "kaggle_screenshot.png"
        driver.save_screenshot(screenshot_path)

        return screenshot_path
    finally:
        driver.quit()

def extract_competitions_from_text(text):
    # Find pattern like: Competitions (3)
    match = re.search(r'Competitions\s*\((\d+)\)', text)
    if match:
        return int(match.group(1))
    return 0

def extract_active_competitions_from_image(image_path):
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)

    print("📄 Extracted Text from Image:")
    print(text)

    return extract_competitions_from_text(text)

# ----------- Streamlit UI ------------

def main():
    st.title("Kaggle Competitions Scraper")

    # Get username input from user
    username = st.text_input("Enter your Kaggle Username:")

    if username:
        st.write(f"Fetching competitions for {username}...")

        screenshot = capture_screenshot(username)
        competition_count = extract_active_competitions_from_image(screenshot)

        st.subheader(f"🏁Competitions participated by {username}: {competition_count}")
        output_json = {
            "username": username,
            "active_competition_count": competition_count ,
        }
        st.download_button(
            label="📥 Download JSON",
            data=json.dumps(output_json, indent=4),
            file_name=f"{username}_competitions.json",
            mime="application/json"
        )
    else:
        st.write("Please enter a username to see the competitions.")

if __name__ == "__main__":
    main()
