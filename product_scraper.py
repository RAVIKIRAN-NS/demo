import streamlit as st
import requests
from bs4 import BeautifulSoup
import random
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import matplotlib.pyplot as plt
import plotly.graph_objects as go

# Set page config
st.set_page_config(
    page_title="PriceCheck",
    page_icon="🛒",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Check if this is the first run of the app
if "app_started" not in st.session_state:
    st.session_state.app_started = False
    st.session_state.current_page = "splash"
    st.session_state.price_history = []
    st.session_state.product_name = ""
else:
    if st.session_state.current_page == "splash" and st.session_state.app_started:
        st.session_state.current_page = "main"

# Custom Styling optimized for mobile
st.markdown("""
    <style>
        /* Global styles */
        body {
            font-family: 'Roboto', sans-serif;
            background-color: #121212;
            color: white;
            padding: 0;
            margin: 0;
            -webkit-tap-highlight-color: transparent;
            touch-action: manipulation;
        }
        
        /* Fix for mobile viewport */
        .main .block-container {
            padding-top: 1rem;
            padding-left: 1rem;
            padding-right: 1rem;
            max-width: 100% !important;
        }
        
        /* App content area */
        .app-content {
            padding: 10px;
            min-height: calc(100vh - 80px);
            background-color: #121212;
        }
        
        /* App header */
        .app-header {
            text-align: center;
            margin-bottom: 15px;
            position: sticky;
            top: 0;
            background-color: #121212;
            z-index: 100;
            padding: 5px 0;
        }
        
        .app-title {
            font-size: 24px;
            font-weight: bold;
            color: #4285F4;
            margin: 5px 0;
        }
        
        /* Custom form elements */
        .input-field {
            background-color: #2d2d2d;
            border: none;
            border-radius: 24px;
            padding: 12px 16px;
            color: white;
            width: 100%;
            margin-bottom: 15px;
            box-sizing: border-box;
            font-size: 16px; /* Better for mobile input */
            -webkit-appearance: none;
        }
        
        .app-button {
            background: linear-gradient(135deg, #4285F4, #34A853);
            color: white;
            border: none;
            border-radius: 24px;
            padding: 12px 0;
            width: 100%;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 1px;
            cursor: pointer;
            transition: transform 0.2s;
            min-height: 44px; /* Touch target size */
            font-size: 16px;
        }
        
        /* Larger touch targets for mobile */
        button, [type="button"], [type="submit"] {
            min-height: 44px;
            min-width: 44px;
        }
        
        /* Splash screen */
        .splash-screen {
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 100vh;
            animation: fadeIn 1.5s;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        .app-logo {
            font-size: 72px;
            margin-bottom: 20px;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.1); }
            100% { transform: scale(1); }
        }
        
        /* Results card */
        .results-card {
            background-color: #2d2d2d;
            border-radius: 16px;
            padding: 15px;
            margin-top: 15px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        
        .price-display {
            font-size: 28px;
            font-weight: bold;
            color: #34A853;
            text-align: center;
            padding: 10px 0;
        }
        
        .review-item {
            border-bottom: 1px solid #444;
            padding: 12px 0;
        }
        
        /* Bottom navigation bar */
        .nav-bar {
            height: 60px;
            background-color: #1f1f1f;
            display: flex;
            justify-content: space-around;
            align-items: center;
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            z-index: 1000;
            box-shadow: 0 -2px 10px rgba(0,0,0,0.3);
        }
        
        .nav-button {
            width: 20%;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            color: #888;
            font-size: 20px;
            transition: color 0.3s;
            cursor: pointer;
        }
        
        .nav-button.active {
            color: #4285F4;
        }
        
        .nav-label {
            font-size: 12px;
            margin-top: 4px;
        }
        
        /* Hide Streamlit branding */
        #MainMenu, footer, header {
            visibility: hidden;
        }
        
        /* Progress bar */
        .stProgress {
            height: 8px !important;
            border-radius: 4px !important;
        }
        
        .stProgress > div > div > div {
            background-color: #4285F4 !important;
        }
        
        /* Price history chart */
        .price-history {
            background-color: #2d2d2d;
            border-radius: 16px;
            padding: 15px;
            margin-top: 15px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        
        /* Add padding at bottom for fixed navbar */
        .page-content {
            padding-bottom: 70px;
        }
        
        /* Tabs styling */
        .st-emotion-cache-h5rgaw {
            margin-bottom: 1rem;
        }
        
        /* Input and button container */
        .input-container {
            display: flex;
            gap: 10px;
            margin-top: 10px;
        }
        
        .input-container .stTextInput {
            flex-grow: 1;
        }
        
        /* Loading animation */
        @keyframes loading {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 2px solid rgba(255,255,255,0.2);
            border-radius: 50%;
            border-top-color: white;
            animation: loading 1s linear infinite;
            margin-right: 10px;
        }
        
        /* PWA meta for browser install */
        .web-app-capable {
            -webkit-overflow-scrolling: touch;
        }
    </style>
    
    <!-- Add viewport meta tag for mobile -->
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    
    <!-- PWA meta tags -->
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <link rel="apple-touch-icon" href="https://emojipedia-us.s3.amazonaws.com/source/skype/289/shopping-cart_1f6d2.png">
    <meta name="theme-color" content="#121212">
""", unsafe_allow_html=True)

# Headers to avoid detection
HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Cache-Control": "max-age=0"
}

