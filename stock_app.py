# stock_app.py

stock_app,py --- import streamlit as st
import hashlib
import sqlite3
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

# Function to securely hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Database setup
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            email TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Function to register user in database
def register_user(username, email, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', 
                       (username, email, hash_password(password)))
        conn.commit()
    except sqlite3.IntegrityError:
        return False  # Username already exists
    finally:
        conn.close()
    return True

# Function to validate login credentials
def validate_user(username, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT password FROM users WHERE username = ?', (username,))
    result = cursor.fetchone()
    conn.close()
    if result and result[0] == hash_password(password):
        return True
    return False

# Function to fetch user details
def get_user_details(username):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT username, email FROM users WHERE username = ?', (username,))
    result = cursor.fetchone()
    conn.close()
    return result

# Initialize the database
init_db()

# Function to handle user registration
def register():
    st.subheader("Register")
    username = st.text_input("Username", key="register_username")
    email = st.text_input("Email", key="register_email")
    password = st.text_input("Password", type="password", key="register_password")
    confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")

    if st.button("Register"):
        if not username or not email or not password:
            st.warning("Please fill in all the fields.")
        elif password != confirm_password:
            st.warning("Passwords do not match!")
        else:
            success = register_user(username, email, password)
            if success:
                st.success("Registration successful! You can now log in.")
            else:
                st.warning("Username already exists!")

# Function to handle user login
def login():
    st.subheader("Login")
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login"):
        if validate_user(username, password):
            st.session_state['logged_in'] = True
            st.session_state['username'] = username
            st.success(f"Welcome, {username}!")
        else:
            st.error("Invalid username or password.")

# Function to handle user logout
def logout():
    st.session_state['logged_in'] = False
    st.session_state['username'] = None
    st.info("You have logged out.")

# Function to fetch and display market data from Alpha Vantage
def fetch_market_data():
    st.subheader("Market Data")

    api_key = "XQJC5CUWQ7VD8575"  # Replace with your Alpha Vantage API key
    base_url = "https://www.alphavantage.co/query"

    symbol = st.text_input("Enter stock symbol (e.g., AAPL)", value="AAPL")
    start_date = st.date_input("Start Date", value=pd.to_datetime("2023-01-01"))
    end_date = st.date_input("End Date", value=pd.to_datetime("2023-12-31"))
    
    if st.button("Fetch Data"):
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "outputsize": "full",
            "apikey": api_key
        }
        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()

            data = response.json()
            if "Error Message" in data:
                st.error("Error with API key or symbol. Please check your inputs.")
                return

            time_series = data.get("Time Series (Daily)", {})
            if not time_series:
                st.error("Failed to fetch data. Check your API key or symbol.")
                return

            df = pd.DataFrame.from_dict(time_series, orient="index")
            df = df.rename(columns={
                "1. open": "Open",
                "2. high": "High",
                "3. low": "Low",
                "4. close": "Close",
                "5. volume": "Volume"
            })
            df.index = pd.to_datetime(df.index)
            df = df.sort_index()
            df = df.loc[start_date:end_date]

            st.write("### Filtered Stock Prices")
            st.dataframe(df)

            # Visualization Options
            st.write("## Visualizations")
            chart_type = st.selectbox("Select Chart Type", ["Line Plot", "Bar Chart", "Scatter Plot", "Histogram", "Box Plot", "Pie Chart"])
            
            if chart_type == "Line Plot":
                st.line_chart(df["Close"])
            elif chart_type == "Bar Chart":
                st.bar_chart(df["Close"])
            elif chart_type == "Scatter Plot":
                fig, ax = plt.subplots()
                ax.scatter(df.index, df["Close"])
                st.pyplot(fig)
            elif chart_type == "Histogram":
                fig, ax = plt.subplots()
                ax.hist(df["Close"], bins=30)
                st.pyplot(fig)
            elif chart_type == "Box Plot":
                fig, ax = plt.subplots()
                ax.boxplot(df["Close"])
                st.pyplot(fig)
            elif chart_type == "Pie Chart":
                st.warning("Pie charts are not suitable for stock data.")

            # Predict Future Stock Prices
            st.write("## Predict Future Trends")
            df["Close"] = pd.to_numeric(df["Close"])
            df["Days"] = (df.index - df.index.min()).days
            X = df[["Days"]]
            y = df["Close"]

            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            model = LinearRegression()
            model.fit(X_train, y_train)

            future_days = st.slider("Number of days to predict", 1, 365, 30)
            future_dates = pd.DataFrame({"Days": [df["Days"].max() + i for i in range(1, future_days + 1)]})
            future_predictions = model.predict(future_dates)

            st.line_chart(pd.Series(future_predictions, index=future_dates["Days"]))

        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching data: {e}")

# Main function to handle the app's logic
def main():
    st.title("Market Trends Analysis Interface")

    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    if 'username' not in st.session_state:
        st.session_state['username'] = None

    if not st.session_state['logged_in']:
        st.sidebar.title("Menu")
        option = st.sidebar.radio("Choose an option:", ("Register", "Login"))
        if option == "Register":
            register()
        elif option == "Login":
            login()
    else:
        st.success(f"Logged in as {st.session_state['username']}")
        fetch_market_data()
        if st.button("Logout"):
            logout()

if __name__ == "__main__":
    main()

#  List of the command give on VS Code on Terminal for run the code 
1) python -m venv venv
.\venv\Scripts\activate
2) pip install streamlit requests pandas matplotlib scikit-learn
3) streamlit run stock_app.py 
