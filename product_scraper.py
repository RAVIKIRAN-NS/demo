import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd
import plotly.express as px
import re

# Page Configuration
st.set_page_config(
    page_title="Amazon Product Scraper",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Modern UI
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    .stButton>button {
        background: linear-gradient(135deg, #FF9900, #FF6600);
        color: white;
        border-radius: 12px;
        padding: 12px 28px;
        border: none;
        font-size: 16px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 12px rgba(255, 153, 0, 0.3);
    }
    .stTextInput>div>div>input {
        border-radius: 12px;
        padding: 12px;
        border: 1px solid #ddd;
        transition: all 0.3s ease;
    }
    .stTextInput>div>div>input:focus {
        border-color: #FF9900;
        box-shadow: 0 0 8px rgba(255, 153, 0, 0.2);
    }
    .stDataFrame {
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    .welcome-page {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 80vh;
        text-align: center;
    }
    .welcome-page h1 {
        font-size: 3.5rem;
        font-weight: 700;
        color: #FF9900;
        margin-bottom: 16px;
    }
    .welcome-page p {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 32px;
    }
    .fade-in {
        animation: fadeIn 1s ease-in-out;
    }
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    </style>
    """, unsafe_allow_html=True)

# Welcome Page
def welcome_page():
    st.markdown("""
        <div class="welcome-page">
            <h1>🛒 Amazon Product Scraper</h1>
            <p>Scrape product details from Amazon with ease. Enter the product URL to get started!</p>
        </div>
    """, unsafe_allow_html=True)

# Clean Price Data
def clean_price(price_str):
    if price_str == "N/A":
        return None
    # Remove non-numeric characters (e.g., "Up to", "off", currency symbols)
    price_str = re.sub(r"[^0-9.]", "", price_str)
    try:
        return float(price_str)
    except ValueError:
        return None

# Scrape Product Details
def scrape_amazon_product(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get(url)
    time.sleep(5)

    product_details = {
        'Product': "N/A",
        'Price': "N/A",
        'Rating': "N/A",
        'Reviews': "N/A",
        'Image URL': "N/A"
    }
    
    try:
        product_details['Product'] = driver.find_element(By.ID, 'productTitle').text.strip()
        product_details['Image URL'] = driver.find_element(By.ID, 'landingImage').get_attribute('src')
        product_details['Rating'] = driver.find_element(By.CLASS_NAME, 'a-icon-alt').get_attribute('innerHTML').strip()
        product_details['Reviews'] = driver.find_element(By.ID, 'acrCustomerReviewText').text.strip()
        
        # Improved price extraction logic
        price_selectors = [
            'span.a-price-whole',
            'span.a-offscreen',
            'span.a-price',
            'span.a-color-price',
            'span.a-size-medium.a-color-price'
        ]
        
        for selector in price_selectors:
            try:
                price_element = driver.find_element(By.CSS_SELECTOR, selector)
                product_details['Price'] = price_element.text.strip()
                if product_details['Price']:
                    break
            except:
                continue
        
    except Exception as e:
        st.error(f"An error occurred while scraping: {e}")
    finally:
        driver.quit()
    
    return product_details

# Main App
def main():
    if 'scrape_started' not in st.session_state:
        st.session_state.scrape_started = False
    if 'history' not in st.session_state:
        st.session_state.history = []

    if not st.session_state.scrape_started:
        welcome_page()
        if st.button("Get Started"):
            st.session_state.scrape_started = True
            st.rerun()
    else:
        st.title("🛒 Amazon Product Scraper")
        st.markdown("### Enter the Amazon Product URL to scrape details")
        
        with st.form(key='amazon_scraper_form'):
            url = st.text_input("Amazon Product URL", placeholder="https://www.amazon.com/dp/B08N5WRWNW")
            submit_button = st.form_submit_button(label='Scrape Product Details')
        
        if submit_button and url:
            with st.spinner("Scraping product details... Please wait ⏳"):
                try:
                    product_details = scrape_amazon_product(url)
                    st.session_state.history.append(product_details)  # Add to history
                    st.success("✅ Product details scraped successfully!")
                    st.markdown("### Product Details")
                    
                    if product_details['Image URL'] != "N/A":
                        st.image(product_details['Image URL'], caption=product_details['Product'], width=300)
                    
                    st.markdown(f"**Product:** {product_details['Product']}")
                    st.markdown(f"**Price:** {product_details['Price']}")
                    st.markdown(f"**Rating:** {product_details['Rating']}")
                    st.markdown(f"**Reviews:** {product_details['Reviews']}")
                    st.markdown("---")

                    # Graphical Visualization
                    st.markdown("### Graphical Visualization")
                    if product_details['Rating'] != "N/A":
                        rating = float(product_details['Rating'].split()[0])
                        fig = px.bar(x=["Rating"], y=[rating], labels={'x': '', 'y': 'Rating (out of 5)'}, 
                                     title="Product Rating", text=[f"{rating}/5"], color_discrete_sequence=["#FF9900"])
                        fig.update_traces(textposition='outside')
                        st.plotly_chart(fig, use_container_width=True)
                    
                    st.markdown("---")
                    st.markdown("### Raw Data")
                    st.json(product_details)
                    
                except Exception as e:
                    st.error(f"❌ An error occurred: {e}")

        # Display History
        if st.session_state.history:
            st.markdown("---")
            st.markdown("### Scraping History")
            history_df = pd.DataFrame(st.session_state.history)
            history_df['Price'] = history_df['Price'].apply(clean_price)  # Clean price data
            st.dataframe(history_df)

            # Plot Price Trends (if available)
            if 'Price' in history_df.columns and not history_df['Price'].isnull().all():
                st.markdown("### Price Trends")
                fig = px.line(history_df, x='Product', y='Price', title="Price Trends of Scraped Products",
                              labels={'Product': 'Product', 'Price': 'Price ($)'}, markers=True)
                fig.update_traces(line_color="#FF6600", marker_color="#FF9900")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("⚠️ No valid price data available for visualization.")

if __name__ == "__main__":
    main()
