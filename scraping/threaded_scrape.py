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
import threading

# INPUT_LOCK = threading.Lock()

# def lockedInput(prompt):
#   with INPUT_LOCK:
#     return input(prompt)

# simple way to work out the key/value pairs here
def grabValue(content, string):
  heading = content.find("h3", string=string)
  variable = heading.find_next("div", class_="field-value").text if heading else ""
  return variable

# write csv file
def crawl(PAGE_START=1, PAGE_STOP=5):
  COURSE_CSV = f"scraping/results/courses{PAGE_START}-{PAGE_STOP}.csv"
  DEPT_CSV = f"scraping/results/depts{PAGE_START}-{PAGE_STOP}.csv"
  department_urls = set(())
  
  try: 
    # standard driver init
    options = webdriver.FirefoxOptions()
    driver = webdriver.Firefox(options=options)
    
    # if the server is overloaded it will check if you're human.
    # this allows the user to complete the captcha, confirm that 
    # they have done this, and try again. 
    # def pageResults(url, tries=0):
    #   if(driver):
    #     # if the user has said "yes" without completing the captcha
    #     # a specified number of times, quit. 
    #     if(tries > 1):
    #       deptDump()
          
    #     driver.get(f"https://bulletin.pugetsound.edu{url}")
    #     html = driver.page_source
        
    #     # manual handling
    #     if "confirm you are human" in html:
    #       canContinue = lockedInput("\nCaptcha encountered. Continue? (y/n): ").strip().lower()
    #       if(canContinue == "y"):
    #         tries+=1
    #         return pageResults(url, tries)
    #       else:
    #         deptDump()
    #     else:
    #       return html
    #   else:
    #     deptDump()
    
    # write department urls for department scraper
    def deptDump():
      if(department_urls):
        with open(DEPT_CSV, "w", newline='', encoding="utf-8") as file:
          write = csv.writer(file, delimiter=',')
          
          write.writerow([
            "Department_Code",
            "Department_Name",
            "Department_URL"
          ])
          
          for dept in department_urls:
            write.writerow([
              dept[0],
              dept[1],
              dept[2]
            ])
          
    with open(f'{COURSE_CSV}', 'w', newline='', encoding='utf-8') as csvfile:
      writer = csv.writer(csvfile, delimiter=',')
      
      # columns
      writer.writerow([
          "Course_Code",
          "Course_Name",
          "Course_Description",
          "Dept",
          "Career",
          "Prerequsites",
          "Satisfies",
          "Typically_Offered",
          "Final_Exam",
          "Credits"
        ])
      
      for i in range(PAGE_START, PAGE_STOP+1, 1):
        url = f"https://bulletin.pugetsound.edu/courses?page={i}"
        driver.get(url)

        # wait until the results have loaded
        # to do: create a case where loading has finished but there are no
        # classes left to scrape (empty page)
        try:
          WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CLASS_NAME, "courses__list"))
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
            driver.get(f"https://bulletin.pugetsound.edu{newurl}")
            try:
              WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.CLASS_NAME, "field-label"))
              )
            except: 
              print("Timeout")
              driver.close()
              quit()
              
            html = driver.page_source

            # throttle
            time.sleep(r.randrange(2, 4))
            
            soup = BeautifulSoup(html, "html.parser")
            content = soup.find("section")
            
            # keys whose values i want to grab
            # to do: handling for courses with multiple departments (can't find any examples)
            searches = [
              "Course Description",
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
              results[0], # description
              results[1], # dept
              results[2], # career
              results[3], # prereqs
              results[4], # satisfies
              results[5], # offered
              results[6], # final exam
              results[7], # credits
            ])
            
            # for department scraping
            deptUrl = content.find("h3", string="Department(s)").find_next("a").get("href")
            dept = courseCode.split(" ")[0]
            department_urls.add((dept, results[1], f"https://bulletin.pugetsound.edu{deptUrl}"))
        else: 
          deptDump()
          driver.close()
          quit()
        
        deptDump()
        
      deptDump()
      driver.close()
      quit()
  finally:
    driver.quit()

threads = []    

for start in range(1, 84, 20):
  end = min(start + 19, 83)
  t = threading.Thread(target=crawl, args=(start, end))
  threads.append(t)

for t in threads:
  t.start()

for t in threads:
  t.join()