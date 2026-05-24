import os
from datetime import datetime
import allure  # Added for Allure Report Integration
from utils.logger import LogGen

logger = LogGen.loggen()



class ScreenshotUtil:

    @staticmethod
    def capture_screenshot(driver, screenshot_name="screenshot"):
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

        # Core Upgrade: Attach the file directly into the current active Allure step context
        try:
            allure.attach.file(
                screenshot_path,
                name=clean_name,
                attachment_type=allure.attachment_type.PNG
            )
            logger.info(f"Successfully embedded '{clean_name}' into Allure timeline tracker.")
        except Exception as e:
            logger.warning(f"Could not attach snapshot to Allure context: {e}")

        return screenshot_path