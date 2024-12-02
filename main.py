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

    def get_breed_name(self, url):
        self.browser.get(url)
        sleep(1)  # Ждём загрузку страницы
        horse_breed_xpath = "/html/body/div[1]/div[2]/div[1]/h1"

        if self.xpath_exists(horse_breed_xpath):
            horse_breed = self.browser.find_elements(By.XPATH, horse_breed_xpath)
            horse_breed = [item.text for item in horse_breed]  # Порода
            return horse_breed[0]
        return None

    def get_characteristics(self, core_ref):

        core = f"{core_ref}/dl[1]"
        dictionary = {}
        i = 1
        while self.xpath_exists(core):
            dictionary[
                self.browser.find_element(By.XPATH, f"{core}/dt/span").text
            ] = self.browser.find_element(By.XPATH, f"{core}/dd").text
            i += 1
            core = f"{core_ref}/dl[{i}]"
        return dictionary

    def get_urls_all_horses(self,url):

        self.browser.get(url)
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
                    href = self.browser.find_elements(By.XPATH, path_element)
                    breed_list.append([item.get_attribute('href') for item in href][0])
                    i += 1
                    path_element = f"{path_group}/div/a[{i}]"

                j += 1
                path_group = f"{main_xpath}/div[{j}]"

            return breed_list

    def get_breed_info(self, url):

        horse_breed = self.get_breed_name(url).replace("Лошадь ", "")
        print(horse_breed)

        if self.browser.current_url != url:
            self.browser.get(url)

        # Переходим на вкладку с характеристиками
        if self.xpath_exists("/html/body/div[1]/div[2]/div[2]/ul/li[2]/a"):
            self.browser.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[2]/ul/li[2]/a").click()

        main_features_dict = self.get_characteristics("/html/body/div[1]/div[2]/div[2]/div/div[2]/div[1]")
        print(main_features_dict)

        appearance_dict = self.get_characteristics("/html/body/div[1]/div[2]/div[2]/div/div[2]/div[2]")
        print(appearance_dict)

        character_temperament_dict = self.get_characteristics("/html/body/div[1]/div[2]/div[2]/div/div[2]/div[3]")
        print(character_temperament_dict)

        care_maintenance_dict = self.get_characteristics("/html/body/div[1]/div[2]/div[2]/div/div[2]/div[4]")
        print(care_maintenance_dict)

    @staticmethod
    def get_last_paragraph(parent_element_xpath, parent_element):
        last_paragraph = parent_element.find_elements(By.XPATH,
                                                      f"{parent_element_xpath}//following::div[@class='text' and not(following::h2)]/*")
        par = ""
        for paragraph in last_paragraph:
            if not paragraph.text.__contains__("видео"):
                par += f"{paragraph.text}\n"
        return par

    @staticmethod
    def get_middle_paragraph(parent_element, xpath):

        el = parent_element.find_elements(By.XPATH,xpath)
        par = ""

        for subparagraph in el:
            par += f"{subparagraph.text}\n"

        return par

    def get_article(self, browser, url):

        if browser.current_url != url:
            browser.get(url)

            # На сайте 2 варианта страницы, с боковой панелью и без
            if self.xpath_exists("/html/body/div[1]/div[2]/div[2]/div/div[1]/article/aside/div"):
                parent_element_xpath= "/html/body/div[1]/div[2]/div[2]/div/div[1]/article/div[4]"
            else:
                parent_element_xpath="/html/body/div[1]/div[2]/div[2]/div/div[1]/article"

            parent_element = browser.find_element(By.XPATH, parent_element_xpath)

            article = {}
            h2_list=parent_element.find_elements(By.XPATH,f"{parent_element_xpath}/h2")
            if self.xpath_exists("/html/body/div[1]/div[2]/div[2]/div/div[1]/article/aside/div"):
                article["first_paragraph"]=parent_element.find_element(By.XPATH,f"{parent_element_xpath}/div[1]/p").text
            else:
                article["first_paragraph"] = parent_element.find_element(By.XPATH,f"{parent_element_xpath}/div[4]/p").text


            for i in range(0, len(h2_list) - 1):
                article[f"paragraph{i+2}"] = self.get_middle_paragraph(parent_element,
                f"{parent_element_xpath}//following::div[@class='text' and (preceding::h2[@id='{h2_list[i].get_attribute("id")}'])"
                f" and (following::h2[@id='{h2_list[i + 1].get_attribute("id")}'])]/*")

            article["last_paragraph"] = self.get_last_paragraph(parent_element_xpath, parent_element)


            print(article)



    def test(self, url):
        # try:
           #urls=self.get_urls_all_horses(browser, "https://stroy-podskazka.ru/loshadi/porody/")

           self.get_article(self.browser, url)

           # for u in range(11, 12):
           #     self.get_breed_info(browser, urls[u])
           #     print("\n-----------------------------------")



        # except  Exception as ex:
        #     print(ex)

hp = HorseParser()

#hp.test("https://stroy-podskazka.ru/loshadi/porody-i-masti/altajskogo-kraya/")
hp.test("https://stroy-podskazka.ru/loshadi/porody/bulonskaya/")

sleep(10000)

hp.close_browser()