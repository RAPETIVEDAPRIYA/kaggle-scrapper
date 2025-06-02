import time
import re
import json
import platform
import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PIL import Image
import pytesseract

# Optional: set path for Windows Tesseract
if platform.system().lower() == 'windows':
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def capture_screenshot(username):
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=options)

    try:
        profile_url = f"https://www.kaggle.com/{username}/competitions"
        driver.get(profile_url)
        time.sleep(5)  # let the page load

        screenshot_path = "kaggle_screenshot.png"
        driver.save_screenshot(screenshot_path)
        return screenshot_path
    finally:
        driver.quit()


def extract_activity_from_image(image_path):
    image = Image.open(image_path)

    # Crop region covering Activity section (adjusted from screenshot)
    width, height = image.size
    crop_box = (int(width * 0.72), int(height * 0.48), int(width * 0.95), int(height * 0.75))
    cropped_image = image.crop(crop_box)

    # Optional: for debugging
    # cropped_image.show()

    # OCR
    text = pytesseract.image_to_string(cropped_image)
    print("🔍 OCR Text:\n", text)

    # Extract numbers
    solo = re.search(r'(\d+)\s+competitions\s+solo', text)
    team = re.search(r'(\d+)\s+competitions\s+in\s+a\s+team', text)
    hosted = re.search(r'(\d+)\s+competitions\s+hosted', text)

    return {
        "competitions_solo": int(solo.group(1)) if solo else 0,
        "competitions_team": int(team.group(1)) if team else 0,
        "competitions_hosted": int(hosted.group(1)) if hosted else 0
    }


# ----------- Streamlit UI ------------

def main():
    st.title("🧠 Kaggle Competition Activity Extractor")

    username = st.text_input("Enter your Kaggle Username (e.g., vedapr471):")

    if username:
        st.info(f"Fetching activity data for user: {username}")
        screenshot_path = capture_screenshot(username)
        activity = extract_activity_from_image(screenshot_path)

        st.success("✅ Activity Data Extracted:")
        st.write(f"- 🏁 Competitions Solo: {activity['competitions_solo']}")
        st.write(f"- 👥 Competitions in a Team: {activity['competitions_team']}")
        st.write(f"- 🛠 Competitions Hosted: {activity['competitions_hosted']}")

        # Download JSON
        output_json = {
            "username": username,
            "competitions_solo": activity["competitions_solo"],
            "competitions_team": activity["competitions_team"],
            "competitions_hosted": activity["competitions_hosted"]
        }

        st.download_button(
            label="📥 Download JSON",
            data=json.dumps(output_json, indent=4),
            file_name=f"{username}_activity.json",
            mime="application/json"
        )
    else:
        st.warning("Please enter a Kaggle username.")


if __name__ == "__main__":
    main()
