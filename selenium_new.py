from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from robotexclusionrulesparser import RobotExclusionRulesParser
import time
def web_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--verbose")
    options.add_argument('--no-sandbox')
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument("--window-size=1920, 1200")
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)
    return driver
def fetch_dynamic_content(url):
    # Check if the website is crawlable
    parser = RobotExclusionRulesParser()
    parser.fetch(url + '/robots.txt')
    if not parser.is_allowed('*', url):
        print("Website is not crawlable according to the robots.txt rules.")
        return None

    crawl_delay = parser.get_crawl_delay('*')
    
    if crawl_delay:
        print(f"Crawl delay specified in robots.txt: {crawl_delay} seconds.")
        time.sleep(crawl_delay)

    
    driver =  web_driver()

    driver.get(url)

    # Wait for the page to fully load
    wait = WebDriverWait(driver, 15)  # Set the timeout duration to 30 seconds
    wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

    # Check if the dynamic content is within an iframe and switch to it if necessary
    # driver.switch_to.frame('iframe_name')

    try:
        # Wait for the visibility of the dynamic element
        element = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@class="dynamic-element"]')))

        # Scroll to the dynamic element to ensure its visibility
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        if not crawl_delay == None:
            time.sleep(crawl_delay)
        html_content = driver.page_source
    except TimeoutException:
        print("Dynamic element not found or not visible within the given timeout duration.")
        html_content = driver.page_source

    driver.quit()

    return html_content

def save_html_content(html_content):
    if html_content:
        with open("/content/Web_scrapping_project/index.html", "w", encoding="utf-8") as file:
            file.write(html_content)
        print("HTML content saved to index.html")
    else:
        print("Failed to retrieve dynamic content. Saving the HTML content retrieved so far.")
        with open("/content/Web_scrapping_project/index.html", "w", encoding="utf-8") as file:
            file.write(html_content)

# website_url = 'http://www.green-local.k12.oh.us/district/district-office-staff'
website_url = "https://www.jones.k12.ms.us/en-US/staff"
html_content = fetch_dynamic_content(website_url)
save_html_content(html_content)
