from robocorp.tasks import task
from robocorp import browser
from robocorp.http import download
import os
import time

from RPA.Excel.Files import Files
from RPA.Tables import Tables
from RPA.HTTP import HTTP
from RPA.Browser.Selenium import Selenium
from RPA.PDF import PDF
from RPA.Archive import Archive

browser_lib = Selenium()

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    """     selenium_webdriver.configure(
        slowmo=1000,
    ) """
    open_robot_order_website()
    download_orders_file()
    close_annoying_modal()
    orders = get_orders()
    for row in orders:
        fill_the_form(row)
    archive_receipts()
    close_browser()


def open_robot_order_website():
    # TODO: Implement your function here
    browser_lib.open_available_browser("https://robotsparebinindustries.com/#/robot-order")
    ##selenium_webdriver.Chrome.start_session("https://robotsparebinindustries.com/#/robot-order")

def download_orders_file():
    HTTP().download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)

def get_orders():
    library = Tables()
    worksheet = library.read_table_from_csv("orders.csv", header=True)
    return worksheet

def close_annoying_modal():
    browser_lib.click_button("//*[@id='root']/div/div[2]/div/div/div/div/div/button[1]")

def fill_the_form(order):
    browser_lib.select_from_list_by_value("//select[@id='head']", str(order['Head']))
    browser_lib.click_element("//input[@id='id-body-" + str(order['Body']) + "']")
    ##browser_lib.click_button("//input[@placeholder='Enter the part number for the legs']", str(order['Legs']))
    browser_lib.input_text("//input[@placeholder='Enter the part number for the legs']", str(order['Legs']))
    browser_lib.input_text("//input[@id='address']", str(order['Address']))
    ##browser_lib.click_button("//input[@id='address']", str(order['Address']))
    browser_lib.click_button("//button[@id='order']")
    ##check if element with "External Server Error" exist
    while browser_lib.does_page_contain_element("//div[@class='alert alert-danger']"):
        browser_lib.click_button("//button[@id='order']")
    ##if browser_lib.does_page_contain_element("//div[text()='Request Got Lost Error']"):
    ##    browser_lib.click_button("//button[@id='order']")
    receipt_generated = browser_lib.get_text("//div[@id='receipt']")
    receipt_location = store_receipt_as_pdf(receipt_generated)
    screenshot_location = screenshot_robot(receipt_generated)
    embed_screenshot_to_receipt(screenshot_location,receipt_location)
    browser_lib.click_button("//button[@id='order-another']")
    close_annoying_modal()

def close_browser():
    browser_lib.close_browser()

def store_receipt_as_pdf(order_number):
    pdf = PDF()
    pdf.html_to_pdf(order_number, "output/receipts/" + str(order_number.split('\n')[2]) + ".pdf")
    ##pdf.html_to_pdf(html element, "output/receipts/" + str(order_number) + ".pdf")
    return "output/receipts/" + str(order_number.split('\n')[2]) + ".pdf"
    

def screenshot_robot(order_number):
    browser_lib.screenshot(filename="output/receipts/" + str(order_number.split('\n')[2]) + ".png")
    ##return "output/receipts/" + str(order_number.split('\n')[2]) + ".png"
    return "output/receipts/" + str(order_number.split('\n')[2]) + ".png"

def embed_screenshot_to_receipt(screenshot, pdf_file):
    pdf = PDF()
    pdf.add_files_to_pdf([screenshot], pdf_file, append=True)

def archive_receipts():
    lib = Archive()
    lib.archive_folder_with_zip('./output/receipts', 'output/receipts.zip', exclude='*.png')