# imports
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import csv

# simple way to work out the key/value pairs here
def grabValue(content, string):
  heading = content.find("h3", string=string)
  variable = heading.find_next("div", class_="field-value").text if heading else ""
  return variable

# write csv file
with open('scraping/bulletin.csv', 'w', newline='', encoding='utf-8') as csvfile:
  writer = csv.writer(csvfile, delimiter=',')
  writer.writerow([
      "Course_Code",
      "Course_Name",
      "Dept",
      "Career",
      "Prerequsites",
      "Satisfies",
      "Typically_Offered",
      "Final_Exam"
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
        #course code and course name
        courseCode = course.find("span", class_="pill-label").text
        courseName = course.find("a").text
        
        # go to the course's dedicated page
        newurl = course.find("a").get("href")
        driver.get(f"https://bulletin.pugetsound.edu{newurl}")
        
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        content = soup.find("section")
        
        # keys whose values i want to grab
        # to do: handling for courses with multiple departments
        searches = [
          "Department(s)", 
          "Career", 
          "Prerequisites", 
          "Catalog Course Attributes",
          "Course Typically Offered",
          "Final Exam Type"]
        
        # results for every search
        results = []
        for search in searches:
          results.append(grabValue(content, search))
        
        writer.writerow([
          courseCode,
          courseName,
          
          # kind of a nightmare for right now
          results[0], # dept
          results[1], # career
          results[2], # prereqs
          results[3], # satisfies
          results[4], # offered
          results[5] # final exam
        ])
    else: 
      driver.close()
      quit()
    
    page+=1