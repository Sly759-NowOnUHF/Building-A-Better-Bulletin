from pathlib import Path
import pandas as pd

# all files in directory
script_dir = Path(__file__).resolve().parent
course_files = list((script_dir / "results").rglob("courses*.csv"))
dept_files = list((script_dir / "results").rglob("depts*.csv"))
 
# append csvs
combined_courses = pd.concat(
  [pd.read_csv(csv) for csv in course_files], ignore_index=True)
combined_departments = pd.concat(
  [pd.read_csv(csv) for csv in dept_files], ignore_index=True)

# satisfies csv
satisfies = combined_courses[["Course_Code", "Satisfies"]]

# this regex keeps from splitting values inside parentheses
# this handles knowledge, identity, and power
satisfies["Satisfies"] = satisfies["Satisfies"].str.strip().str.split(r",\s*(?![^()]*\))", regex=True)
satisfies_csv = satisfies.explode("Satisfies").dropna().reset_index()[["Course_Code", "Satisfies"]]

# processing departments
combined_departments["Duplicate"] = combined_departments.duplicated()
combined_departments = combined_departments.loc[combined_departments["Duplicate"] == False, ["Department_Code","Department_Name","Department_URL"]].sort_values(by=["Department_Code"])

combined_courses.to_csv("scraping/courses.csv", index=False)
combined_departments.to_csv("scraping/departments.csv", index=False)
satisfies_csv.to_csv("scraping/satisfies.csv", index=False)