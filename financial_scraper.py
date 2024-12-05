from playwright.sync_api import sync_playwright
import streamlit as st

# Function to extract links using Playwright
def extract_links():
    url = "https://www.sharedata.co.za/v2/Scripts/LatestResults.aspx"
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()

            # Navigate to the URL
            page.goto(url)

            # Wait for the content to load
            page.wait_for_timeout(5000)  # Adjust as needed

            # Extract links
            links = [
                f"https://www.sharedata.co.za{a.get_attribute('href')}"
                for a in page.query_selector_all("a[title='View Results']")
            ]

            browser.close()
            return links
    except Exception as e:
        st.error(f"Error extracting links: {e}")
        return []

# Streamlit App
def main():
    st.title("Extract 'View Results' Links with Playwright")
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
