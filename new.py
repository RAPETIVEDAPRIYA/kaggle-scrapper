import time
import re
import json
import platform
import pytesseract
from PIL import Image
from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import FileResponse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

app = FastAPI()

# Tesseract path for Windows
if platform.system().lower() == 'windows':
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def capture_screenshot(username: str) -> str:
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
        time.sleep(5)
        screenshot_path = "kaggle_screenshot.png"
        driver.save_screenshot(screenshot_path)
        return screenshot_path
    finally:
        driver.quit()


def extract_activity_from_image(image_path: str) -> dict:
    image = Image.open(image_path)
    width, height = image.size
    crop_box = (int(width * 0.72), int(height * 0.48), int(width * 0.95), int(height * 0.75))
    cropped_image = image.crop(crop_box)
    text = pytesseract.image_to_string(cropped_image)

    solo = re.search(r'(\d+)\s+competitions\s+solo', text)
    team = re.search(r'(\d+)\s+competitions\s+in\s+a\s+team', text)
    hosted = re.search(r'(\d+)\s+competitions\s+hosted', text)

    return {
        "competitions_solo": int(solo.group(1)) if solo else 0,
        "competitions_team": int(team.group(1)) if team else 0,
        "competitions_hosted": int(hosted.group(1)) if hosted else 0
    }


@app.get("/download-activity/{username}")
def download_kaggle_activity(username: str):
    try:
        screenshot_path = capture_screenshot(username)
        activity = extract_activity_from_image(screenshot_path)

        data = {
            "username": username,
            **activity
        }

        json_path = f"{username}_activity.json"
        with open(json_path, "w") as f:
            json.dump(data, f, indent=4)

        return FileResponse(
            path=json_path,
            filename=json_path,
            media_type="application/json"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
