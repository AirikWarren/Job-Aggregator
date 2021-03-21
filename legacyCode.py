import os
import webbrowser

import requests
from jinja2 import Environment
from jinja2.loaders import FileSystemLoader

# CONFIG VARIABLES
number_of_requests = 5
keywords = [
    'c',
    'python',
    'junior'
] # values inside this list used for tags / filtering search result

CHECKMARK = '�'
# This is an emoji that Github accepts as a parameter in their query strings for some
# reason 

def send_requests_and_filter(page=number_of_requests, keywords=keywords) -> list:
    '''First sends $page numbers of requests to the github jobs endpoint, 
    filters the resulting list using the keywords passed to it,
    returns a list of the filtered results''' 
    print(f"Sending request {page}")
    r = requests.get(
        'https://jobs.github.com/positions.json',
        params={ "utf8":CHECKMARK, "page":str(page)}
    )
    r.raise_for_status()
    if r.json() == None:
        return []
    else:
        jobs = r.json()  
    print(f"returned {len(jobs)} jobs")
    jobs_with_keywords = [job_post for job_post in jobs if any((x in job_post['description'].lower()) for x in keywords)] 
    print(f"Narrowing down to {len(jobs_with_keywords)} that have your keywords")
    return jobs_with_keywords 

def calculate_match(job_posting_desc : str, keywords=keywords) -> float:
    '''returns a float which can be easily represented as a percentage via string formatting'''
    matches = 0
    max_matches = len(keywords)
    for x in keywords:
        if x.lower() in job_posting_desc:
            matches += 1
    return matches / max_matches if matches > 0 else 0.0

def generate_tags_list(job_posting_desc : str, keywords=keywords) -> list:
    '''a list of keywords found in a job_posting_desc, used to generate the little 
    tags seen to the left of the percentage in the rendered HTML'''
    return [x for x in keywords if x.lower() in job_posting_desc]

def render_html_templates(outfile : str ='jobPostings.html') -> None:
    '''initializes a Jinja 2 environment and renders 'jobs.html' from it'''
    env = Environment(loader=FileSystemLoader('./templates'))
    page = env.get_template('jobs.html')

    with open('jobPostings.html', 'w', encoding='utf-8') as fp:
        fp.write(str(page.render(jobs_list=jobs_list)))

if __name__ == "__main__":
    jobs_list = list()
    for i in number_of_requests:
        current_page_results = send_requests_and_filter(page=i)
        if len(current_page_results > 0):
            jobs_list.extend(current_page_results)
            print(f"current jobs: {len(jobs_list)}")
    
    for job_posting in jobs_list:
        job_posting["match_percent"] = calculate_match(job_posting["description"].lower())
        job_posting["tag_list"] = generate_tags_list(job_posting["description"].lower())
    
    jobs_list = sorted(jobs_list, key=lambda k: k['match_percent'])[::-1] # sorts the list, reverses it

    # opens up the file in your web browser
    os.path.abspath(os.curdir)
    webbrowser.open(os.path.join(os.path.abspath(os.curdir), './jobPostings.html'))