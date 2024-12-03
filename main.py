import re
import json

from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait


class HorseParser:

    def __init__(self):
        self.browser = webdriver.Chrome()

    # метод для закрытия браузера
    def close_browser(self):

        self.browser.close()
        self.browser.quit()
    #Проверка, существует ли xpath
    def xpath_exists(self, url):

        browser = self.browser
        try:
            browser.find_element(By.XPATH,url)
            exist = True
        except NoSuchElementException:
            exist = False
        return exist
    #Получить название породы
    def get_breed_name(self, url):
        if self.browser.current_url != url:
            self.browser.get(url)
        WebDriverWait(self.browser, 10).until(ec.presence_of_element_located((By.TAG_NAME, "html")))  # Ждём загрузку страницы
        horse_breed_xpath = "/html/body/div[1]/div[2]/div[1]/h1"

        if self.xpath_exists(horse_breed_xpath):
            return self.browser.find_elements(By.XPATH, horse_breed_xpath)[0].text# Порода

        return None
    #Получить характеристики породы по переданному блоку
    def get_characteristic(self, parent_element_xpath):

        core = f"{parent_element_xpath}/dl[1]"
        characteristics = {}
        i = 1
        while self.xpath_exists(core):
            characteristics[
                self.browser.find_element(By.XPATH, f"{core}/dt/span").text
            ] = self.browser.find_element(By.XPATH, f"{core}/dd").text
            i += 1
            core = f"{parent_element_xpath}/dl[{i}]"
        return characteristics
    #Получить ссылки на все посты(породы)
    def get_urls_all_breeds(self, url):

        if self.browser.current_url != url:
            self.browser.get(url)

        main_xpath = "/html/body/div/div[2]/div[2]/div[5]"

        if self.xpath_exists(main_xpath):
            path_group = f"{main_xpath}/div[1]"
            breed_list = []
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
    #Получить характеристики породы
    def get_breed_characteristics(self, url):

        if self.browser.current_url != url:
            self.browser.get(url)

        characteristics = {}

        # Переходим на вкладку с характеристиками
        if self.xpath_exists("/html/body/div[1]/div[2]/div[2]/ul/li[2]/a"):
            self.browser.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[2]/ul/li[2]/a").click()

        main_features_dict = self.get_characteristic("/html/body/div[1]/div[2]/div[2]/div/div[2]/div[1]")
        characteristics["main_features"] = main_features_dict

        appearance_dict = self.get_characteristic("/html/body/div[1]/div[2]/div[2]/div/div[2]/div[2]")
        characteristics["appearance"] = appearance_dict

        character_temperament_dict = self.get_characteristic("/html/body/div[1]/div[2]/div[2]/div/div[2]/div[3]")
        characteristics["character_temperament"] = character_temperament_dict

        care_maintenance_dict = self.get_characteristic("/html/body/div[1]/div[2]/div[2]/div/div[2]/div[4]")
        characteristics["care_maintenance_dict"] = care_maintenance_dict

        return characteristics
    #Получить последний абзац
    @staticmethod
    def get_last_paragraph(parent_element_xpath, parent_element):
        last_paragraph = parent_element.find_elements(By.XPATH,
                                                      f"{parent_element_xpath}//following::div[@class='text' and not(following::h2)]/*")
        par = ""
        for paragraph in last_paragraph:
            #Убираем часть с видео
            if not paragraph.text.__contains__("видео"):
                par += f"{paragraph.text}\n"
        return par
    #Получить абзацы между последним и первым
    @staticmethod
    def get_middle_paragraph(parent_element, xpath):

        el = parent_element.find_elements(By.XPATH,xpath)
        par = ""
        for subparagraph in el:
            par += f"{subparagraph.text}\n"
        return par
    #Получить изображения
    @staticmethod
    def get_images(parent_element_xpath, parent_element,attrib):
            images = parent_element.find_elements(By.XPATH,f"{parent_element_xpath}")
            return (img.get_attribute(attrib) for img in images)
    #Получить статью
    def get_article(self, url):
            if self.browser.current_url != url:
                self.browser.get(url)

            # На сайте 2 варианта страницы, с боковой панелью и без
            if self.xpath_exists("/html/body/div[1]/div[2]/div[2]/div/div[1]/article/aside/div"):
                parent_element_xpath = "/html/body/div[1]/div[2]/div[2]/div/div[1]/article/div[4]"
            else:
                parent_element_xpath ="/html/body/div[1]/div[2]/div[2]/div/div[1]/article"

            parent_element = self.browser.find_element(By.XPATH, parent_element_xpath)

            article = {}
            h2_list = parent_element.find_elements(By.XPATH,f"{parent_element_xpath}/h2")#Получить все заголовки

            #Записываем первый параграф
            if self.xpath_exists("/html/body/div[1]/div[2]/div[2]/div/div[1]/article/aside/div"):
                article["first_paragraph"] = parent_element.find_element(By.XPATH,f"{parent_element_xpath}/div[1]/p").text
            else:
                article["first_paragraph"] = parent_element.find_element(By.XPATH,f"{parent_element_xpath}/div[4]/p").text

            #Записываем параграфы между первым и последним
            for i in range(0, len(h2_list)):
                article[f"header{i+1}"] = h2_list[i].text#Добавить заголовок
                if i < len(h2_list) - 1:
                    article[f"paragraph{i+2}"] = self.get_middle_paragraph(parent_element,
                    f"{parent_element_xpath}//following::div[@class='text' and (preceding::h2[@id='{h2_list[i].get_attribute("id")}'])"
                    f" and (following::h2[@id='{h2_list[i + 1].get_attribute("id")}'])]/*") #Добавить параграф

            # Записываем последний параграф
            article["last_paragraph"] = self.get_last_paragraph(parent_element_xpath, parent_element)

            imgs_from_article = []
            domain=url.split("/")[2] #Получаем домен сайта

            #Получаем динамические изображения
            #Адрес разбит по тэгам домен + s + r + c
            imgs_from_article_s = list(self.get_images(f"{parent_element_xpath}//following::img[@s]",parent_element,"s"))
            imgs_from_article_r = list(self.get_images(f"{parent_element_xpath}//following::img[@s]",parent_element,"r"))
            imgs_from_article_c = list(self.get_images(f"{parent_element_xpath}//following::img[@s]",parent_element,"c"))

            #Получаем изображения из статьи
            for i in range(0,len(imgs_from_article_s)):
                imgs_from_article.append(f"https://{domain}{imgs_from_article_s[i]}{imgs_from_article_r[i]}{imgs_from_article_c[i]}")
                #Заменяем миниатюры на оригинальные изображения
                imgs_from_article[i] = (imgs_from_article[i].replace(
                    re.search(r"(\w+/(\d*))-\d*/",imgs_from_article[i]).group(), "/orig/"))

            #Записываем изображения из статьи
            article["images_from_article"] = imgs_from_article

            return article
    #Получить породу
    def get_breed(self, url):
        if self.browser.current_url != url:
            self.browser.get(url)
        WebDriverWait(self.browser, 10).until(ec.presence_of_element_located((By.TAG_NAME, "html")))
        # Записываем название(удаляя из него лишнее) и характеристики
        breed = {"copyright": url,
                 "name": self.get_breed_name(url).replace("Лошадь ", ""),
                 "characteristics": self.get_breed_characteristics(url)}

        general_images=[]
        #Получаем основные изображения
        if self.xpath_exists("/html/body/div[1]/div[2]/div[2]/div/div[1]/article/div[1]/div[1]/div[2]/div/img"):
            general_images = self.get_images("/html/body/div[1]/div[2]/div[2]/div/div[1]/article/div[1]/div[1]/div[2]/div/img",
                                     self.browser, "src")
            # Заменяем миниатюры на оригинальные изображения
            general_images = list((img.replace(
                re.search(r"(\w+/(\d*))-\d*/", img).group(), "/orig/") for img in general_images))

        #Записываем основные изображения
        breed["general_images"] = general_images
        #Получаем статью
        article = self.get_article(url)
        #Записываем статью
        breed["article"] = article

        return breed
    #Собрать все данные в json
    def create_breeds_json(self):
        urls=self.get_urls_all_breeds("https://stroy-podskazka.ru/loshadi/porody/")

        for u in range(0, len(urls)):
            print(f"{u+1}/{len(urls)} - {self.get_breed_name(urls[u])}")

            breed = self.get_breed(urls[u])

            with open(f"outputs/{breed["name"]}.json", "w", encoding="utf-8") as f:
                json.dump(breed, f, indent=4, ensure_ascii=False)

            #if u%10==0 and u!=0:
              #  sleep(80)#Вроде бы сайт начинает тупить от кол-ва запросов

hp = HorseParser()

#hp.test("https://stroy-podskazka.ru/loshadi/porody-i-masti/altajskogo-kraya/")
hp.create_breeds_json()

hp.close_browser()

# with open('result.json', 'r', encoding="utf-8") as json_file:
#     data = json.load(json_file)
#     print(data)