from bs4 import BeautifulSoup as BS
from json import dumps
import re

def parseHTML(html):

    notes = []
    soup = BS(html, 'html.parser')
    
    # Get title text
    title = soup.title.text.lower()
    hrefs = []
    try:
        for link in soup.findAll('a'):
            hrefs.append(link.get('href'))
    except Exception as e:
        print(e)
        
    notes.append(f"Hrefs: {dumps(hrefs, default=str)}")
    
    notes.append(f"Page Title: \"{title}\".")
        
        
    
    return notes
    