# Function to add random delays to avoid detection
def random_delay():
    time.sleep(random.uniform(0.5, 1.5))  # Shorter delay for mobile experience

# Function to scrape Amazon and extract product name
# Enhanced price extraction function
def scrape_amazon(url):
    session = requests.Session()
    random_delay()
    response = session.get(url, headers=HEADERS)
    
    if response.status_code != 200:
        return selenium_scrape_amazon(url)
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Extract product name
    product_name = soup.find("span", id="productTitle")
    if not product_name:
        product_name = soup.find("h1", class_="product-title")
    product_name = product_name.text.strip() if product_name else "Unknown Product"
    
    # Enhanced price extraction - try multiple selectors
    price_value = 0
    price_text = "Price not found"
    
    # Try multiple potential price selectors
    price_selectors = [
        "span.a-price-whole",
        "span.a-offscreen",
        "span#priceblock_ourprice",
        "span#priceblock_dealprice",
        "span.priceToPay span.a-offscreen",
        "span.a-color-price",
        "span[data-a-color='price'] span.a-offscreen"
    ]
    
    for selector in price_selectors:
        price_element = soup.select_one(selector)
        if price_element:
            price_text = price_element.text.strip()
            # Try to extract the numeric value
            try:
                price_value = float(''.join(filter(lambda x: x.isdigit() or x == '.', price_text)))
                break  # Found a valid price, exit the loop
            except:
                continue
    
    # Extract reviews - keeping your original code
    reviews = [r.text.strip() for r in soup.select("span[data-hook='review-body']")[:5]]
    ratings = []
    rating_elements = soup.select("i[data-hook='review-star-rating']")
    for rate in rating_elements[:5]:
        try:
            rating_text = rate.text.strip()
            rating_value = float(rating_text.split()[0])
            ratings.append(rating_value)
        except:
            ratings.append(0)
    
    # Match ratings with reviews or fill with zeros
    while len(ratings) < len(reviews):
        ratings.append(0)
    
    return {
        "product_name": product_name,
        "price": price_text,
        "price_value": price_value,
        "reviews": reviews,
        "ratings": ratings
    }

