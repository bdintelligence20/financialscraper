import requests
from bs4 import BeautifulSoup
import streamlit as st

# Function to extract "View Results" links
def extract_links():
    url = "https://www.sharedata.co.za/v2/Scripts/LatestResults.aspx"

    # Headers and cookies from your request
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
        "Connection": "keep-alive",
        "Referer": "https://www.sharedata.co.za/",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0",
    }

    cookies = {
        "SDORecentlyViewed": "List=47896,5733,103&LastUsed=2024/12/03 10:13:10",
        "sdoCookieTest": "OK",
        "SDOv2": "V2=1",
        "SDOTrial": "Email=nicholasflemmer@gmail.com&Applied=2024/12/03 13:18:59",
        "SDO_chart": "SDO_chart",
        "SDOCompanyPage": "/v2/Scripts/Results.aspx?c=#JSECODE#",
        "SDO_token": "HDS31HKKCEBNZJAJZ7BJGF1K4CCI8EJBQYU1MABIBG60G41QCGYOL7TGADC1EF",
        "BrandingPage": "",
        "SDOSubscriber": "Email=nicholasflemmer@gmail.com&LoginEmail=nicholasflemmer@gmail.com&LastLogin=2024/12/05 08:24:41",
        "SDOVC": "2024/12/05 08:24:41",
        "UID": "ID=4283&DateTime=2024/12/05 08:24:41",
    }

    try:
        # Fetch the page content
        response = requests.get(url, headers=headers, cookies=cookies)
        response.raise_for_status()

        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all "View Results" links
        links = [
            f"https://www.sharedata.co.za{a['href']}"
            for a in soup.find_all('a', href=True)
            if "Results.aspx?c=" in a['href']
        ]
        return links
    except Exception as e:
        st.error(f"Error extracting links: {e}")
        return []

# Streamlit App
def main():
    st.title("Extract 'View Results' Links")
    st.write("This app extracts all 'View Results' links from the ShareData Latest Results page.")

    if st.button("Extract Links"):
        st.info("Extracting links...")
        links = extract_links()

        if links:
            st.success(f"Extracted {len(links)} links.")
            for link in links:
                st.write(link)

            # Provide a download button for the links
            links_text = "\n".join(links)
            st.download_button(
                label="Download Links",
                data=links_text,
                file_name="view_results_links.txt",
                mime="text/plain"
            )
        else:
            st.warning("No links were found.")

if __name__ == "__main__":
    main()
