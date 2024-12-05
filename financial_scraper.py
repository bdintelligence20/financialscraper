import requests
from bs4 import BeautifulSoup
import streamlit as st

# Function to extract "View Results" links
def extract_links():
    url = "https://www.sharedata.co.za/v2/Scripts/LatestResults.aspx"
    try:
        # Fetch the page content
        response = requests.get(url)
        response.raise_for_status()

        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all "View Results" links based on the structure provided
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
