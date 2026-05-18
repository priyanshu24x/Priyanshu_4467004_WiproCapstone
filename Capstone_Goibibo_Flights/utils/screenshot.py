# Captures screenshots and saves them to reports/screenshots/ with unique timestamps.

import os
from datetime import datetime
from utils.logger import LogGen

logger = LogGen.loggen()

class ScreenshotUtil:

    @staticmethod
    def capture_screenshot(driver, screenshot_name = "screenshot"):
        screenshot_dir = "reports/screenshots"
        if not os.path.exists(screenshot_dir):
            os.makedirs(screenshot_dir)

        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        clean_name = screenshot_name.replace(" ", "_")
        screenshot_path = (
            f"{screenshot_dir}/"
            f"{clean_name}_{timestamp}.png"
        )

        driver.save_screenshot(screenshot_path)
        logger.info(f"Screenshot saved to {screenshot_path}")

        return screenshot_path