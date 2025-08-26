# django
import os, time
import unittest

# selenium
import selenium
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


class ProductsCategoryTests(unittest.TestCase):
    def setUp(self):
        self.BASE_URL = "http://localhost:8000"

        # run with hidden window
        options = Options()
        options.add_argument("--headless")

        self.browser = webdriver.Firefox(
            service=Service(GeckoDriverManager().install()), options=options
        )
        self.browser.implicitly_wait(30)
        # self.browser.maximize_window()

    def tearDown(self):
        self.browser.quit()

    def test_can_start_app(self):
        self.browser.get(f"{self.BASE_URL}")

        # user sees website title as tab title
        self.assertIn("Golden - Home", self.browser.title)

        # user sees different data lists
        data_list = [
            "product-categories",
            "showrooms",
            "stores",
            "catogory-product-group",
            "new-arrivals",
        ]

        for data_list_name in data_list:
            self.assertTrue(
                self.browser.find_element(
                    By.CSS_SELECTOR, f'ul[data-context="{data_list_name}"]'
                )
            )

    def test_user_click_product_tab(self):
        # user is at home page
        self.browser.get(f"{self.BASE_URL}/")

        # the user see the "product" tab and decides to click on it
        product_tab = self.browser.find_element(By.LINK_TEXT, "Products")
        product_tab.click()
        self.assertIn(f"Golden - Products", self.browser.title)

    def test_user_select_single_product(self):
        # user is at home page
        self.browser.get(f"{self.BASE_URL}/")

        # the user see an interesting product and decides to click on it
        product_category_group = self.browser.find_element(
            By.CSS_SELECTOR, f'[data-category-group-index="1"]'
        )

        # selecting first item in list
        selected_item = product_category_group.find_element(
            By.CSS_SELECTOR, '[data-product-index="1"]'
        )
        selected_item_name = selected_item.find_element(By.CSS_SELECTOR, "span").text
        selected_item.click()

        # user sees detail page with product that he selected
        product_name = self.browser.find_element(By.ID, "product-name").text
        self.assertEqual(product_name, selected_item_name)

    def test_user_selects_category(self):
        # at home page
        # user is at home page
        self.browser.get(f"{self.BASE_URL}/")

        # the user see the "categories" and decides to click on the first category
        selected_category = self.browser.find_element(
            By.CSS_SELECTOR, 'li[data-category-index="1"] a'
        )
        selected_category_name = selected_category.find_element(
            By.CSS_SELECTOR, "span"
        ).text

        selected_category.click()

        # use sees selected category name as tab title and page title
        self.assertIn(f"Golden - {selected_category_name}", self.browser.title)

        category_name = self.browser.find_element(By.ID, "category-name").text

        self.assertEqual(selected_category_name, category_name)

    def test_subcategory_select(self):
        # navigate category detail page
        # user is at home page

        self.browser.get(f"{self.BASE_URL}/")

        # the user see the "categories" and decides to click on the first category
        selected_category = self.browser.find_element(By.ID, "categories-view-all")

        selected_category.click()

        # on category list page
        self.assertIn(f"Golden - Categories", self.browser.title)

        # select first subcategory in first category
        category_list = self.browser.find_element(
            By.CSS_SELECTOR, '[data-category-index="1"]'
        )
        selected_subcategory = category_list.find_element(
            By.CSS_SELECTOR, '[data-subcategory-index="1"]'
        )
        selected_subcategory_name = category_list.find_element(
            By.CSS_SELECTOR, '[data-subcategory-index="1"]'
        ).text
        selected_subcategory.click()

        self.assertIn(f"Golden - {selected_subcategory_name}", self.browser.title)

        self.assertEqual(
            selected_subcategory_name,
            self.browser.find_element(By.ID, "sub_category_name").text,
        )


class ShowRoowTests(unittest.TestCase):
    def setUp(self):
        self.BASE_URL = "http://localhost:8000"

        # run with hidden window
        options = Options()
        options.add_argument("--headless")

        self.browser = webdriver.Firefox(
            service=Service(GeckoDriverManager().install()), options=options
        )
        self.browser.implicitly_wait(30)
        # self.browser.maximize_window()

    def tearDown(self):
        self.browser.quit()

    def test_click_showrooms_tab(self):
        # user is at home page
        self.browser.get(f"{self.BASE_URL}/")

        # the user see the "showrooms" tab and decides to click on it
        product_tab = self.browser.find_element(By.LINK_TEXT, "Showrooms")
        product_tab.click()
        self.assertIn(f"Golden - Showrooms", self.browser.title)

    def test_select_showroom(self):
        # user is at home page
        self.browser.get(f"{self.BASE_URL}/")

        selected_showroom = self.browser.find_element(
            By.CSS_SELECTOR, "[data-showroom-index='1']"
        )
        selected_showroom_name = selected_showroom.find_element(
            By.CSS_SELECTOR, "p"
        ).text

        selected_showroom.click()

        # redirected to showroom page
        self.assertIn(f"Golden - {selected_showroom_name}", self.browser.title)

        # one storeroom list page
        self.browser.get(f"{self.BASE_URL}/showrooms/")

        selected_showroom = self.browser.find_element(
            By.CSS_SELECTOR, "[data-showroom-index='1']"
        )
        selected_showroom_name = selected_showroom.find_element(
            By.CSS_SELECTOR, "p"
        ).text

        selected_showroom.click()

        # redirected to showroom page
        self.assertIn(f"Golden - {selected_showroom_name}", self.browser.title)

    def test_select_store(self):

        # navigate showroom detail page
        # user is at home page
        self.browser.get(f"{self.BASE_URL}/")

        selected_showroom = self.browser.find_element(
            By.CSS_SELECTOR, "[data-showroom-index='1']"
        )
        selected_showroom.click()

        # on showroom detail page
        # user clicks on store item
        selected_store = self.browser.find_element(
            By.CSS_SELECTOR, "[data-store-index='1']"
        )
        selected_store_name = selected_store.find_element(By.CSS_SELECTOR, "p").text

        selected_store.click()

        self.assertIn(f"Golden - {selected_store_name}", self.browser.title)


if __name__ == "__main__":
    unittest.main()