# Selenium fallback for Amazon
def selenium_scrape_amazon(url):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1")
    # Add these additional options to help avoid detection
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    
    driver = webdriver.Chrome(service=Service("chromedriver"), options=options)
    
    # Execute JS to help avoid detection
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    driver.get(url)
    time.sleep(3)  # Allow JavaScript to load
    
    product_name = "Unknown Product"
    price = "Price not found"
    price_value = 0
    reviews = []
    ratings = []
    
    try:
        product_name = driver.find_element(By.ID, "productTitle").text.strip()
    except:
        try:
            product_name = driver.find_element(By.CSS_SELECTOR, "h1.product-title").text.strip()
        except:
            pass
    
    # Try multiple price selectors with Selenium too
    price_selectors = [
        "span.a-price-whole",
        "span.a-offscreen",
        "#priceblock_ourprice",
        "#priceblock_dealprice",
        "span.priceToPay span.a-offscreen",
        "span.a-color-price",
        "span[data-a-color='price'] span.a-offscreen"
    ]
    
    for selector in price_selectors:
        try:
            price_element = driver.find_element(By.CSS_SELECTOR, selector)
            price = price_element.text.strip()
            try:
                price_value = float(''.join(filter(lambda x: x.isdigit() or x == '.', price)))
                break
            except:
                continue
        except:
            continue
    
    # Try to get reviews
    try:
        review_elements = driver.find_elements(By.CSS_SELECTOR, "span[data-hook='review-body']")
        reviews = [r.text.strip() for r in review_elements[:5]]
        
        rating_elements = driver.find_elements(By.CSS_SELECTOR, "i[data-hook='review-star-rating']")
        for rate in rating_elements[:5]:
            try:
                rating_text = rate.text.strip()
                rating_value = float(rating_text.split()[0])
                ratings.append(rating_value)
            except:
                ratings.append(0)
    except:
        pass
    
    driver.quit()
    return {
        "product_name": product_name,
        "price": price,
        "price_value": price_value,
        "reviews": reviews,
        "ratings": ratings
    }

# Mock price tracking function - would be replaced with actual database in real app
def track_price(product_name, price_value):
    current_time = time.strftime("%d %b %H:%M")
    
    if not hasattr(st.session_state, 'price_history'):
        st.session_state.price_history = []
    
    st.session_state.price_history.append({"time": current_time, "price": price_value})
    
    # Keep only last 30 days of data
    if len(st.session_state.price_history) > 30:
        st.session_state.price_history = st.session_state.price_history[-30:]

# Function to switch pages
def switch_page(page):
    st.session_state.current_page = page
    st.rerun()

