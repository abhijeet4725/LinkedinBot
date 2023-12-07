from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
import time
import re
import json
import logging


class Bot:
    def __init__(self, data):
        self.email = data['email']
        self.password = data['password']
        self.search_word = data['search_word']
        self.location = data['location']
        self.driver = webdriver.Chrome()

    def login(self):
        self.driver.get("https://www.linkedin.com/login")

        email_locator = self.driver.find_element(By.ID, "username")
        email_locator.clear()
        email_locator.send_keys(self.email)

        password_locator = self.driver.find_element(By.ID, "password")
        password_locator.clear()
        for char in self.password:
            password_locator.send_keys(char)
            time.sleep(0.1)

        ActionChains(self.driver).move_to_element(email_locator).perform()

        logging.info(f"Entered Password: {self.password}")

        password_locator.send_keys(Keys.RETURN)

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, "Jobs"))
        )

    def job(self):
        jobs = self.driver.find_element(By.XPATH, "//header[@id='global-nav']//nav["
                                                  "@class='global-nav__nav']/ul//span[@title='Jobs']")
        jobs.click()
        time.sleep(2)

        search = self.driver.find_element(By.XPATH, "/html//div[@id='global-nav-search']/div/div[2]/div[2]/div["
                                                    "@class='jobs-search-box__inner']//input[@role='combobox']")
        search.clear()
        search.send_keys(self.search_word)
        time.sleep(2)

        search_place = self.driver.find_element(By.XPATH, "/html//div[@id='global-nav-search']/div/div[2]/div[3]/div["
                                                          "@class='jobs-search-box__inner']//input[@role='combobox']")
        search_place.clear()

        search_place.send_keys(self.location)

        search.send_keys(Keys.RETURN)

    def filter(self):

        easy_apply_button = self.driver.find_element(By.XPATH, "//div[@id='search-reusables__filters-bar']/ul"
                                                               "//button[@role='radio']")
        easy_apply_button.click()
        time.sleep(1)

    def find_offers(self):
        global total_jobs

        total_results = self.driver.find_element(By.XPATH, "/html//main[@id='main']/div/div[1]/header//span[1]")
        total_results_int = int(total_results.text.split(' ', 1)[0].replace(",", ""))
        print(total_results_int)

        time.sleep(2)
        current_page = self.driver.current_url
        results = self.driver.find_elements(By.CLASS_NAME,
                                            "ember-view   jobs-search-results__list-item occludable-update p0 "
                                            "relative scaffold-layout__list-item")

        for result in results:
            hover = ActionChains(self.driver).move_to_element(result)
            hover.perform()
            titles = result.find_element(By.CLASS_NAME, "disabled ember-view job-card-container__link "
                                                        "job-card-list__title")

            for title in titles:
                self.submit_apply(title)
        if total_results_int > 24:
            time.sleep(2)

            find_pages = self.driver.find_element(By.ID, "ember1302")
            total_pages = find_pages[-1].text
            total_pages_int = int(re.sub(r"[^\d.]", "", total_pages))
            get_last_page = self.driver.find_element(By.ID, "ember1302" + str(total_pages_int) + "']")
            get_last_page.send_keys(Keys.RETURN)
            time.sleep(2)
            last_page = self.driver.current_url
            total_jobs = int(last_page.split('start=', 1)[1])

        for page_number in range(25, total_jobs + 25, 25):
            self.driver.get(current_page + '&start=' + str(page_number))
            time.sleep(2)
            results_ext = self.driver.find_elements(By.CLASS_NAME,
                                                    "ember-view   jobs-search-results__list-item occludable-update p0 "
                                                    "relative scaffold-layout__list-item")
            for result_ext in results_ext:
                for result in results:
                    hover_ext = ActionChains(self.driver).move_to_element(result_ext)
                    hover_ext.perform()
                    titles = result_ext.find_element(By.CLASS_NAME, "disabled ember-view job-card-container__link "
                                                                    "job-card-list__title")

                    for title_ext in titles_ext:
                        self.submit_apply(title_ext)
        else:
            self.close_session()

    def submit_apply(self, job_add):

        print('You are applying to the position of: ', job_add.text)
        job_add.click()
        time.sleep(2)

        try:
            in_apply = self.driver.find_element(By.XPATH, "/html//main[@id='main']/div["
                                                          "@class='scaffold-layout__list-detail-inner']/div[2]/div["
                                                          "@class='jobs-search__job-details--wrapper']/div[2]/div["
                                                          "@class='job-view-layout jobs-details']/div[1]/div//div["
                                                          "@class='mt5']/div[@class='display-flex']/div/div["
                                                          "@class='jobs-apply-button--top-card']/button/span["
                                                          "@class='artdeco-button__text']")
            in_apply.click()
        except NoSuchElementException:
            print('You already applied to this job, go to next...')
            pass
        time.sleep(1)

        try:
            submit = self.driver.find_element(By.XPATH, "ember616")
            submit.send_keys(Keys.RETURN)
        except NoSuchElementException:
            print('Not a direct application, going to next...')
            try:
                next_button = self.driver.find_element(By.ID, "ember590")
                next_button.click()
                time.sleep(2)

                # Click on "Review" button (if it exists)
                try:
                    review_button = self.driver.find_element(By.XPATH, "//div[@id='artdeco-modal-outlet']/div/div["
                                                                       "@role='dialog']/div[2]//button["
                                                                       "@class='artdeco-button artdeco-button--2 "
                                                                       "artdeco-button--primary ember-view']/span["
                                                                       "@class='artdeco-button__text']")
                    review_button.click()
                    time.sleep(2)  # Add a delay to allow the page to load after clicking "Review"
                except NoSuchElementException:
                    print('No "Review" button found, proceeding without review...')

                # After clicking "Review," attempt to find and click the "Submit" button
                submit = self.driver.find_element(By.ID, "ember616")
                submit.click()
            except NoSuchElementException:
                print('No "Next" button found, proceeding without submission...')
                try:
                    discard = self.driver.find_element(By.ID, "ember635")
                    discard.send_keys(Keys.RETURN)
                    time.sleep(1)
                    discard_confirm = self.driver.find_element(By.CLASS_NAME, "artdeco-button__text")
                    discard_confirm.send_keys(Keys.RETURN)
                    time.sleep(1)
                except NoSuchElementException:
                    pass
            time.sleep(1)

    def close_session(self):

        print('End of the session, see you later!')
        self.driver.close()

    def apply(self):

        self.driver.maximize_window()
        self.login()
        time.sleep(5)
        self.job()
        time.sleep(5)
        self.filter()
        time.sleep(2)
        self.find_offers()


with open("config.json") as File:
    data = json.load(File)
bot = Bot(data)

bot.apply()
