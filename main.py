import csv
import logging
import os
import pdb
import random
import re
import time
from datetime import datetime, timedelta
from urllib.request import urlopen

import emoji
import pandas as pd
import yaml
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

# set BREAKPOINT to 1 for debug or PYTHONBREAKPOINT to 0 to turn off debugging
os.environ["PYTHONBREAKPOINT"] = "0"

# breakpoint()

log = logging.getLogger(__name__)
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))


def setupLogger() -> None:
    dt: str = datetime.strftime(datetime.now(), "%m_%d_%y %H_%M_%S ")

    if not os.path.isdir("./logs"):
        os.mkdir("./logs")

    # TODO need to check if there is a log dir available or not
    logging.basicConfig(
        filename=("./logs/" + str(dt) + "applyJobs.log"),
        filemode="w",
        format="%(asctime)s::%(lineno)d::%(name)s::%(levelname)s::%(message)s",
        datefmt="./logs/%d-%b-%y %H:%M:%S",
    )
    log.setLevel(logging.INFO)
    c_handler = logging.StreamHandler()
    c_handler.setLevel(logging.DEBUG)
    c_format = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s", "%H:%M:%S"
    )
    c_handler.setFormatter(c_format)
    log.addHandler(c_handler)


class DigitalAssistant:
    setupLogger()
    # MAX_SEARCH_TIME is 10 hours by default, feel free to modify it
    MAX_SEARCH_TIME = 10 * 60 * 60

    def __init__(
        self,
        username,
        password,
        phone_number,
        salarynumeric,
        resumename,
        uploads={},
        filename="output.csv",
        blacklist_companies=[],
        blacklist_titles=[],
        technicalskills={},
        radio_and_dropdowns={},
    ) -> None:

        log.info("Welcome to Easy Apply Bot")
        dirpath: str = os.getcwd()
        log.info("current directory is : " + dirpath)

        self.filename: str = filename
        self.uploads = uploads
        past_ids: list | None = self.get_appliedIDs(filename)
        self.appliedJobIDs: list = past_ids if past_ids != None else []
        self.options = self.browser_options()
        self.browser = driver
        self.actions = ActionChains(self.browser)
        self.wait = WebDriverWait(self.browser, 30)
        self.blacklist_companies = blacklist_companies
        self.blacklist_titles = blacklist_titles
        self.start_linkedin(username, password)
        self.phone_number = phone_number
        self.techexperience = technicalskills
        self.salary_number = salarynumeric
        self.radiodropdowns = radio_and_dropdowns
        self.resume_name = resumename

    def get_appliedIDs(self, filename) -> list | None:
        try:
            df = pd.read_csv(
                filename,
                header=None,
                names=[
                    "timestamp",
                    "jobID",
                    "job",
                    "company",
                    "attempted",
                    "result",
                ],
                lineterminator="\n",
                encoding="cp1252",
            )  # cp1252

            df["timestamp"] = pd.to_datetime(
                df["timestamp"], format="%Y-%m-%d %H:%M:%S"
            )
            df = df[df["timestamp"] > (datetime.now() - timedelta(days=2))]
            jobIDs: list = list(df.jobID)
            log.debug(f"found {jobIDs}")
            log.info(f"{len(jobIDs)} jobIDs found")
            return jobIDs
        except Exception as e:
            log.info(
                str(e) + "   jobIDs could not be loaded from CSV {}".format(filename)
            )
            return None

    def get_applied_companies(self, filename) -> list | None:
        try:
            df = pd.read_csv(
                filename,
                header=None,
                names=[
                    "timestamp",
                    "jobID",
                    "job",
                    "company",
                    "attempted",
                    "result",
                ],
                lineterminator="\n",
                encoding="cp1252",
            )  # cp1252

            df["timestamp"] = pd.to_datetime(
                df["timestamp"], format="%Y-%m-%d %H:%M:%S"
            )
            df = df[df["timestamp"] > (datetime.now() - timedelta(days=2))]
            applied_companies: list = list(df.company)
            log.debug(f"found {applied_companies}")
            log.info(f"{len(applied_companies)} companies found")
            return applied_companies
        except Exception as e:
            log.info(
                str(e)
                + "   list of companies could not be loaded from CSV {}".format(
                    filename
                )
            )
            return None

    def browser_options(self):
        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-extensions")

        # Disable webdriver flags or you will be easily detectable
        options.add_argument("--disable-blink-features")
        options.add_argument("--disable-blink-features=AutomationControlled")
        return options

    def start_linkedin(self, username, password) -> None:
        log.info("Logging in.....Please wait :)  ")
        self.browser.get(
            "https://www.linkedin.com/login?trk=guest_homepage-basic_nav-header-signin"
        )
        try:
            user_field = self.browser.find_element("id", "username")
            pw_field = self.browser.find_element("id", "password")
            login_button = self.browser.find_element(
                "xpath", '//*[@id="organic-div"]/form/div[3]/button'
            )
            user_field.send_keys(username)
            user_field.send_keys(Keys.TAB)
            time.sleep(2)
            pw_field.send_keys(password)
            time.sleep(2)
            login_button.click()
            time.sleep(3)
            input("Check login Info, or verification check")
        except TimeoutException:
            log.info(
                "TimeoutException! Username/password field or login button not found"
            )

    def fill_data(self) -> None:
        self.browser.set_window_size(1, 1)
        self.browser.set_window_position(2000, 2000)

    def start_apply(self, positions, locations) -> None:
        start: float = time.time()
        self.fill_data()

        combos: list = []
        while len(combos) < len(positions) * len(locations):
            position = positions[random.randint(0, len(positions) - 1)]
            location = locations[random.randint(0, len(locations) - 1)]
            combo: tuple = (position, location)
            if combo not in combos:
                combos.append(combo)
                log.info(f"Applying to {position}: {location}")
                location = "&location=" + location
                app_loop_result = self.applications_loop(position, location)
                if app_loop_result == "No Next Page Found":
                    continue
            if len(combos) > 500:
                break

    def scroll_down_page(self):
        scrollable_div = self.browser.find_element(
            By.XPATH, '//*[@id="main"]/div/section[1]/div'
        )
        height_total = int(
            driver.execute_script("return arguments[0].scrollHeight", scrollable_div)
        )
        for x in range(1, height_total, 5):
            driver.execute_script(
                "arguments[0].scrollTo(0, {})".format(x), scrollable_div
            )

    def applications_loop(self, position, location):

        count_application = 0
        count_job = 0
        jobs_per_page = 0
        start_time: float = time.time()
        self.browser.maximize_window()
        # navigate to jobs page
        page_url_path = self.navigate_to_jobs_page(position, location, jobs_per_page)
        log.info("Looking for jobs, please wait..")

        while time.time() - start_time < self.MAX_SEARCH_TIME:
            log.info(
                f"{(self.MAX_SEARCH_TIME - (time.time() - start_time)) // 60} minutes left in this search"
            )

            # sleep to make sure everything loads, add random to make us look human.
            randoTime: float = random.uniform(3.5, 4.9)
            log.debug(f"Sleeping for {round(randoTime, 1)}")
            time.sleep(randoTime)
            self.load_page(sleep=1)

            self.scroll_down_page()

            time.sleep(randoTime)
            # get job links, (the following are actually the job card objects)
            links = self.browser.find_elements("xpath", "//div[@data-job-id]")

            log.info(f"Found {len(links)} links")

            if len(links) == 0:
                log.debug("No links found")
                break

            IDs: list = []
            # reload the csv to check duplicate companies
            past_companies: list | None = self.get_applied_companies(self.filename)
            applied_companies: list = past_companies if past_companies != None else []

            # children selector is the container of the job cards on the left
            for link in links:
                companies = link.find_elements(
                    By.XPATH,
                    './/div[@class="job-card-container__company-name"]',
                )
                # job_titles = link.find_elements(By.XPATH, "//div[@class='full-width artdeco-entity-lockup__title ember-view']//a")
                for comp in companies:
                    # get job title
                    # job_title = link.find_element(By.XPATH, "//div[@class='full-width artdeco-entity-lockup__title ember-view']//a")
                    # job_title_lowercase = job_title.text.lower()
                    company_name = comp.text
                    company_name_lowercase = comp.text.lower()
                    if (
                        company_name_lowercase not in self.blacklist_companies
                        and company_name not in applied_companies
                    ):
                        log.debug(
                            f"'{company_name_lowercase}' was not found in {self.blacklist_companies} and {company_name} was not found in {applied_companies}"
                        )
                        temp = link.get_attribute("data-job-id")
                        jobID = temp.split(":")[-1]
                        IDs.append(int(jobID))
                    else:
                        log.debug(
                            f"skipping {company_name}, because it was found in the csv list: {applied_companies} or yaml config: {self.blacklist_companies}"
                        )
            IDs: list = set(IDs)

            # remove already applied jobs
            before: int = len(IDs)
            jobIDs: list = [x for x in IDs if x not in self.appliedJobIDs]
            after: int = len(jobIDs)

            # if the jobIDs filtered is equal to 0 then go to next page
            log.debug(f"after filtering jobIDs, there are {len(jobIDs)} left")
            # breakpoint()
            if len(jobIDs) == 0:
                page_url_path = self.click_on_next_page(page_url_path)
                if not page_url_path:
                    log.info(f"Unable to navigate to next page, stopping script")
                    return
                continue

            for i, jobID in enumerate(jobIDs):
                count_job += 1
                self.get_job_page(jobID)

                # get easy apply button
                button = self.get_easy_apply_button()
                # word filter to skip positions not wanted

                if button is not False:
                    if any(word in self.browser.title for word in blacklist_titles):
                        log.info(
                            "skipping this application, a blacklisted keyword was found in the job position"
                        )
                        string_easy = "* Contains blacklisted keyword"
                        result = False
                    else:
                        string_easy = "* has Easy Apply Button"
                        log.info("Clicking the EASY apply button")
                        button.click()
                        time.sleep(3)
                        self.fill_out_phone_number()
                        # get the list of tech_skills, the corresponding value and input into the boxes
                        result: bool = self.send_resume()
                        count_application += 1
                else:
                    log.info("The button does not exist.")
                    string_easy = "* Doesn't have Easy Apply Button"
                    result = False

                position_number: str = str(count_job + jobs_per_page)
                log.info(
                    f"\nPosition {position_number}:\n {self.browser.title} \n {string_easy} \n"
                )

                # remove emoji from text
                self.write_to_file(button, jobID, self.browser.title, result)

                # sleep every 20 applications
                if count_application != 0 and count_application % 20 == 0:
                    sleepTime: int = random.randint(500, 900)
                    log.info(
                        f"application count: {count_application} Sleeping for:{int(sleepTime / 60)} mins"
                    )
                    time.sleep(sleepTime)

                # go to new page if all jobs are done
                log.debug(
                    f"count job is {count_job}, number for jobIDs is {len(jobIDs)}"
                )
                if count_job == len(jobIDs):
                    count_job = 0
                    log.info("Navigating to Next Jobs Page...")
                    page_url_path = self.click_on_next_page(page_url_path)
                    if not page_url_path:
                        log.info("unable to click on next page, no more jobs found")
                        return "No Next Page Found"

    def write_to_file(self, button, jobID, browserTitle, result) -> None:
        def re_extract(text, pattern):
            target = re.search(pattern, text)
            if target:
                target = target.group(1)
            return target

        timestamp: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        attempted: bool = False if button == False else True
        job = re_extract(browserTitle.split(" | ")[0], r"\(?\d?\)?\s?(\w.*)")
        company = re_extract(browserTitle.split(" | ")[1], r"(\w.*)")
        company = self.clean_emoji(company)
        job = self.clean_emoji(job)

        toWrite: list = [timestamp, jobID, job, company, attempted, result]
        with open(self.filename, "a", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(toWrite)

    def get_job_page(self, jobID):

        job: str = "https://www.linkedin.com/jobs/view/" + str(jobID)
        self.browser.get(job)
        self.job_page = self.load_page(sleep=0.5)
        return self.job_page

    def get_easy_apply_button(self):

        try:
            self.browser.find_element(
                "xpath",
                "//button[contains(@class, 'jobs-apply-button')]//span[text()[contains(.,'Easy Apply')]]",
            )
            button = self.browser.find_elements(
                "xpath", "//button[contains(@class, 'jobs-apply-button')]"
            )
            EasyApplyButton = button[0]
        except Exception as e:
            print("Exception:", e)
            EasyApplyButton = False

        return EasyApplyButton

    # method to get the number of experience numeric inputs
    def input_experience_numeric(self):
        def is_present(button_locator) -> bool:
            return (
                len(self.browser.find_elements(button_locator[0], button_locator[1]))
                > 0
            )

        # try:
        next_locater = (
            By.CSS_SELECTOR,
            "button[aria-label='Continue to next step']",
        )
        # Get the experience input elements
        experience_elements = self.browser.find_elements(
            "xpath",
            "//span[text()[contains(translate(.,'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ'),'EXPERIENCE')]]",
        )
        # See if any the list of skills is in the question
        if experience_elements:
            for elements in experience_elements:
                question = elements.text
                # loop through the list of skills and check if it's in the question
                for skill in self.techexperience:
                    skill_name_caps = skill.upper()
                    num_years = self.techexperience[f"{skill}"]
                    question_lowercase = question.lower()
                    if skill in question_lowercase:
                        # make sure it's an input
                        experience_input = self.browser.find_element(
                            "xpath",
                            f"//span[text()[contains(translate(.,'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ'),'{skill_name_caps}')]]//parent::label//following-sibling::div//input",
                        )
                        if experience_input:
                            experience_input.clear()
                            experience_input.send_keys(int(num_years))
                        else:
                            log.debug("Not an input")
                    # if skill is not listed then enter in the default
                    else:
                        # make sure it's an input
                        experience_input = self.browser.find_element(
                            "xpath",
                            f"//span[text()='{question}']//parent::label//following-sibling::div//input",
                        )
                        experience_input.clear()
                        experience_input.send_keys(int(self.techexperience["default"]))
                    # gives the digital assistant a soul
                    time.sleep(random.uniform(4.5, 6.5))

            next_locater = (
                By.CSS_SELECTOR,
                "button[aria-label='Continue to next step']",
            )
            error_locator = (
                By.CSS_SELECTOR,
                "p[data-test-form-element-error-message='true']",
            )

            # Click Next or submitt button if possible
            button: None = None
            if is_present(next_locater):
                button: None = self.wait.until(EC.element_to_be_clickable(next_locater))

            if is_present(error_locator):
                for element in self.browser.find_elements(
                    error_locator[0], error_locator[1]
                ):
                    text = element.text
                    if "Please enter a valid answer" in text:
                        button = None
                        return False
            if button:
                button.click()
                time.sleep(random.uniform(1.5, 2.5))
            button: None = None
            return True
        else:
            # Check if there are any experience inputs
            log.debug(f"No experience input field found")
            return False

    def fill_additional_questions(self):
        breakpoint()
        # Find the addtional questions element
        additional_questions_elements = self.browser.find_elements(
            By.XPATH,
            "//div[contains(@class, 'jobs-easy-apply-form-section__grouping')]",
        )
        # get the config values into variables
        tech_experience_dict = self.techexperience
        radio_dropdowns_dict = self.radiodropdowns

        additional_questions_num_elements = len(additional_questions_elements)
        log.info(f"found {additional_questions_num_elements} questions to be filled")
        if additional_questions_num_elements > 0:
            radio_type_xpath = (
                "//legend[contains(@class, 'fb-dash-form-element__label')]"
            )
            dropdown_type_xpath = (
                "//label[contains(@class,'fb-dash-form-element__label')]"
            )
            input_type_xpath = "//label[contains(@class, 'artdeco-text-input--label')]"
            # locate all the input type fields
            try:
                log.info(f"Seeing if element is a input type field")
                input_type_elements = self.browser.find_elements(
                    By.XPATH, input_type_xpath
                )
            except Exception as e:
                log.info(e)
                log.info(f"No input type elements found")
                input_type_elements = None
            # locate all the radio buttons
            try:
                log.info(f"Seeing if element is a radio type")
                radio_type_elements = self.browser.find_elements(
                    By.XPATH, radio_type_xpath
                )
            except Exception as e:
                log.info(e)
                log.info(f"No radio type elements found")
                radio_type_elements = None
            # locate all the dropdowns
            try:
                log.info(f"Seeing if element is a dropdown type")
                dropdown_type_elements = self.browser.find_elements(
                    By.XPATH, dropdown_type_xpath
                )
            except Exception as e:
                log.info(e)
                log.info(f"No dropdown type elements found")
                dropdown_type_elements = None

            # loop through the input elements found
            if len(input_type_elements) > 0:
                for input_el in input_type_elements:
                    input_question_element_txt = input_el.text.strip()
                    input_question_element_txt_lowercase = (
                        input_question_element_txt.lower()
                    )
                    # see if it's a numeric input type
                    numeric_type_xpath = f'//label[contains(@class, "artdeco-text-input--label") and text()[contains(.,"{input_question_element_txt}")]]//following-sibling::input[contains(@aria-describedby, "numeric-error")]'
                    try:
                        log.info(f"Seeing if element is a numeric input type field")
                        numeric_input_type = self.browser.find_element(
                            By.XPATH, numeric_type_xpath
                        )
                        # get the current value of the input to check if it is blank and needs to be filled
                        input_question_element_txt_value = (
                            numeric_input_type.get_attribute("value")
                        )
                    except:
                        log.info(
                            f"{input_question_element_txt} not a numeric input type"
                        )
                        numeric_input_type = None
                        # Just stop it completely until words input functions has been has been made
                        return False

                    # if the numeric input type exists and is a blank valueexit
                    if numeric_input_type and input_question_element_txt_value == "":
                        # If it's a salary question numeric value then input the salary specified in the config
                        if str("salary") in input_question_element_txt_lowercase:
                            numeric_input_type.clear()
                            numeric_input_type.send_keys(self.salary_number)
                            # gives the digital assistant a soul
                            time.sleep(random.uniform(4.5, 6.5))
                            break
                        # Check the listed skills in the config and input accordingly
                        for skill in tech_experience_dict:
                            regex_match = rf"\b{skill}\b"
                            if re.search(
                                regex_match,
                                input_question_element_txt_lowercase,
                            ):
                                log.info(
                                    f"skill {skill} found in string: {input_question_element_txt_lowercase}"
                                )
                                skill_num_value = int(tech_experience_dict[skill])
                                log.info(
                                    f"Entering number {skill_num_value} value for {input_question_element_txt_lowercase}"
                                )
                                numeric_input_type.clear()
                                numeric_input_type.send_keys(skill_num_value)
                                # gives the digital assistant a soul
                                time.sleep(random.uniform(4.5, 6.5))
                                break
                        # if there is no skill listed for it then enter the default specified value in config
                        else:
                            log.info(
                                f"skill {skill} NOT found in string: {input_question_element_txt_lowercase} using default"
                            )
                            # Use the default number set in config
                            default_skill_num_value = int(
                                tech_experience_dict["default"]
                            )
                            log.info(
                                f"Entering the default number {default_skill_num_value} value for {input_question_element_txt_lowercase}"
                            )
                            numeric_input_type.clear()
                            numeric_input_type.send_keys(default_skill_num_value)
                            # gives the digital assistant a soul
                            time.sleep(random.uniform(4.5, 6.5))
                    else:
                        input_question_element_txt
                        log.info(
                            f"{input_question_element_txt} is already filled out with value of {input_question_element_txt_value}"
                        )

            # for radio input types
            if len(radio_type_elements) > 0:
                for radio_el in radio_type_elements:
                    radio_type_element_text = radio_el.text.strip()
                    radio_type_element_text_lowercase = radio_type_element_text.lower()
                    for keyname in radio_dropdowns_dict:
                        log.info(
                            f"seeing if {keyname} is in string: {radio_type_element_text_lowercase}"
                        )
                        if keyname in radio_type_element_text_lowercase:
                            key_value = radio_dropdowns_dict[keyname]
                            # translate keyname values True or False booleans to yes or no strings
                            if key_value is True:
                                key_value = "Yes"
                            elif key_value is False:
                                key_value = "No"
                            # select according to the key's value in the config
                            radio_type_element_input_xpath = f'//legend[contains(@class,"fb-dash-form-element__label") and text()[contains(.,"{radio_type_element_text}")]]//following-sibling::div//input[contains(@value,"{key_value}")]'
                            try:
                                radio_type_input_element = self.browser.find_element(
                                    By.XPATH,
                                    radio_type_element_input_xpath,
                                )
                            except:
                                log.error(f"{radio_type_element_input_xpath} not found")
                                radio_type_input_element = None
                            if radio_type_input_element:
                                self.actions.move_to_element(
                                    radio_type_input_element
                                ).click().perform()
                                # gives the digital assistant a soul
                                time.sleep(random.uniform(4.5, 6.5))
                                break
                    else:
                        log.info(
                            f"{keyname} was not found in {radio_type_element_text_lowercase}"
                        )
                        # Use default value of yes if yes or no options else select the first option just to move the app submission forward
                        radio_type_element_input_no_xpath = f'//legend[contains(@class,"fb-dash-form-element__label" ) and text()[contains(.,"{radio_type_element_text}")]]//following-sibling::div//input[contains(translate(@value,"ABCDEFGHIJKLMNOPQRSTUVWXYZ","abcdefghijklmnopqrstuvwxyz"),"yes")]'
                        try:
                            radio_element_no_value = self.browser.find_element(
                                By.XPATH, radio_type_element_input_no_xpath
                            )
                        except:
                            log.debug(
                                f"not finding a No option using {radio_type_element_input_no_xpath}, going to choose the first option instead"
                            )
                        if radio_element_no_value:
                            log.debug("Choosing first radio option")
                            self.actions.move_to_element(
                                radio_element_no_value
                            ).click().perform()
                            # gives the digital assistant a soul
                            time.sleep(random.uniform(4.5, 6.5))
                        radio_type_input_element_first_selection_xpath = f'//legend[contains(@class,"fb-dash-form-element__label" ) and text()[contains(.,"{radio_type_element_text}")]]//following-sibling::div[1]//input'
                        try:
                            radio_element_first_option = self.browser.find_element(
                                By.XPATH,
                                radio_type_input_element_first_selection_xpath,
                            )
                        except:
                            log.error(
                                f"Unable to select first radio option using {radio_type_input_element_first_selection_xpath} either, breaking out of script"
                            )
                            return False
                        if radio_element_first_option:
                            self.actions.move_to_element(
                                radio_element_first_option
                            ).click().perform()
                            # gives the digital assistant a soul
                            time.sleep(random.uniform(4.5, 6.5))
            # breakpoint()
            if len(dropdown_type_elements) > 0:
                for dropdown_el in dropdown_type_elements:
                    dropdown_type_element_text = dropdown_el.text.strip()
                    # remove any '
                    # dropdown_type_element_text = "'".join(dropdown_type_element_text.split("'")[:-1])
                    dropdown_type_element_text_lowercase = (
                        dropdown_type_element_text.lower()
                    )
                    dropdown_select_xpath = f'//label[contains(@class,"fb-dash-form-element__label") and text()[contains(.,"{dropdown_type_element_text}")]]//following-sibling::select'
                    for keyname in radio_dropdowns_dict:
                        log.info(
                            f"seeing if {keyname} is in string: {dropdown_type_element_text_lowercase}"
                        )
                        if keyname in dropdown_type_element_text_lowercase:
                            key_name_value = str(radio_dropdowns_dict[keyname])
                            # key_name_value_lowercase = key_name_value.lower()
                            try:
                                select_dropdown = Select(
                                    self.browser.find_element(
                                        By.XPATH, dropdown_select_xpath
                                    )
                                )
                                # dropdown_select_element = self.browser.find_element(By.XPATH, dropdown_select_xpath)
                            except Exception as e:
                                log.warning(
                                    f"{e}: Unable to find {dropdown_select_xpath} to select from the dropdown"
                                )
                                # dropdown_select_element = None
                                select_dropdown = None
                            if select_dropdown:
                                log.info(f"key value is {key_name_value}")
                                if key_name_value is True:
                                    key_name_translate_value = "Yes"
                                elif key_name_value is False:
                                    key_name_translate_value = "No"
                                else:
                                    key_name_translate_value = (
                                        key_name_value.capitalize()
                                    )
                                try:
                                    select_dropdown.select_by_value(
                                        f"{key_name_translate_value}"
                                    )
                                except Exception as e:
                                    log.info(f"{e}: Error clicking on dropdown option")
                                    break
                                # dropdown_select_element.click()
                                # gives the digital assistant a soul
                                time.sleep(random.uniform(4.5, 6.5))
                                break
                    else:
                        log.info(
                            f"{keyname} not in {dropdown_type_element_text_lowercase}"
                        )
                        # go with the default yes or use the first option
                        try:
                            select_dropdown = Select(
                                self.browser.find_element(
                                    By.XPATH, dropdown_select_xpath
                                )
                            )
                            # dropdown_select_element = self.browser.find_element(By.XPATH, dropdown_select_xpath)
                        except Exception as e:
                            log.warning(
                                f"{e}: Unable to find {dropdown_select_xpath} to select from the dropdown"
                            )
                            # dropdown_select_element = None
                            select_dropdown = None
                            return False
                        if select_dropdown:
                            try:
                                # dropdown_select_yes_element = self.browser.find_element(By.XPATH, dropdown_select_yes_xpath)
                                select_dropdown.select_by_value("Yes")
                                dropdown_select_yes_element = True
                            except Exception as e:
                                log.debug(
                                    f"{e}: unable to find Yes to click on, going to try the first valid option"
                                )
                                dropdown_select_yes_element = None
                        if dropdown_select_yes_element:
                            # dropdown_select_yes_element.click()
                            # gives the digital assistant a soul
                            time.sleep(random.uniform(4.5, 6.5))
                            # break
                        else:
                            # select first valid option
                            try:
                                # dropdown_default_select_first_element = self.browser.find_element(By.XPATH, dropdown_default_select_first_valid_xpath)
                                select_dropdown.select_by_index(1)
                                dropdown_default_select_first_valid_xpath = True
                            except:
                                log.error(
                                    f"Unable to locate the first valid dropdown element option either, returning function"
                                )
                                dropdown_default_select_first_valid_xpath = None
                                return False
                            if dropdown_default_select_first_valid_xpath:
                                # dropdown_default_select_first_element.click()
                                # gives the digital assistant a soul
                                time.sleep(random.uniform(4.5, 6.5))
                                # break
        else:
            # Check if there are any experience inputs
            log.debug(f"No fields to be filled or selected found")
            return False
        # Check to make sure there is no more errors
        try:
            error_check = self.browser.find_element(
                By.XPATH,
                '//span[@class="artdeco-inline-feedback__message" and text()[contains(.,"Please enter a valid answer")]]',
            )
            log.info(f"Error message was found after filling out addtional questions")
        except:
            log.info(f"No Error message found after filling out addtional questions")
            error_check = None

        if error_check:
            return False
        return True

    def fill_out_phone_number(self):
        def is_present(button_locator) -> bool:
            return (
                len(self.browser.find_elements(button_locator[0], button_locator[1]))
                > 0
            )

        # try:
        next_locater = (
            By.CSS_SELECTOR,
            "button[aria-label='Continue to next step']",
        )
        try:
            input_field = self.browser.find_element(
                By.XPATH,
                "//input[contains(@name,'phoneNumber') or contains(@id,'phoneNumber')]",
            )
        except Exception as e:
            log.info(f"{e}: No phone number field")
            input_field = None

        if input_field:
            input_field.clear()
            input_field.send_keys(self.phone_number)
            time.sleep(random.uniform(4.5, 6.5))

            next_locater = (
                By.CSS_SELECTOR,
                "button[aria-label='Continue to next step']",
            )
            error_locator = (
                By.XPATH,
                "//span[@class='artdeco-inline-feedback__message']",
            )

            # Click Next or submitt button if possible
            button: None = None
            if is_present(next_locater):
                button: None = self.wait.until(EC.element_to_be_clickable(next_locater))

            if is_present(error_locator):
                for element in self.browser.find_elements(
                    error_locator[0], error_locator[1]
                ):
                    text = element.text
                    if "Please enter a valid answer" in text:
                        button = None
                        break
            if button:
                button.click()
                time.sleep(random.uniform(1.5, 2.5))
                # if i in (3, 4):
                #     submitted = True
                # if i != 2:
                #     break

        else:
            log.debug(f"Could not find phone number field")

    def send_resume(self) -> bool:
        # breakpoint()
        def is_present(button_locator) -> bool:
            return (
                len(self.browser.find_elements(button_locator[0], button_locator[1]))
                > 0
            )

        try:
            time.sleep(random.uniform(1.5, 2.5))
            next_locater = (
                By.CSS_SELECTOR,
                "button[aria-label='Continue to next step']",
            )
            review_locater = (
                By.CSS_SELECTOR,
                "button[aria-label='Review your application']",
            )
            submit_locater = (
                By.CSS_SELECTOR,
                "button[aria-label='Submit application']",
            )
            submit_application_locator = (
                By.CSS_SELECTOR,
                "button[aria-label='Submit application']",
            )
            error_locator = (
                By.XPATH,
                "//span[@class='artdeco-inline-feedback__message']",
            )
            upload_locator = (By.CSS_SELECTOR, "input[name='file']")
            follow_locator = (
                By.CSS_SELECTOR,
                "label[for='follow-company-checkbox']",
            )
            resume_required_error_locator = (
                By.XPATH,
                '//p[@role="alert" and text()="A resume is required"]',
            )

            submitted = False
            while True:
                # Upload Cover Letter if possible
                if is_present(upload_locator):

                    input_buttons = self.browser.find_elements(
                        upload_locator[0], upload_locator[1]
                    )
                    for input_button in input_buttons:
                        parent = input_button.find_element(By.XPATH, "..")
                        sibling = parent.find_element(By.XPATH, "preceding-sibling::*")
                        grandparent = sibling.find_element(By.XPATH, "..")
                        for key in self.uploads.keys():
                            sibling_text = sibling.text
                            gparent_text = grandparent.text
                            if (
                                key.lower() in sibling_text.lower()
                                or key in gparent_text.lower()
                            ):
                                input_button.send_keys(self.uploads[key])

                    # input_button[0].send_keys(self.cover_letter_loctn)
                    time.sleep(random.uniform(4.5, 6.5))

                # Click Next or submitt button if possible
                button: None = None
                buttons: list = [
                    next_locater,
                    review_locater,
                    follow_locator,
                    submit_locater,
                    submit_application_locator,
                ]
                for i, button_locator in enumerate(buttons):
                    if is_present(button_locator):
                        button: None = self.wait.until(
                            EC.element_to_be_clickable(button_locator)
                        )

                    if is_present(resume_required_error_locator):
                        # Choose resume option
                        log.info(f"Choosing Resume")
                        choose_resume_result = self.choose_resume()
                        if choose_resume_result is True:
                            continue
                        else:
                            button = None
                            break

                    if is_present(error_locator):
                        # Fill out additional questions
                        log.info("Filling out the additional questions")
                        additional_questions_result = self.fill_additional_questions()
                        log.info(
                            f"Additional questions result is {str(additional_questions_result)}"
                        )
                        if additional_questions_result is True:
                            continue
                        elif additional_questions_result is False:
                            button = None
                            break

                        for element in self.browser.find_elements(
                            error_locator[0], error_locator[1]
                        ):
                            text = element.text
                            if "Please enter a valid answer" in text:
                                button = None
                                break
                    if button:
                        # Adding try here in case the button is broken
                        try:
                            button.click()
                        except Exception as e:
                            log.error(f"{e} error clicking the next button")
                            button = None
                            break
                        time.sleep(random.uniform(1.5, 2.5))
                        if i in (3, 4):
                            submitted = True
                        if i != 2:
                            break
                if button == None:
                    log.info("Could not complete submission")
                    break
                elif submitted:
                    log.info("Application Submitted")
                    break

            time.sleep(random.uniform(1.5, 2.5))

        except Exception as e:
            log.info(e)
            log.info("cannot apply to this job")
            # button = None
            return None
            # raise (e)

        return submitted

    # method to choose resume insted of upload
    def choose_resume(self):
        # breakpoint()
        uploaded_resume = self.resume_name
        time.sleep(random.uniform(1.5, 2.5))

        choose_resume_xpath = f'//div[@class="jobs-resume-picker__resume-list"]//div[text()[contains(.,"{uploaded_resume}")]]//parent::div//parent::div//following-sibling::button[@aria-label="Choose Resume"]'
        try:
            choose_resume_element = self.browser.find_element(
                By.XPATH, choose_resume_xpath
            )
        except:
            log.debug(
                f"choose resume button element not found at {choose_resume_xpath}"
            )
            choose_resume_element = None
        if choose_resume_element:
            choose_resume_element.click()
            # input_button[0].send_keys(self.cover_letter_loctn)
            time.sleep(random.uniform(4.5, 6.5))
            return True
        else:
            log.error(
                f"uploaded resume name: {uploaded_resume} could not be found to choose"
            )
            return False

    def load_page(self, sleep=1):
        scroll_page = 0
        while scroll_page < 4000:
            self.browser.execute_script("window.scrollTo(0," + str(scroll_page) + " );")
            scroll_page += 200
            time.sleep(sleep)

        if sleep != 1:
            self.browser.execute_script("window.scrollTo(0,0);")
            time.sleep(sleep * 3)

        page = BeautifulSoup(self.browser.page_source, "lxml")
        return page

    def navigate_to_jobs_page(self, position, location, jobs_per_page):
        self.browser.get(
            "https://www.linkedin.com/jobs/search/?f_LF=f_AL&f_TPR=r604800&keywords="
            + position
            + location
            + "&start="
            + str(jobs_per_page)
        )
        # self.avoid_lock()
        # log.info("Lock avoided.")
        self.load_page()
        # get the current url
        current_url_page = self.browser.current_url
        return current_url_page

    # get the numbered buttons for going to next jobs page
    def click_on_next_page(self, previous_url):
        log.info(f"Navigating to {previous_url}")
        # navigate back to previous url
        self.browser.get(previous_url)

        # scroll down the scaffold
        # self.scroll_down_page()
        # get current page number
        current_page_number_xpath = (
            '//button[@aria-current="true" and contains(@aria-label,"Page")]'
        )
        try:
            current_page_element = self.browser.find_element(
                By.XPATH, current_page_number_xpath
            )
            current_page_num_str = str(current_page_element.text)
            log.info(f"current page number is {current_page_num_str}")
        except Exception as e:
            log.error(f"{e}: could not find current page number button element")
            current_page_num_str = None
        # click on next page number
        if current_page_num_str:
            next_page_number_str = str(int(current_page_num_str) + 1)
            next_page_number_xpath = (
                f'//button[contains(@aria-label,"Page {next_page_number_str}")]'
            )
        try:
            next_page_number_element = self.browser.find_element(
                By.XPATH, next_page_number_xpath
            )
        except Exception as e:
            log.info(f"{e}: could not find next page number button element")
            next_page_number_element = None
        if next_page_number_element:
            log.info("navigating to next page number")
            # self.actions.move_to_element(next_page_number_element).click().perform()
            click_next_element = self.wait.until(
                EC.element_to_be_clickable(next_page_number_element)
            )
            click_next_element.click()
            # confirm it's now on the next page
            next_page_number_check_xpath = f'//button[@aria-current="true" and contains(@aria-label,"Page {next_page_number_str}")]'
            try:
                next_page_number_check_element = self.browser.find_element(
                    By.XPATH, next_page_number_check_xpath
                )
            except Exception as e:
                log.error(
                    f"{e}: not on currently on next page num: {next_page_number_str}"
                )
                next_page_number_check_element = None
            if next_page_number_check_element:
                # get the next page url
                next_page_url = self.browser.current_url
                return next_page_url
        return False

    def clean_emoji(self, text):
        allchars = [str for str in text]
        emoji_list = [c for c in allchars if c in emoji.EMOJI_DATA]
        clean_text = " ".join(
            [str for str in text.split() if not any(i in str for i in emoji_list)]
        )

        return clean_text

    def finish_apply(self) -> None:
        self.browser.close()


if __name__ == "__main__":
    # breakpoint()
    with open("config.yaml", "r") as stream:
        try:
            parameters = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            raise exc

    username = input(f"Please enter your Linkedin username:   ")
    password = input(f"Please enter your Linkedin password:   ")

    assert len(parameters["positions"]) > 0
    assert len(parameters["locations"]) > 0
    assert parameters["phone_number"] is not None

    if "uploads" in parameters.keys() and type(parameters["uploads"]) == list:
        raise Exception(
            "uploads read from the config file appear to be in list format"
            + " while should be dict. Try removing '-' from line containing"
            + " filename & path"
        )

    log.info(
        {
            k: parameters[k]
            for k in parameters.keys()
            if k not in ["username", "password"]
        }
    )

    output_filename: list = [
        f for f in parameters.get("output_filename", ["output.csv"]) if f != None
    ]
    output_filename: list = (
        output_filename[0] if len(output_filename) > 0 else "output.csv"
    )
    blacklist_companies = parameters.get("blacklist_companies", [])
    blacklist_titles = parameters.get("blacklist_titles", [])

    uploads = (
        {} if parameters.get("uploads", {}) == None else parameters.get("uploads", {})
    )
    for key in uploads.keys():
        assert uploads[key] != None

    assistant = DigitalAssistant(
        username=username,
        password=password,
        phone_number=parameters["phone_number"],
        uploads=uploads,
        filename=output_filename,
        blacklist_companies=blacklist_companies,
        blacklist_titles=blacklist_titles,
        technicalskills=parameters["tech_skills"],
        salarynumeric=parameters["salary"],
        radio_and_dropdowns=parameters["radio_and_dropdowns"],
        resumename=parameters["existing_resume"],
    )

    locations: list = [l for l in parameters["locations"] if l != None]
    positions: list = [p for p in parameters["positions"] if p != None]
    assistant.start_apply(positions, locations)


# it's skipping after it goes to the input_experience_numeric function, need it to go back and run the resume again
# Have you previously worked as a Technical Architect?