# Splash Screen
if st.session_state.current_page == "splash":
    st.markdown("""
        <div class="splash-screen">
            <div class="app-logo">🛒</div>
            <div class="app-title">PriceCheck</div>
            <div style="color: #888; margin-top: 10px;">Your ultimate shopping companion</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Auto transition to main screen after 2 seconds
    time.sleep(1.5)
    st.session_state.app_started = True
    st.rerun()

# Main App content
elif st.session_state.current_page == "main":
    st.markdown('<div class="page-content">', unsafe_allow_html=True)
    
    st.markdown("""
        <div class="app-header">
            <div class="app-title">PriceCheck</div>
            <div style="color: #888; font-size: 14px;">Find the best deals instantly</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Tabs for different functions
    tab1, tab2 = st.tabs(["🔍 Search", "📑 Recent"])
    
    with tab1:
        # URL Input with cleaner layout
        col1, col2 = st.columns([4, 1])
        
        with col1:
            product_url = st.text_input("", placeholder="🔗 Paste Amazon URL here", label_visibility="collapsed")
        
        with col2:
            search_button = st.button("Check", key="search_button")
        
        if search_button and product_url:
            progress_placeholder = st.empty()
            with progress_placeholder.container():
                progress_bar = st.progress(0)
                
            status_placeholder = st.empty()
            status_placeholder.markdown("""
                <div style="text-align: center; margin: 10px 0; color: #888;">
                    <span class="loading"></span>Searching for product...
                </div>
            """, unsafe_allow_html=True)
            
            for i in range(100):
                time.sleep(0.01)  # Faster for mobile
                progress_bar.progress(i + 1)
            
            product_data = scrape_amazon(product_url)
            st.session_state.product_data = product_data
            st.session_state.product_name = product_data["product_name"]
            
            # Track price for history
            if product_data["price_value"] > 0:
                track_price(product_data["product_name"], product_data["price_value"])
            
            # Clear progress indicators
            progress_placeholder.empty()
            status_placeholder.empty()
            
            st.rerun()
        elif search_button:
            st.markdown("""
                <div style="background-color: #FF5252; color: white; padding: 10px; border-radius: 8px; margin: 10px 0; text-align: center;">
                    Please enter a product URL
                </div>
            """, unsafe_allow_html=True)
        
        # Display Results
        if "product_data" in st.session_state:
            product_data = st.session_state.product_data
            
            # Product name display
            st.markdown(f"""
                <div style="margin-top: 15px; word-wrap: break-word;">
                    <h3 style="margin: 0; font-size: 16px; color: #eee;">{st.session_state.product_name[:60]}...</h3>
                </div>
            """, unsafe_allow_html=True)
            
            # Price display card
            st.markdown(f"""
                <div class="results-card">
                    <h3 style="margin-top: 0; color: #4285F4; font-size: 16px;">Current Price</h3>
                    <div class="price-display">₹ {product_data["price"]}</div>
                    <div style="text-align: center; color: #888; font-size: 12px;">Last updated: {time.strftime("%d %b %Y, %H:%M")}</div>
                </div>
            """, unsafe_allow_html=True)
            
            # Price history using Plotly for better mobile experience
            if st.session_state.price_history:
                st.markdown("""
                    <div style="margin-top: 20px;">
                        <h3 style="margin: 0 0 10px 0; font-size: 16px; color: #4285F4;">Price History</h3>
                    </div>
                """, unsafe_allow_html=True)
                
                # Create price history chart
                times = [item["time"] for item in st.session_state.price_history]
                prices = [item["price"] for item in st.session_state.price_history]
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=times,
                    y=prices,
                    mode='lines+markers',
                    line=dict(color='#4285F4', width=2),
                    marker=dict(color='#34A853', size=8)
                ))
                
                fig.update_layout(
                    margin=dict(l=10, r=10, t=10, b=10),
                    paper_bgcolor='#2d2d2d',
                    plot_bgcolor='#2d2d2d',
                    font=dict(color='white'),
                    xaxis=dict(
                        showgrid=False,
                        showticklabels=True,
                        tickangle=45,
                        tickfont=dict(size=10)
                    ),
                    yaxis=dict(
                        showgrid=True,
                        gridcolor='rgba(255,255,255,0.1)',
                        tickprefix='₹'
                    ),
                    height=250,
                )
                
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            
            # Reviews Expandable Section
            if st.button("📝 Show Reviews", key="reviews_button"):
                st.markdown("""
                    <div class="results-card" style="margin-top: 15px;">
                        <h3 style="margin-top: 0; color: #4285F4; font-size: 16px;">Customer Reviews</h3>
                """, unsafe_allow_html=True)
                
                if product_data["reviews"]:
                    for i, review in enumerate(product_data["reviews"], start=1):
                        # Get rating if available
                        rating = product_data["ratings"][i-1] if i <= len(product_data["ratings"]) else 0
                        rating_stars = "⭐" * int(rating) + ("★" if rating % 1 >= 0.5 else "")
                        
                        st.markdown(f"""
                            <div class="review-item">
                                <div style="color: #888; margin-bottom: 5px; font-size: 12px;">
                                    {rating_stars} {rating}/5
                                </div>
                                <div style="font-size: 14px;">{review[:150]}{"..." if len(review) > 150 else ""}</div>
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                        <div style="text-align: center; padding: 15px 0; color: #888;">
                            No reviews available
                        </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
            
            # Price alert form
            st.markdown("""
                <div style="margin-top: 20px;">
                    <h3 style="margin: 0 0 10px 0; font-size: 16px; color: #4285F4;">Set Price Alert</h3>
                </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns([3, 1])
            with col1:
                alert_price = st.number_input("", min_value=1, value=int(product_data["price_value"]*0.9) if product_data["price_value"] > 0 else 100, step=1, label_visibility="collapsed")
            
            with col2:
                if st.button("Set Alert"):
                    st.markdown("""
                        <div style="background-color: #34A853; color: white; padding: 10px; border-radius: 8px; margin: 10px 0; text-align: center;">
                            Alert set successfully!
                        </div>
                    """, unsafe_allow_html=True)
    
    with tab2:
        if hasattr(st.session_state, 'price_history') and st.session_state.price_history:
            st.markdown("""
                <div style="margin: 10px 0;">
                    <h3 style="margin: 0; font-size: 16px; color: #4285F4;">Recently Tracked</h3>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
                <div class="results-card">
                    <div style="font-weight: bold; color: #eee;">{st.session_state.product_name[:40]}...</div>
                    <div class="price-display" style="font-size: 22px;">₹ {st.session_state.product_data["price"]}</div>
                    <div style="display: flex; justify-content: space-between; margin-top: 5px;">
                        <span style="color: #888; font-size: 12px;">Last checked: {time.strftime("%d %b, %H:%M")}</span>
                        <span style="color: #34A853; font-size: 12px;">Alert: ₹ {int(st.session_state.product_data["price_value"]*0.9)}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <div style="text-align: center; padding: 30px 0; color: #888;">
                    <div style="font-size: 30px; margin-bottom: 10px;">📊</div>
                    <div>No recent searches</div>
                    <div style="font-size: 12px; margin-top: 5px;">Track products to see your history</div>
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)  # Close page-content div

# Settings page
elif st.session_state.current_page == "settings":
    st.markdown('<div class="page-content">', unsafe_allow_html=True)
    
    st.markdown("""
        <div class="app-header">
            <div class="app-title">Settings</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Settings options
    st.markdown("""
        <div class="results-card">
            <h3 style="margin-top: 0; color: #4285F4; font-size: 16px;">App Preferences</h3>
            
            <div style="display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #444;">
                <span>Notifications</span>
                <span style="color: #4285F4;">On</span>
            </div>
            
            <div style="display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #444;">
                <span>Dark Mode</span>
                <span style="color: #4285F4;">On</span>
            </div>
            
            <div style="display: flex; justify-content: space-between; padding: 12px 0;">
                <span>Currency</span>
                <span style="color: #4285F4;">INR (₹)</span>
            </div>
        </div>
        
        <div class="results-card">
            <h3 style="margin-top: 0; color: #4285F4; font-size: 16px;">About</h3>
            <div style="padding: 5px 0; font-size: 14px;">
                <div>PriceCheck v1.0.0</div>
                <div style="color: #888; margin-top: 5px;">Your ultimate shopping companion for tracking prices and finding the best deals online.</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Favorites page
elif st.session_state.current_page == "favorites":
    st.markdown('<div class="page-content">', unsafe_allow_html=True)
    
    st.markdown("""
        <div class="app-header">
            <div class="app-title">Favorites</div>
        </div>
    """, unsafe_allow_html=True)
    
    if "product_data" in st.session_state:
        st.markdown("""
            <div class="results-card">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <div style="max-width: 80%;">
                        <div style="font-weight: bold; color: #eee; font-size: 14px;">{}</div>
                        <div style="color: #34A853; margin-top: 5px; font-size: 18px; font-weight: bold;">₹ {}</div>
                    </div>
                    <div style="font-size: 24px; color: #FF5252;">❤️</div>
                </div>
            </div>
        """.format(
            st.session_state.product_name[:40] + "...", 
            st.session_state.product_data["price"]
        ), unsafe_allow_html=True)
    else:
        st.markdown("""
            <div style="text-align: center; padding: 40px 0; color: #888;">
                <div style="font-size: 40px; margin-bottom: 15px;">❤️</div>
                <div>No favorites yet</div>
                <div style="font-size: 12px; margin-top: 5px;">Add products to favorites to track them</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Analytics page
elif st.session_state.current_page == "analytics":
    st.markdown('<div class="page-content">', unsafe_allow_html=True)
    
    st.markdown("""
        <div class="app-header">
            <div class="app-title">Price Analytics</div>
        </div>
    """, unsafe_allow_html=True)
    
    if "price_history" in st.session_state and st.session_state.price_history:
        # Create price analytics using Plotly
        times = [item["time"] for item in st.session_state.price_history]
        prices = [item["price"] for item in st.session_state.price_history]
        
        # Calculate statistics
        avg_price = sum(prices) / len(prices)
        max_price = max(prices)
        min_price = min(prices)
        price_drop = ((max_price - prices[-1]) / max_price) * 100 if prices else 0
        
        # Display stats cards
        st.markdown("""
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 15px;">
                <div class="results-card" style="margin-top: 5px; padding: 10px;">
                    <div style="font-size: 12px; color: #888;">Average Price</div>
                    <div style="font-size: 18px; font-weight: bold; color: #4285F4;">₹ {:.2f}</div>
                </div>
                <div class="results-card" style="margin-top: 5px; padding: 10px;">
                    <div style="font-size: 12px; color: #888;">Lowest Price</div>
                    <div style="font-size: 18px; font-weight: bold; color: #34A853;">₹ {:.2f}</div>
                </div>
                <div class="results-card" style="margin-top: 5px; padding: 10px;">
                    <div style="font-size: 12px; color: #888;">Highest Price</div>
                    <div style="font-size: 18px; font-weight: bold; color: #EA4335;">₹ {:.2f}</div>
                </div>
                <div class="results-card" style="margin-top: 5px; padding: 10px;">
                    <div style="font-size: 12px; color: #888;">Price Drop</div>
                    <div style="font-size: 18px; font-weight: bold; color: #FBBC05;">-{:.1f}%</div>
                <div class="results-card" style="margin-top: 5px; padding: 10px;">
                    <div style="font-size: 12px; color: #888;">Price Drop</div>
                    <div style="font-size: 18px; font-weight: bold; color: #FBBC05;">-{:.1f}%</div>
                </div>
            </div>
        """.format(avg_price, min_price, max_price, price_drop), unsafe_allow_html=True)
        
        # Main chart
        st.markdown("""
            <div style="margin-top: 10px;">
                <h3 style="margin: 0 0 10px 0; font-size: 16px; color: #4285F4;">Price Trend</h3>
            </div>
        """, unsafe_allow_html=True)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=times,
            y=prices,
            mode='lines+markers',
            line=dict(color='#4285F4', width=2),
            marker=dict(color='#34A853', size=8)
        ))
        
        # Add horizontal line for average price
        fig.add_shape(
            type="line",
            x0=0,
            y0=avg_price,
            x1=len(times)-1,
            y1=avg_price,
            line=dict(color="#FBBC05", width=2, dash="dash"),
        )
        
        fig.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor='#2d2d2d',
            plot_bgcolor='#2d2d2d',
            font=dict(color='white'),
            xaxis=dict(
                showgrid=False,
                showticklabels=True,
                tickangle=45,
                tickfont=dict(size=10)
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='rgba(255,255,255,0.1)',
                tickprefix='₹'
            ),
            height=300,
            annotations=[
                dict(
                    x=len(times)*0.9,
                    y=avg_price,
                    xref="x",
                    yref="y",
                    text="Avg",
                    showarrow=False,
                    font=dict(color="#FBBC05", size=10),
                    bgcolor="#2d2d2d",
                    borderpad=2
                )
            ]
        )
        
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        # Prediction card
        st.markdown("""
            <div class="results-card">
                <h3 style="margin-top: 0; color: #4285F4; font-size: 16px;">Price Prediction</h3>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 10px;">
                    <div>
                        <div style="font-size: 14px;">Expected in 7 days:</div>
                        <div style="font-weight: bold; color: #34A853; font-size: 18px;">₹ {:.2f}</div>
                    </div>
                    <div style="color: #34A853; font-size: 14px;">-{:.1f}%</div>
                </div>
                <div style="font-size: 12px; color: #888; margin-top: 10px; text-align: center;">
                    Best time to buy: Next week
                </div>
            </div>
        """.format(
            min_price * 0.95,  # Fake prediction - would use ML in real app
            5.0  # Example predicted drop
        ), unsafe_allow_html=True)
    else:
        st.markdown("""
            <div style="text-align: center; padding: 40px 0; color: #888;">
                <div style="font-size: 40px; margin-bottom: 15px;">📊</div>
                <div>No price data available</div>
                <div style="font-size: 12px; margin-top: 5px;">Track products to see analytics</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Bottom Navigation Bar - fixed at bottom of screen
st.markdown(f"""
    <div class="nav-bar">
        <div class="nav-button {"active" if st.session_state.current_page == "main" else ""}" onclick="handleNavClick('main')">
            🏠
            <div class="nav-label">Home</div>
        </div>
        <div class="nav-button {"active" if st.session_state.current_page == "analytics" else ""}" onclick="handleNavClick('analytics')">
            📊
            <div class="nav-label">Analytics</div>
        </div>
        <div class="nav-button {"active" if st.session_state.current_page == "favorites" else ""}" onclick="handleNavClick('favorites')">
            ❤️
            <div class="nav-label">Favorites</div>
        </div>
        <div class="nav-button {"active" if st.session_state.current_page == "settings" else ""}" onclick="handleNavClick('settings')">
            ⚙️
            <div class="nav-label">Settings</div>
        </div>
    </div>
    
    <script>
    function handleNavClick(page) {{
        // Use Streamlit's session state to manage page navigation
        const queryParams = new URLSearchParams(window.location.search);
        queryParams.set('nav_to', page);
        window.location.search = queryParams.toString();
    }}
    
    // Check if there's a navigation parameter and process it
    document.addEventListener('DOMContentLoaded', function() {{
        const queryParams = new URLSearchParams(window.location.search);
        const navTo = queryParams.get('nav_to');
        if (navTo) {{
            // Clear the parameter after processing
            queryParams.delete('nav_to');
            const newUrl = window.location.pathname + (queryParams.toString() ? '?' + queryParams.toString() : '');
            window.history.replaceState({{}}, '', newUrl);
            
            // Submit a form to trigger Streamlit rerun
            const form = document.createElement('form');
            form.method = 'POST';
            form.innerHTML = `<input type="hidden" name="nav_to" value="${{navTo}}">`;
            document.body.appendChild(form);
            form.submit();
        }}
    }});
    
    // Make entire app feel more like a native app
    document.addEventListener('DOMContentLoaded', function() {{
        // Prevent pull-to-refresh
        document.body.addEventListener('touchmove', function(e) {{
            if (e.target.classList.contains('web-app-capable')) {{
                e.preventDefault();
            }}
        }}, {{ passive: false }});
        
        // Add iOS home screen app behavior
        if (window.navigator.standalone) {{
            document.body.classList.add('web-app-capable');
        }}
    }});
    </script>
""", unsafe_allow_html=True)

# Handle navigation from JavaScript 
if "nav_to" in st.query_params:
    nav_to = st.query_params["nav_to"][0]
    st.session_state.current_page = nav_to
    # Clean up URL after processing navigation
    st.experimental_set_query_params()
    st.rerun()