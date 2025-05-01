import streamlit as st
import requests
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PIL import Image
import os

# Streamlit page configuration
st.set_page_config(page_title="Daily Field Report Tool", layout="wide")

# Initialize session state for storing logs
if 'logs' not in st.session_state:
    st.session_state.logs = []

# Function to fetch weather data from OpenWeatherMap API
def get_weather(city, api_key):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        response = requests.get(url)
        data = response.json()
        if response.status_code == 200:
            return {
                "temperature": data["main"]["temp"],
                "description": data["weather"][0]["description"],
                "humidity": data["main"]["humidity"]
            }
        else:
            return None
    except:
        return None

# Function to generate PDF report
def generate_pdf_report(logs, filename="daily_field_report.pdf"):
    c = canvas.Canvas(filename, pagesize=letter)
    c.setFont("Helvetica", 12)
    y = 750
    c.drawString(100, y, "Daily Field Report")
    y -= 30
    for log in logs:
        c.drawString(100, y, f"Date: {log['date']}")
        y -= 20
        c.drawString(100, y, f"Location: {log['location']}")
        y -= 20
        c.drawString(100, y, f"Weather: {log['weather']}")
        y -= 20
        c.drawString(100, y, f"Activities: {log['activities']}")
        y -= 20
        c.drawString(100, y, f"Delays/Incidents: {log['delays']}")
        y -= 20
        if log['media']:
            c.drawString(100, y, "Media: Attached")
        y -= 30
        if y < 50:
            c.showPage()
            y = 750
    c.save()
    return filename

# Main app
st.title("Daily Field Report Tool")

# Sidebar for API key and location
st.sidebar.header("Settings")
api_key = st.sidebar.text_input("OpenWeatherMap API Key", type="password")
default_location = st.sidebar.text_input("Default Location (City)", value="New York")

# Daily Log Form
st.header("Daily Log Entry")
with st.form(key="daily_log_form"):
    date = st.date_input("Date", value=datetime.today())
    location = st.text_input("Location", value=default_location)
    activities = st.text_area("Activities")
    delays = st.text_area("Delays or Incidents")
    media = st.file_uploader("Upload Photo/Video", accept_multiple_files=False, type=["jpg", "png", "mp4"])
    submit_button = st.form_submit_button("Submit Log")

    if submit_button:
        if not activities or not location:
            st.error("Please fill in all required fields.")
        else:
            # Fetch weather data
            weather_info = get_weather(location, api_key) if api_key else None
            weather_str = "Weather data not available"
            if weather_info:
                weather_str = f"Temperature: {weather_info['temperature']}°C, {weather_info['description']}, Humidity: {weather_info['humidity']}%"

            # Save media file if uploaded
            media_path = None
            if media:
                media_path = f"media/{media.name}"
                os.makedirs("media", exist_ok=True)
                with open(media_path, "wb") as f:
                    f.write(media.read())

            # Store log in session state
            log_entry = {
                "date": date.strftime("%Y-%m-%d"),
                "location": location,
                "weather": weather_str,
                "activities": activities,
                "delays": delays,
                "media": media_path
            }
            st.session_state.logs.append(log_entry)
            st.success("Log submitted successfully!")

# Display Logs
st.header("Logged Entries")
if st.session_state.logs:
    for i, log in enumerate(st.session_state.logs):
        st.subheader(f"Log {i+1} - {log['date']}")
        st.write(f"**Location**: {log['location']}")
        st.write(f"**Weather**: {log['weather']}")
        st.write(f"**Activities**: {log['activities']}")
        st.write(f"**Delays/Incidents**: {log['delays']}")
        if log['media']:
            if log['media'].endswith((".jpg", ".png")):
                st.image(log['media'], caption="Attached Photo")
            elif log['media'].endswith(".mp4"):
                st.video(log['media'])
        st.markdown("---")
else:
    st.info("No logs submitted yet.")

# Generate and Download Report
st.header("Generate Summary Report")
if st.button("Generate PDF Report"):
    if st.session_state.logs:
        pdf_file = generate_pdf_report(st.session_state.logs)
        with open(pdf_file, "rb") as f:
            st.download_button(
                label="Download PDF Report",
                data=f,
                file_name=pdf_file,
                mime="application/pdf"
            )
    else:
        st.error("No logs available to generate a report.")

# Notes
st.markdown("""
### Notes
- Ensure you have a valid OpenWeatherMap API key for weather updates.
- Media files are saved in the `media/` directory.
- The app is mobile-friendly due to Streamlit's responsive design.
- Reports are generated as PDFs for stakeholder sharing.
""")
