import requests
from bs4 import BeautifulSoup

# URL of the Latest Results page
url = "https://www.sharedata.co.za/v2/Scripts/LatestResults.aspx"

# Send a GET request to fetch the page content
response = requests.get(url)
response.raise_for_status()  # Raise an exception for HTTP errors

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(response.text, 'html.parser')

# Find all 'a' tags with the title 'View Results'
view_results_links = soup.find_all('a', title='View Results')

# Extract the href attribute from each 'a' tag and print it
for link in view_results_links:
    href = link.get('href')
    if href:
        full_url = f"https://www.sharedata.co.za{href}"
        print(full_url)
