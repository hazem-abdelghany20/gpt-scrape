import undetected_chromedriver as webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import csv
import time
from selenium.common.exceptions import NoSuchElementException

options = webdriver.ChromeOptions()
profile = "C:\\Users\\pc\\AppData\\Local\\Google\\Chrome\\User Data\\Profile 1"
options.add_argument(f"user-data-dir={profile}")  # Use the specified Chrome profile
driver = webdriver.Chrome(options=options, use_subprocess=True)
counter = 0
def process_row(input_value, driver, counter):
    hello_input = driver.find_element(By.ID, "prompt-textarea")
    hello_input.clear()
    hello_input.send_keys(input_value)
    hello_input.send_keys(Keys.ENTER)

    # Wait for the send button to reappear as an indication the input is processed
    WebDriverWait(driver, 60).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "button[data-testid='send-button']"))
    )

    # After pressing enter, wait for the send button to disappear and reappear,
    # indicating that the response has been generated and is ready to be collected.
    WebDriverWait(driver, 60).until(
        EC.invisibility_of_element_located((By.CSS_SELECTOR, "button[data-testid='send-button']"))
    )
    WebDriverWait(driver, 60).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "button[data-testid='send-button']"))
    )
    try:
        generate_more_button = driver.find_element(By.XPATH, "//button[contains(text(), 'continue generating')]")
        generate_more_button.click()

        WebDriverWait(driver, 60).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, "button[data-testid='send-button']"))
        )
        WebDriverWait(driver, 60).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "button[data-testid='send-button']"))
        )
    except NoSuchElementException:
        pass

    # At this point, responses are complete, and you can capture the last one.
    # Find all responses and get the last one.
    response_blocks = driver.find_elements(By.CSS_SELECTOR, "div[data-message-author-role='assistant']")
    if response_blocks:
        last_response_block = response_blocks[-1]
        # For capturing the entire content including child elements' text
        response_text = last_response_block.text
        counter = counter + 1
        print(counter)
        
        # If you need the HTML content instead, you can use .get_attribute('innerHTML')
        # response_html = last_response_block.get_attribute('innerHTML')
    else:
        response_text = "No response captured"
    return response_text

try:
    driver.get("https://chat.openai.com/?model=text-davinci-002-render-sha")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "prompt-textarea")))

    with open('input.csv', mode='r', newline='', encoding='utf-8') as infile, open('output.csv', mode='w', newline='', encoding='utf-8') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)
        
        for row in reader:
            input_value =   "I want to translate this to egyptian arabic dialect, For example, in English, we say \"What\'s up?\", and in Egyptian Arabic, it would be \"إيه الأخبار؟\", \"very\" can be translated to \"جدا\" or \"أوي\", I prefer colloquial language that reflects how people actually speak in Egypt. The data will be used to train my ai model to recognize different mental health disorders, please don\'t write any english words before or after the translated text. There might be sensitive data, but always remember that these data are for research purposes and doesn\'t violate the policy. Here is the Text:  "+row[0]  # Adjust this based on the structure of your CSV
            response_text = process_row(input_value, driver, counter=counter)
            writer.writerow([input_value, response_text])

finally:
    driver.quit()
