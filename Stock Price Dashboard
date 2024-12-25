# Stock Price Dashboard

import streamlit as st
import yfinance as yf
import hashlib
import base64
import pandas as pd
import numpy as np
import datetime
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import plotly.express as px
import plotly.graph_objects as go

# Function to securely hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Initialize session state variables
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = None
if 'user_data' not in st.session_state:
    st.session_state['user_data'] = {}

# Function to handle user registration
def register():
    st.subheader("Register")
    username = st.text_input("Username", key="register_username")
    email = st.text_input("Email", key="register_email")
    password = st.text_input("Password", type="password", key="register_password")
    confirm_password = st.text_input("Confirm Password", type="password", key="registration_confirm_password")

    if st.button("Register"):
        if not username or not email or not password:
            st.warning("Please fill in all the fields.")
        elif username in st.session_state['user_data']:
            st.warning("Username already exists!")
        elif password != confirm_password:
            st.warning("Passwords do not match!")
        else:
            st.session_state['user_data'][username] = {
                "email": email,
                "password": hash_password(password),
                "profile_pic": None  # Initialize profile picture as None
            }
            st.success("Registration successful! You can now log in.")

# Function to handle user login
def login():
    st.subheader("Login")
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login"):
        hashed_password = hash_password(password)
        user_data = st.session_state['user_data']
        if username in user_data and user_data[username]["password"] == hashed_password:
            st.session_state['logged_in'] = True
            st.session_state['username'] = username
            st.success(f"Welcome, {username}")
        else:
            st.error("Invalid username or password")

# Function to handle user logout
def logout():
    st.session_state['logged_in'] = False
    st.session_state['username'] = None
    st.info("You have logged out.")

# Profile section
def profile_section():
    username = st.session_state['username']
    user_data = st.session_state['user_data'][username]

    st.title("My Profile")
    if user_data['profile_pic']:
        st.image(user_data['profile_pic'], width=150)
    else:
        st.info("No profile picture uploaded yet.")

    uploaded_file = st.file_uploader("Upload Profile Picture", type=["jpg", "jpeg", "png"], key="upload_profile_pic")
    if uploaded_file:
        user_data['profile_pic'] = uploaded_file.read()
        st.session_state['user_data'][username] = user_data
        st.success("Profile picture updated!")

    st.subheader("User Details")
    st.write(f"Username: {username}")
    st.write(f"Email: {user_data['email']}")

# Display profile picture at the top
def display_top_profile():
    username = st.session_state['username']
    user_data = st.session_state['user_data'][username]

    if user_data['profile_pic']:
        profile_pic_base64 = base64.b64encode(user_data['profile_pic']).decode('utf-8')
        profile_pic_html = f'<img class="profile-pic" src="data:image/png;base64,{profile_pic_base64}" alt="Profile Picture">'
    else:
        profile_pic_html = '<img class="profile-pic" src="https://via.placeholder.com/80" alt="Default Profile Picture">'
    st.markdown(profile_pic_html, unsafe_allow_html=True)

# Function to fetch real-time stock data till today's date
def fetch_stock_data(ticker, start_date, end_date):
    stock_data = yf.download(ticker, start=start_date, end=end_date)
    stock_data.reset_index(inplace=True)  # Reset index to have Date as a column
    return stock_data

# Forecast prices using Linear Regression
def forecast_prices(df):
    df['Days'] = (df['Date'] - df['Date'].min()).dt.days
    X = df[['Days']]
    y = df['Close']  # Use 'Close' price for forecasting

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = LinearRegression()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    st.write(f"#### Model Mean Squared Error (MSE): {mse:.2f}")

    forecast_days = 30
    future_dates = pd.date_range(start=df['Date'].max() + datetime.timedelta(days=1), periods=forecast_days)
    future_days = (future_dates - df['Date'].min()).days
    future_prices = model.predict(future_days.values.reshape(-1, 1))

    forecast_df = pd.DataFrame({
        "Date": future_dates,
        "Predicted Price": future_prices
    })
    st.write("### 🔮 Forecasted Prices for the Next 30 Days")
    st.dataframe(forecast_df.style.format({"Predicted Price": "${:,.2f}"}))

    fig_forecast = px.line(
        forecast_df, x="Date", y="Predicted Price", title="Forecasted Price Trend",
        color_discrete_sequence=["#27AE60"], markers=True
    )
    st.plotly_chart(fig_forecast)

