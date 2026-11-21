# imports
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from tqdm import tqdm
import csv
import time
import random as r

# standard driver init
options = webdriver.FirefoxOptions()
driver = webdriver.Firefox(options=options)

# constants
CSV_NAME = "scraping/courses.csv" # save file as
PAGE = 1                           # page to start on (inclusive)
PAGE_STOP = 3                      # page to end on (inclusive)
THROTTLE = 2                       # rate at which to send requests
ATTEMPTS = 1                       # amount of times to recurse on error

# other variables
department_urls = set(())          # no duplicate urls

# simple way to work out the key/value pairs here
def grabValue(content, string):
  heading = content.find("h3", string=string)
  variable = heading.find_next("div", class_="field-value").text if heading else ""
  return variable

# if the server is overloaded it will check if you're human.
# this allows the user to complete the captcha, confirm that 
# they have done this, and try again. 
def pageResults(url, tries=0):
  if(driver):
    # if the user has said "yes" without completing the captcha
    # a specified number of times, quit. 
    if(tries > ATTEMPTS):
      deptDump()
      driver.close()
      quit()
      
    driver.get(f"https://bulletin.pugetsound.edu{url}")
    html = driver.page_source
    
    # manual handling
    if "confirm you are human" in html:
      canContinue = input("\nCaptcha encountered. Continue? (y/n): ").strip().lower()
      if(canContinue == "y"):
        tries+=1
        return pageResults(url, tries)
      else:
        deptDump()
        driver.close()
        quit()
    else:
      return html
  else:
    deptDump()
    quit()
    
# write department urls for department scraper
def deptDump():
  print(f"Found {len(department_urls)} total departments")
  if(department_urls):
    with open('scraping/departments.txt', "w", encoding="utf-8") as file:
      for dept in department_urls:
        file.write(f"{dept}\n")

# write csv file
with open(f'{CSV_NAME}', 'w', newline='', encoding='utf-8') as csvfile:
  writer = csv.writer(csvfile, delimiter=',')
  
  # columns
  writer.writerow([
      "Course_Code",
      "Course_Name",
      "Dept",
      "Career",
      "Prerequsites",
      "Satisfies",
      "Typically_Offered",
      "Final_Exam",
      "Credits"
    ])
  
  for i in range(PAGE, PAGE_STOP+1, 1):
    url = f"https://bulletin.pugetsound.edu/courses?page={i}"
    driver.get(url)

    # wait until the results have loaded
    # to do: create a case where loading has finished but there are no
    # classes left to scrape (empty page)
    try:
      WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CLASS_NAME, "courses__list "))
      )
    except: 
      print("Timeout")
      driver.close()
      quit()
    
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    courseList = soup.find("ul", class_="courses__list")
    results = courseList.find_all("li")
    
    if results:
      print(f"Courses found on page {i}!")
      
      for course in tqdm(results):
        #course code and course name
        courseCode = course.find("span", class_="pill-label").text
        courseName = course.find("a").text
        
        # go to the course's dedicated page
        newurl = course.find("a").get("href")
        html = pageResults(newurl)

        # throttle
        time.sleep(r.randrange(2, 4))
        
        soup = BeautifulSoup(html, "html.parser")
        content = soup.find("section")
        
        # for department scraping
        deptUrl = content.find("h3", string="Department(s)").find_next("a").get("href")
        department_urls.add(f"https://bulletin.pugetsound.edu{deptUrl}")
        
        # keys whose values i want to grab
        # to do: handling for courses with multiple departments (can't find any examples)
        searches = [
          "Department(s)", 
          "Career", 
          "Prerequisites", 
          "Catalog Course Attributes",
          "Course Typically Offered",
          "Final Exam Type", 
          "Max Units"]
        
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
          results[5], # final exam
          results[6], # credits
        ])
    else: 
      deptDump()
      driver.close()
      quit()
    
    deptDump()
    
  deptDump()
  driver.close()
  quit()
