import urllib.request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import codecs
from bs4 import BeautifulSoup


driver_ = webdriver.Chrome()
wait = WebDriverWait(driver_, 1.5)


class Parser(object):
    @staticmethod
    def open_page(url):
        req = urllib.request.urlopen(url)
        data = req.read()
        html = codecs.decode(data)
        return html

    @staticmethod
    def save_csv(array, file_name):
        file = open(file_name, "a")
        for row in array:
            if "@" in row[2]:
                file.write(f"{row[0]}, {row[2]};\n")
        file.close()

    @staticmethod
    def look_schools(url, driver, file_name):
        rows = []
        html = Parser.open_page(url)
        soup = BeautifulSoup(html, "html.parser")
        anchors = soup.findAll("span", {"class": "bhead"})
        for schools in anchors:
            for i in schools:
                data = Parser.look_email(f"https://osvita.ua/{i.get('href')}", driver)
                if len(data) != 0:
                    if "@" in data[-1]:
                        rows.append(data)
                        print(data)
                        file = open(file_name, "a")
                        file.write(f"{','.join(data)};\n")
                        file.close()
        return rows

    @staticmethod
    def look_email(url, driver):
        try:
            driver.get(url)
            wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, ".bhead")))
            driver.execute_script("window.stop();")
            soup = BeautifulSoup(driver.page_source, "html.parser")
            email_el = soup.find("td", {"class": "vmiddle"})
            email = email_el.find("a").get_text()
            school_name = soup.find("h1", {"class": "heading"}).get_text()
            school_info = email_el.get_text().split(",")
            return school_name, school_info[1], school_info[2], email
        except AttributeError:
            return []

    @staticmethod
    def look_pages(url, driver, file_name):
        not_done = True
        counter = 0
        while not_done:
            url_to_change = url[:-5]
            url_to_check = f"{url_to_change}{counter}.html"
            driver.get(url_to_check)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            if soup.find("div", {"class": "cur"}).get_text() == "Сторінка не знайдена":
                not_done = False
            else:
                Parser.look_schools(url_to_check, driver, file_name)
                counter += 25


Parser.look_pages("https://osvita.ua/school/school-ukraine/search-44-252-0-0-0.html", driver_, "test.csv")
