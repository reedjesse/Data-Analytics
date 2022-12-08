import pandas as pd
import requests
from tqdm import tqdm
from sqlalchemy import create_engine
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver import ChromeOptions

#main function
def ScrapeJob():
    keyword = input('Enter Keyword:')
    p = int(input('Enter number of pages:'))
    url = 'https://malaysia.indeed.com/jobs?q='+keyword
    pages = p*10
    indeed = {'Url':[],'Job Link':[], 'Job Description':[], 'Title':[],'Company':[],'Rating':[],'Location':[],'Posted':[],'Salary':[]}
    options = ChromeOptions()
    # options.headless = True
    driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=options)
    for i in tqdm(range(0,pages,10)):
        try:
            link = url+'&start='+str(i)
            driver.get(link)
            time.sleep(5)
            element = driver.find_element(By.XPATH, "/html/body")
            soup = BeautifulSoup(element.get_attribute('outerHTML'), "html.parser")
            container = soup.find('div', id='mosaic-provider-jobcards')
            ul = container.find('ul', class_='jobsearch-ResultsList css-0')
            lis = ul.find_all('li')
            for i in lis:
                try:
                    job_url = i.find('h2', class_='jobTitle').a['href']
                    job_url = 'https://malaysia.indeed.com' + str(job_url)
                    title = i.find('h2', class_='jobTitle').text.strip()
                    company = i.find('span', class_='companyName').text
                    try: #rating can be null
                        rating = i.find('span', class_='ratingNumber').text 
                    except:
                        rating = 'NULL'
                    location = i.find('div', class_='companyLocation').text
                    posted = i.find('span', class_='date').text.strip().replace('Posted', '')
                    try: #salary can be null
                        salary = i.find('div', class_='metadata salary-snippet-container').text.strip()
                    except:
                        salary = ''
                    job_description = getJobDesc(job_url)
                    print(link)
                    print(job_url)
                    print(title)
                    print(company)
                    print(rating)
                    print(location)
                    print(posted)
                    print(salary)
                    print(job_description)
                    print('<------------------------------------------------------------------------------>')
                    indeed['Url'].append(link)
                    indeed['Job Link'].append(job_url) # Link
                    indeed['Title'].append(title) # Title
                    indeed['Company'].append(company) # Company
                    indeed['Rating'].append(rating) # Rating
                    indeed['Location'].append(location) # Location
                    indeed['Posted'].append(posted) # Posted
                    indeed['Salary'].append(salary) # Salary
                    indeed['Job Description'].append(job_description) # Description
                except Exception as e:
                    pass
        # driver.quit()
        except Exception as c:
            print('error',c)
    driver.quit()
    indeed_df = pd.DataFrame(indeed)
    indeed_df.drop_duplicates(ignore_index=True,inplace=True)
    try:
        indeed_df['Min Salary'] = indeed_df['Salary'].str.split('-',expand=True)[0]
        indeed_df['Max Salary'] = indeed_df['Salary'].str.split('-',expand=True)[1]
    except Exception as e:
        indeed_df['Min Salary'] = 'NULL'
        indeed_df['Max Salary'] = 'NULL'
        # print('error1', e)
    indeed_df.drop('Salary',axis=1,inplace=True)
    indeed_df.to_csv('indeed_jobs_data_analyst.csv',index=False)

    #For saving to database
    #engine = create_engine('mysql+pymysql://root@localhost:3306/jobsearch') 
    #indeed_df.to_sql(con=engine,name='jobs',if_exists='append',index=False)

#function for scraping job description on individual page
def getJobDesc(url):
options = ChromeOptions()
driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=options)
driver.get(url)
time.sleep(5)
element = driver.find_element(By.XPATH, "/html/body")
soup = BeautifulSoup(element.get_attribute('outerHTML'), "html.parser")
jobDesc = soup.find('div', id='jobDescriptionText')
# kill all script and style elements
for script in jobDesc(["script", "style"]):
  script.extract()    # rip it out
# get text
text = jobDesc.get_text()

# break into lines and remove leading and trailing space on each
lines = (line.strip() for line in text.splitlines())

# break multi-headlines into a line each
chunks = (phrase.strip() for line in lines for phrase in line.split("  "))

# drop blank lines
text = '\n'.join(chunk for chunk in chunks if chunk)

return text
