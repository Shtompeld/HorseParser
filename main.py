import os

import requests
from time import sleep
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


class HorseParser:

    def __init__(self):
        self.browser = webdriver.Chrome()

    # метод для закрытия браузера
    def close_browser(self):

        self.browser.close()
        self.browser.quit()

    def xpath_exists(self, url):

        browser = self.browser
        try:
            browser.find_element(By.XPATH,url)
            exist = True
        except NoSuchElementException:
            exist = False
        return exist

    def class_name_exists(self, cls):

        browser = self.browser
        try:
            browser.find_element(By.CLASS_NAME, cls)
            exist = True
        except NoSuchElementException:
            exist = False
        return exist

    def get_breed_name(self, browser, url):
        browser.get(url)
        sleep(1)  # Ждём загрузку страницы
        horse_breed_xpath = "/html/body/div[1]/div[2]/div[1]/h1"

        if self.xpath_exists(horse_breed_xpath):
            horse_breed = browser.find_elements(By.XPATH, horse_breed_xpath)
            horse_breed = [item.text for item in horse_breed]  # Порода
            return horse_breed[0]
        return None

    def get_characteristics(self, browser,core_ref):

        core = f"{core_ref}/dl[1]"
        dictionary = {}
        i = 1
        while self.xpath_exists(core):
            dictionary[
                browser.find_element(By.XPATH, f"{core}/dt/span").text
            ] = browser.find_element(By.XPATH, f"{core}/dd").text
            i += 1
            core = f"{core_ref}/dl[{i}]"
        return dictionary

    def get_urls_all_horses(self, browser,url):

        browser.get(url)
        #sleep(1)
        main_xpath="/html/body/div/div[2]/div[2]/div[5]"

        if self.xpath_exists(main_xpath):
            path_group = f"{main_xpath}/div[1]"
            breed_list=[]
            j = 1
            while self.xpath_exists(path_group):
                i = 1
                path_element = f"{path_group}/div/a[{i}]"
                while self.xpath_exists(path_element):
                    href = browser.find_elements(By.XPATH, path_element)
                    breed_list.append([item.get_attribute('href') for item in href][0])
                    i += 1
                    path_element = f"{path_group}/div/a[{i}]"

                j += 1
                path_group = f"{main_xpath}/div[{j}]"

            return breed_list

    def get_breed_info(self, browser, url):

        horse_breed = self.get_breed_name(browser, url).replace("Лошадь ", "")
        print(horse_breed)

        if browser.current_url != url:
            browser.get(url)

        # Переходим на вкладку с характеристиками
        if self.xpath_exists("/html/body/div[1]/div[2]/div[2]/ul/li[2]/a"):
            browser.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[2]/ul/li[2]/a").click()

        main_features_dict = self.get_characteristics(browser, "/html/body/div[1]/div[2]/div[2]/div/div[2]/div[1]")
        print(main_features_dict)

        appearance_dict = self.get_characteristics(browser, "/html/body/div[1]/div[2]/div[2]/div/div[2]/div[2]")
        print(appearance_dict)

        character_temperament_dict = self.get_characteristics(browser,
                                                              "/html/body/div[1]/div[2]/div[2]/div/div[2]/div[3]")
        print(character_temperament_dict)

        care_maintenance_dict = self.get_characteristics(browser, "/html/body/div[1]/div[2]/div[2]/div/div[2]/div[4]")
        print(care_maintenance_dict)

    def test(self, url):
        # try:
           browser = self.browser
           urls=self.get_urls_all_horses(browser, "https://stroy-podskazka.ru/loshadi/porody/")

           for u in range(11, 14):
               self.get_breed_info(browser, urls[u])
               print("\n-----------------------------------")



        # except  Exception as ex:
        #     print(ex)

hp = HorseParser()

hp.test("https://stroy-podskazka.ru/loshadi/porody/amerikanskaya-miniatyurnaya-loshad/")

sleep(10000)
#
# Сбор текста, какого - хз
hp.close_browser()