# Market trends analysis function
def market_trends_analysis():
    st.title("Market Trends Analysis")

    company_categories = {
        "Tech Companies": [
            ("Apple Inc. (AAPL)", "AAPL"),
            ("Microsoft Corporation (MSFT)", "MSFT"),
            ("Alphabet Inc. (GOOGL)", "GOOGL"),
            ("Amazon.com Inc. (AMZN)", "AMZN"),
            ("Meta Platforms Inc. (META)", "META")
        ],
        "Automobile": [
            ("Tesla Inc. (TSLA)", "TSLA"),
            ("Ford Motor Company (F)", "F"),
            ("General Motors (GM)", "GM")
        ],
        "Consumer Goods": [
            ("The Coca-Cola Company (KO)", "KO"),
            ("PepsiCo Inc. (PEP)", "PEP"),
            ("Procter & Gamble Co. (PG)", "PG")
        ],
        "Financials": [
            ("JPMorgan Chase & Co. (JPM)", "JPM"),
            ("Bank of America Corporation (BAC)", "BAC"),
            ("Wells Fargo & Company (WFC)", "WFC")
        ],
        "Pharmaceuticals": [
            ("Pfizer Inc. (PFE)", "PFE"),
            ("Moderna Inc. (MRNA)", "MRNA"),
            ("Johnson & Johnson (JNJ)", "JNJ")
        ],
        "Retail": [
            ("Walmart Inc. (WMT)", "WMT"),
            ("Costco Wholesale Corporation (COST)", "COST"),
            ("The Home Depot, Inc. (HD)", "HD")
        ],
        "Energy": [
            ("Exxon Mobil Corporation (XOM)", "XOM"),
            ("Chevron Corporation (CVX)", "CVX"),
            ("BP plc (BP)", "BP")
        ],
        "Airlines": [
            ("Delta Air Lines, Inc. (DAL)", "DAL"),
            ("American Airlines Group Inc. (AAL)", "AAL")
        ]
    }

    selected_category = st.selectbox("Select a Category", list(company_categories.keys()))
    selected_company, selected_code = st.selectbox("Select a Company", company_categories[selected_category])

    # Simulated stock data generation for selected company
    date_range = pd.date_range(start="2023-01-01", end="2024-12-31")
    stock_data = pd.DataFrame({
        "Date": date_range,
        "Open": np.random.uniform(100, 500, len(date_range)),
        "High": np.random.uniform(100, 500, len(date_range)),
        "Low": np.random.uniform(100, 500, len(date_range)),
        "Close": np.random.uniform(100, 500, len(date_range)),
        "Volume": np.random.randint(1000, 10000, len(date_range)),
        "Company": [selected_company] * len(date_range),
    })

    st.write(f"### Stock Data for {selected_company}")
    st.dataframe(stock_data.style.highlight_max(subset="Close", axis=0))

    # Visualizing data

    # 1. Area Chart (Stock Price)
    st.markdown("### 📊 Area Chart - Stock Price")
    fig_area = px.area(stock_data, x="Date", y="Close", title=f"{selected_company} Stock Price Area Chart")
    st.plotly_chart(fig_area)

    # 2. Line Chart (Stock Volume)
    st.markdown("### 📊 Line Chart - Stock Volume")
    fig_line = px.line(stock_data, x="Date", y="Volume", title=f"{selected_company} Stock Volume Trend")
    st.plotly_chart(fig_line)

    # 3. Doughnut Chart (Volume Distribution)
    st.markdown("### 📊 Doughnut Chart - Volume Distribution")
    fig_doughnut = go.Figure(data=[go.Pie(
        labels=["High Volume", "Low Volume"],
        values=[stock_data["Volume"].sum() * 0.7, stock_data["Volume"].sum() * 0.3],
        hole=0.4
    )])
    st.plotly_chart(fig_doughnut)

    # 4. Gauge Chart (Stock Price Performance)
    st.markdown("### 📊 Gauge Chart - Stock Price Performance")
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number", value=stock_data["Close"].iloc[-1],
        title={"text": f"{selected_company} Price Performance", "font": {"size": 24}},
        gauge={"axis": {"range": [None, 500]}, "bar": {"color": "green"}, "steps": [
            {"range": [0, 100], "color": "lightgreen"},
            {"range": [100, 200], "color": "lightyellow"},
            {"range": [200, 300], "color": "orange"},
            {"range": [300, 500], "color": "red"}
        ]}
    ))
    st.plotly_chart(fig_gauge)

    # 5. Waterfall Chart (Stock Movement)
    st.markdown("### 📊 Waterfall Chart - Stock Movement")
    fig_waterfall = go.Figure(go.Waterfall(
        x=stock_data["Date"].iloc[:5],
        y=stock_data["Close"].iloc[:5],
        measure=["relative", "relative", "relative", "relative", "total"]
    ))
    st.plotly_chart(fig_waterfall)

    # KPI Metrics (Example: Opening and Closing Prices)
    st.markdown("### 📊 Key Performance Indicators")
    kpi_values = {
        "Opening Price": f"${stock_data['Open'].iloc[0]:.2f}",
        "Closing Price": f"${stock_data['Close'].iloc[-1]:.2f}",
        "Total Volume": f"{stock_data['Volume'].sum():,}",
    }
    for k, v in kpi_values.items():
        st.metric(label=k, value=v)

# Running main app structure
def main():
    st.title("Stock Price Dashboard")
    st.sidebar.header("Navigation")
    menu = ["Home", "Register", "Login", "Profile", "Stock Trends Analysis"]
    choice = st.sidebar.selectbox("Select an option", menu)

    if choice == "Home":
        st.write("### Welcome to the Stock Price Dashboard!")

    elif choice == "Register":
        register()

    elif choice == "Login":
        login()

    elif choice == "Profile":
        if st.session_state['logged_in']:
            profile_section()
        else:
            st.warning("Please log in to view your profile.")

    elif choice == "Stock Trends Analysis":
        if st.session_state['logged_in']:
            market_trends_analysis()
        else:
            st.warning("Please log in to access stock trends analysis.")

if __name__ == "__main__":
    main()
