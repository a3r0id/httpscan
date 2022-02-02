from bs4 import BeautifulSoup as BS
from json import dumps

# [i] HTML parsed results go to notes!

def parseHTML(html):
    
    if html == None:
        return []

    try:
        soup = BS(html, 'html.parser')
    except:
        return []
    
    try:
        # Get title text
        title = soup.title.text.lower()
    except:
        title = "None"
        
    hrefs = [link.get('href') for link in soup.findAll('a')]

    notes = [
        f"URLs: {dumps(hrefs, default=str)}",
        f"Page Title: \"{title}\"."
    ]

    return notes
    