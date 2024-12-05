import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import pandas as pd
import streamlit as st
import time

# Function to initialize Selenium driver
def init_driver():
    options = uc.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = uc.Chrome(options=options)
    return driver

# Function to log in
def login(driver, username, password):
    try:
        login_url = "https://www.sharedata.co.za/v2/Scripts/Home.aspx"
        driver.get(login_url)

        # Click the login button to open the modal
        login_button = driver.find_element(By.XPATH, "//td[@class='brandingmenulink' and contains(text(), 'Login')]")
        login_button.click()
        time.sleep(2)

        # Enter credentials and log in
        driver.find_element(By.ID, "Branding_LblLoginEmail").send_keys(username)
        driver.find_element(By.ID, "Branding_LblLoginPwd").send_keys(password)
        driver.find_element(By.XPATH, "//button[contains(text(), 'Login')]").click()
        time.sleep(3)

        return "Logout" in driver.page_source  # Check if login succeeded
    except Exception as e:
        st.error(f"Login failed: {e}")
        return False

# Function to extract data
def extract_data(driver):
    base_url = "https://www.sharedata.co.za"
    results_url = f"{base_url}/v2/Scripts/LatestResults.aspx"
    data = []

    # Navigate to results page
    driver.get(results_url)
    time.sleep(5)

    # Get all "View Results" links
    links = [a.get_attribute("href") for a in driver.find_elements(By.XPATH, "//a[@title='View Results']")]

    # Visit each company page and extract data
    for link in links:
        driver.get(link)
        time.sleep(3)

        # Extract table data
        company_name = link.split("=")[-1]
        tables = driver.find_elements(By.TAG_NAME, "table")

        categories = ["Income Statement", "Balance Sheet", "Share Statistics", "Ratios"]
        for idx, table in enumerate(tables[:4]):  # First 4 tables correspond to these categories
            rows = table.find_elements(By.TAG_NAME, "tr")
            category = categories[idx]

            for row in rows[1:]:  # Skip header row
                cols = row.find_elements(By.TAG_NAME, "td")
                if len(cols) < 2:
                    continue
                metric = cols[0].text.strip()
                avg_growth = cols[1].text.strip() if len(cols) > 1 else None
                years_data = [col.text.strip() for col in cols[2:]]
                data.append([company_name, category, metric, avg_growth] + years_data)

    return data

# Streamlit App
def main():
    st.title("ShareData Financial Results Scraper")
    st.write("Extract financial data for multiple companies from ShareData.")

    # Input login credentials
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Start Extraction"):
        if not username or not password:
            st.error("Please enter your login credentials.")
            return

        st.info("Initializing scraper...")
        driver = init_driver()

        # Log in
        if login(driver, username, password):
            st.success("Login successful. Extracting data...")
            data = extract_data(driver)

            # Close the driver
            driver.quit()

            if data:
                # Create DataFrame
                columns = ["Company Name", "Category", "Metric", "Avg. Growth", "Year 1", "Year 2", "Year 3", "Year 4", "Year 5"]
                df = pd.DataFrame(data, columns=columns)

                # Display data
                st.write("Extracted Data")
                st.dataframe(df)

                # Provide download button
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name="financial_results.csv",
                    mime="text/csv"
                )
            else:
                st.error("No data was extracted. Please try again.")
        else:
            st.error("Login failed. Check your credentials.")

if __name__ == "__main__":
    main()
