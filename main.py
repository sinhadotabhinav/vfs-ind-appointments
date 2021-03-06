#!/opt/anaconda3/bin/python3
import getpass
import logging
import os
import smtplib
import threading
import time
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait

# def check_appointment retireves available appointments
def check_appointment(first_run_flag):
    log.info("The application is checking appointment availability for: %s in %s", visa_category, embassy_location_name)
    selenium_driver = setup_selenium_driver()
    try:
        WebDriverWait(selenium_driver, wait_time).until(EC.presence_of_element_located((By.ID, "plhMain_lnkSchApp")))
        selenium_driver.find_element_by_id("plhMain_lnkSchApp").click()
        Select(selenium_driver.find_element_by_id("plhMain_cboVAC")).select_by_visible_text(embassy_location_name)
        selenium_driver.find_element_by_id("plhMain_btnSubmit").click()
        Select(selenium_driver.find_element_by_id("plhMain_cboVisaCategory")).select_by_visible_text(visa_category)
        selenium_driver.find_element_by_id("plhMain_btnSubmit").click()
        if "No date(s) available for appointment" in selenium_driver.page_source:
            log.info("No appointments are available, trying again in {} minutes.".format(schedule_interval/60))
            if first_run_flag:
                log.debug("Welcome email notification will be sent to the recipient")
                send_email_notification(email_subject_first, email_body_first, 'welcome')
        else:
            log.info("New appointments are available! Please book soon.")
            send_email_notification(email_subject, email_body, 'new appointment')
    finally:
        global first_run
        first_run = False
        run_daily_digest(selenium_driver)
        selenium_driver.quit()

# def get_category_menu prints appointment type menu
def get_category_menu():
    return """Choose visa application category:
    1. Certificate of life (attestatie de vita)
    2. Consular declarations
    3. Copy conform original (NL passport, ID card or driving license)
    4. Identity card, first time application for a minor
    5. Identity card, first time application for an adult
    6. Identity card, renewal for a minor
    7. Identity card, renewal for an adult
    8. Legalisation of a signature
    9. Legalisation of documents
    10. MVV - Exchange for study
    11. MVV ??? Employment
    12. MVV ??? Family
    13. MVV ??? Highly skilled migrant
    14. MVV ??? Study
    15. Passport
    16. Passport - renewal after obtaining foreign nationality
    17. Passport ??? 2nd passport
    18. Passport, first time application for a minor
    19. Passport, first time application for an adult
    20. Passport, renewal for a minor
    21. Passport, renewal for an adult
    22. Visa - Schengen, for diplomatic and special passport holders"""

# def get_category fetches category number entered by user
def get_category(menu):
    print(menu)
    print("Please enter a valid category number from the above menu (1-22)")
    number = int(input("> "))
    while number not in range(1, 23):
        print("Invalid input for category number, please try again")
        log.error("User entered an invalid category number: %s", number)
        number = int(input("> "))
    for item in menu.split("\n"):
        if str(number) in item:
            return item.strip()[len(str(number)) + 2:]

# def get_chrome_driver fetches chromedriver
def get_chrome_driver():
    dir_name = os.path.dirname(__file__)
    driver_file = os.path.join(dir_name, driver_path)
    return driver_file

# def get_schedule_interval fetches schedule interval entered by user
def get_schedule_interval():
    print("Enter a scheduling time interval in minutes e.g., 10, 15, or 20. Default is 60 minutes")
    while True:
        try:
            interval = int(input("> "))
            if interval > 0:
                return interval * 60
            else:
                print("Invalid input for interval minutes, please try again")
                log.error(f"User entered an invalid input for interval minutes: %s", interval)
                interval = int(input("> "))
        except:
            print("Invalid input for interval minutes, please try again")
            log.error(f"User entered an invalid input for interval minutes")

# def run_daily_digest executes a daily report EOD
def run_daily_digest(selenium_driver):
    current_time = datetime.now()
    next_run_time = current_time + timedelta(seconds=schedule_interval)
    if not (next_run_time.day == current_time.day and \
      next_run_time.month == current_time.month and \
      next_run_time.year == current_time.year):
      log.debug("Daily digest report will be sent to the recipient")
      time.sleep(5)
      email_body = email_body_digest + "\n\n{}".format(selenium_driver.page_source)
      send_email_notification(email_subject_digest, email_body, 'daily digest')

# def schedule_notifier schedules the application
def schedule_notifier():
    threading.Timer(schedule_interval, schedule_notifier).start()
    check_appointment(first_run)
    log.debug("Next application run has been scheduled")

# def send_email_notification sends email notification
def send_email_notification(subject, content, event):
    message = MIMEMultipart()
    message['From'] = "{}<{}>".format(app_name, client)
    message['To'] = recipient
    message['Subject'] = subject
    message.attach(MIMEText(content, 'html'))
    body = message.as_string()
    smtp_conn = setup_smtp_settings(client, password)
    try:
        smtp_conn.sendmail(client, recipient, body)
        log.info(f"Email notification sent to %s (%s)", recipient, event)
        time.sleep(5)
    except smtplib.SMTPException as e:
        log.error("Unable to send email notification at the moment: %s (%s), will retry", e, event)

# def setup_selenium_driver configures selenium driver
def setup_selenium_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(driver_file, options=chrome_options)
    driver.get(base_url)
    log.debug(f"Selenium driver configured successfully for %s", app_name)
    return driver

# def setup_smtp_settings configures smpt server settings
def setup_smtp_settings(client, password):
    try:
        server = smtplib.SMTP(smtp_address, smtp_port)
        server.starttls()
        server.login(client, password)
        log.debug(f"SMTP login successful for client %s!", client)
        return server
    except smtplib.SMTPException as e:
        log.error("Unsuccessful login %s. Please try again", e)

# decalare application configs
app_name = "vfs-ind-appointments"
base_url = "https://www.vfsvisaonline.com/Netherlands-Global-Online-Appointment_Zone1/AppScheduling/AppWelcome.aspx?P=Y83R/PGUiM5WxqKHxt0UdFsdz2igW6T2aLOpDTU7AEw=" # India zone
driver_path = "./chromedriver"
email_body = "Make an appointment online here:\n\
https://www.vfsvisaonline.com/Netherlands-Global-Online-Appointment_Zone1/AppScheduling/AppWelcome.aspx?P=c%2F75XIhVUvxD%2BgDk%2BH%2BCGBV5n9rG51cpAkEXPymduoQ%3D"
email_body_digest = "Welcome to the daily digest report. The application periodically checked for appointments and will continue to look for new slots tomorrow."
email_body_first = "There are no appointments available at the moment. The application will run periodically and send alerts."
email_subject = app_name + ": new MVV appointments are now available"
email_subject_digest = app_name + ": daily digest report"
email_subject_first = app_name + ": thank you for using this application"
embassy_location_name = "New Delhi"
first_run = True
recipient = "asinha093@gmail.com"
schedule_interval = 3600
smtp_address = "smtp.gmail.com"
smtp_port = 587
wait_time = 10

# setup logging
logging.basicConfig(filename=app_name+'.log', filemode='w', format='[%(asctime)s] %(name)s %(levelname)s %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)
log = logging.getLogger(app_name)

# start application
log.info("vfs-ind-appointments has started")

# display interactive emenu
print("Please enter your Gmail credentials below:")
client = input("Email address: ")
password = getpass.getpass("Password: ")
smtp_server = setup_smtp_settings(client, password)
if smtp_server is not None:
    schedule_interval = get_schedule_interval()
    menu = get_category_menu()
    visa_category = get_category(menu)
    driver_file = get_chrome_driver()
    schedule_notifier()
