from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()
driver.get("https://www.nba.com/stats/leaders/?Season=2021-22&SeasonType=Regular%20Season")
s = driver.find_element(By.CLASS_NAME,"stats-table-pagination")
s = driver.find_element(By.XPATH,"/html/body/main/div/div/div[2]/div/div/nba-stat-table/div[1]/div/div/select")
s = Select(s)
s.select_by_visible_text("All")