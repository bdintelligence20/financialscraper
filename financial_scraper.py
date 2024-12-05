import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st
from io import BytesIO
import logging

# Base URL
BASE_URL = "https://www.sharedata.co.za"

# Configure logging
logging.basicConfig(filename="scraper.log", level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")

# Function to extract table data
def extract_table_data(table, company_name, category):
    rows = table.find_all("tr")
    data = []
    for row in rows[1:]:  # Skip header row
        cols = row.find_all("td")
        if len(cols) < 2:  # Skip rows with insufficient data
            continue
        metric = cols[0].text.strip()
        avg_growth = cols[1].text.strip() if len(cols) > 1 else None
        years_data = [col.text.strip() for col in cols[2:]]
        data.append([company_name, category, metric, avg_growth] + years_data)
    return data

# Function to scrape data for a single company
def scrape_company_data(company_url, company_name):
    try:
        response = requests.get(company_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        tables = soup.find_all("table")
        all_data = []
        categories = ["Income Statement", "Balance Sheet", "Share Statistics", "Ratios"]
        for idx, table in enumerate(tables[:4]):  # Limit to first 4 tables
            category = categories[idx]
            table_data = extract_table_data(table, company_name, category)
            all_data.extend(table_data)
        return all_data
    except Exception as e:
        logging.error(f"Error scraping company: {company_name} at {company_url} - {e}")
        return []

# Function to scrape all companies
def scrape_all_companies(username, password):
    try:
        login_url = f"{BASE_URL}/login"
        latest_results_url = f"{BASE_URL}/v2/Scripts/LatestResults.aspx"
        session = requests.Session()

        # Login
        credentials = {"username": username, "password": password}
        session.post(login_url, data=credentials)

        # Access the latest results page
        response = session.get(latest_results_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract company links
        links = [
            (BASE_URL + a["href"], a["href"].split("=")[-1])
            for a in soup.find_all("a", href=True, title="View Results")
        ]

        consolidated_data = []
        for link, company_name in links:
            st.write(f"Scraping: {company_name}")
            company_data = scrape_company_data(link, company_name)
            consolidated_data.extend(company_data)
        return consolidated_data
    except Exception as e:
        logging.error(f"Error in main scraping process: {e}")
        st.error("An error occurred during scraping. Please check the logs.")
        return []

# Streamlit App
def main():
    st.title("Financial Results Scraper")
    st.write("Scrape and consolidate financial data for multiple companies.")

    # Input credentials
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    # Start scraping
    if st.button("Scrape Data"):
        if not username or not password:
            st.error("Please enter your login credentials.")
            return

        # Scrape the data
        st.info("Scraping data, please wait...")
        raw_data = scrape_all_companies(username, password)

        if raw_data:
            # Create DataFrame
            columns = ["Company Name", "Category", "Metric", "Avg. Growth", "2024 Value", "2023 Value", "2022 Value", "2021 Value", "2020 Value"]
            df = pd.DataFrame(raw_data, columns=columns)

            # Display DataFrame
            st.write("Consolidated Financial Data")
            st.dataframe(df)

            # Download as Excel
            output = BytesIO()
            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                df.to_excel(writer, index=False, sheet_name="Financial Data")
            st.download_button(
                label="Download Excel File",
                data=output.getvalue(),
                file_name="financial_results_consolidated.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.error("No data was scraped. Please check your credentials or the website.")

if __name__ == "__main__":
    main()
