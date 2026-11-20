# imports
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import csv

# write csv file
with open('bulletin.csv', 'w', newline='', encoding='utf-8') as csvfile:
  writer = csv.writer(csvfile, delimiter=',')
  writer.writerow([
      "Course_Code",
      "Course_Name"
    ])
  
  # standard driver init
  options = webdriver.FirefoxOptions()
  driver = webdriver.Firefox(options=options)

  # for making urls
  page = 1
  
  while True:
    url = f"https://bulletin.pugetsound.edu/courses?page={page}"
    driver.get(url)

    # wait until the results have loaded
    # to do: create a case where loading has finished but there are no
    # classes left to scrape (empty page)
    WebDriverWait(driver, 30).until(
      EC.presence_of_element_located((By.CLASS_NAME, "courses__list "))
    )
    
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    courseList = soup.find("ul", class_="courses__list")
    results = courseList.find_all("li")
    
    if results:
      print(f"Courses found on page {page}!")
      
      # to do: threading for other attributes
      for course in results:
        courseCode = course.find("span", class_="pill-label").text
        courseName = course.find("a").text
        
        writer.writerow([
          courseCode,
          courseName
        ])
    else: 
      quit()
    
    page+=1