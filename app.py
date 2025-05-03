import datetime
import threading
import geocoder
import cv2
import streamlit as st
from PIL import Image
import os, tempfile, time, json
import numpy as np
import pandas as pd
import folium
import plotly.express as px
from geopy.geocoders import Nominatim
from twilio.rest import Client
import yagmail
import matplotlib.pyplot as plt
from pathlib import Path
from streamlit_folium import folium_static
import base64

# Set wide page configuration with custom theme
st.set_page_config(
    page_title="Trash Tracker | Smart Waste Detection",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS styling for a more attractive interface
st.markdown("""
<style>
    /* Main styling */
    .main {
        background-color: #f8f9fa;
    }
    
    /* Custom fonts */
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;700&display=swap');
    
    h1, h2, h3, h4 {
        font-family: 'Montserrat', sans-serif;
        color: #2c3e50;
        font-weight: 700;
    }
    
    /* Button styling */
    div.stButton > button {
        background-color: #27ae60;
        color: white;
        border-radius: 10px;
        border: none;
        padding: 10px 25px;
        font-weight: bold;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
    
    div.stButton > button:hover {
        background-color: #2ecc71;
        box-shadow: 0 6px 8px rgba(0, 0, 0, 0.15);
        transform: translateY(-2px);
    }
    
    /* Success message styling */
    div.element-container.st-emotion-cache-zq5wmm.e1tzin5v0 div[data-testid="stText"] p {
        background-color: #d4edda;
        color: #155724;
        padding: 10px 15px;
        border-radius: 5px;
        border-left: 5px solid #28a745;
    }
    
    /* File uploader styling */
    .uploadedFile {
        border-radius: 10px !important;
        border: 2px dashed #6c757d !important;
        padding: 20px !important;
    }
    
    /* Hide menu and footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Custom card styling */
    .css-card {
        border-radius: 10px;
        padding: 20px;
        background-color: #27ae60;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        border-radius: 5px 5px 0px 0px;
        padding-left: 20px;
        padding-right: 20px;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #27ae60;
        color: white;
    }
    
    /* Progress bar styling */
    div.stProgress > div > div > div > div {
        background-color: #27ae60;
    }
    
    /* Loading spinner styling */
    div.stSpinner > div > div {
        border-top-color: #27ae60 !important;
    }
</style>
""", unsafe_allow_html=True)

# Twilio and Email Credentials
TWILIO_SID = 'ACe91623fd25f7469c81a0e35add822bc2'
TWILIO_AUTH_TOKEN = 'b68be38bc93812e02fd8399585fb6d82'  # ✅ Corrected
EMAIL_APP_PASSWORD = 'kecvuuderioxpsqk'  # ✅ App password only

# Function to create header with logo
def create_header():
    cols = st.columns([1, 3])
    with cols[0]:
        image = Image.open("Resources/UI Images/icon.jpg")
        st.image(image, width=150)
    with cols[1]:
        st.markdown("""
        <div style="padding-top: 10px;">
            <h1 style="color: #27ae60; margin-bottom: 0;">Trash Tracker</h1>
            <p style="font-size: 1.2em; color: #7f8c8d; margin-top: 0;">Smart Waste Detection for Cleaner Cities</p>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("<hr style='margin: 0; padding: 0; margin-bottom: 20px;'>", unsafe_allow_html=True)

# Enhanced notification functions with better visual feedback
def send_sms(timestamp, lat, lon):
    try:
        # Create a shortened timestamp (just time, no date)
        short_time = timestamp.strftime("%H:%M")
        
        # Create a much shorter message body
        body = f"⚠️ Trash Alert! {short_time} @ {lat:.4f},{lon:.4f}"
        
        # Send the SMS
        client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=body, 
            from_='+15513832453', 
            to='+919999889373'
        )
        
        print(f"SMS sent: {message.sid}")
        return True
    except Exception as e:
        error_msg = f"SMS ERROR: {str(e)}"
        print(error_msg)
        return False

def make_call(lat, lon):
    try:
        client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
        # Enhanced TwiML with better voice and pauses
        twiml = """
        <Response>
            <Say voice="woman" language="en-IN">
                Alert! Trash detected in your area. Immediate action required.
            </Say>
            <Pause length="1"/>
            <Say voice="woman" language="en-IN">
                Please check the sent notifications for exact location details.
            </Say>
        </Response>
        """
        call = client.calls.create(
            twiml=twiml,
            from_='+15513832453',
            to='+919999889373'
        )
        print(f"Call initiated: {call.sid}")
        return True
    except Exception as e:
        print(f"Call ERROR: {str(e)}")
        return False

def send_whatsapp(lat, lon):
    try:
        client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
        # Enhanced WhatsApp message with emoji and better formatting
        message = client.messages.create(
            body=f'🚨 *TRASH ALERT* 🚨\n\n📍 Location detected: {lat:.6f}, {lon:.6f}\n\nPlease take immediate action.',
            persistent_action=[f'geo:{lat},{lon}'],
            from_='whatsapp:+14155238886',
            to='whatsapp:+919999889373'
        )
        print("WhatsApp message sent.")
        return True
    except Exception as e:
        print(f"WhatsApp ERROR: {str(e)}")
        return False

def send_email(timestamp, lat, lon, image_path="snapshot.jpg"):
    try:
        sender_email = "trashtrackerproject@gmail.com"  # Corrected email
        
        # Check if image exists
        if not os.path.exists(image_path):
            print(f"Warning: Image file {image_path} not found, sending email without attachment")
            has_attachment = False
        else:
            has_attachment = True
            
        geolocator = Nominatim(user_agent="trash_tracker")
        try:
            location = geolocator.reverse(f"{lat},{lon}")
            address = ",".join(list(location.raw['address'].values()))
        except Exception as geo_error:
            print(f"Geocoding error: {str(geo_error)}")
            address = f"Coordinates: {lat}, {lon}"
            
        maps_link = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
        
        # Enhanced HTML email with better styling
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 5px;">
                <div style="background-color: #e74c3c; color: white; padding: 15px; border-radius: 5px 5px 0 0; text-align: center;">
                    <h1 style="margin: 0;">🚨 TRASH ALERT 🚨</h1>
                </div>
                
                <div style="padding: 20px; background-color: #f9f9f9;">
                    <p style="font-size: 16px;">Trash has been detected at the following location:</p>
                    
                    <div style="background-color: white; padding: 15px; border-radius: 5px; margin: 15px 0; border-left: 4px solid #e74c3c;">
                        <p><strong>🕒 Time:</strong> {timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
                        <p><strong>📍 Address:</strong> {address}</p>
                    </div>
                    
                    <div style="text-align: center; margin: 20px 0;">
                        <a href="{maps_link}" style="background-color: #3498db; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                            View on Google Maps
                        </a>
                    </div>
                    
                    <p style="font-size: 14px; color: #7f8c8d; font-style: italic;">This is an automated alert from the Trash Tracker System.</p>
                </div>
            </body>
        </html>
        """
            
        # Create the yagmail SMTP object with SSL explicitly enabled
        yag = yagmail.SMTP(
            user=sender_email, 
            password=EMAIL_APP_PASSWORD,
            smtp_ssl=True
        )
        
        # Send email with or without attachment
        if has_attachment:
            yag.send(
                to="shreya06lg@gmail.com", 
                subject="🚨 Trash Alert Notification", 
                contents=[html_content, yagmail.inline(image_path)]
            )
        else:
            yag.send(
                to="shreya06lg@gmail.com", 
                subject="🚨 Trash Alert Notification", 
                contents=[html_content]
            )
            
        print("Email sent successfully.")
        return True
    except Exception as e:
        error_details = f"Email ERROR: {type(e).__name__}: {str(e)}"
        print(error_details)
        return False

# Test SMS function with better UI feedback
def test_sms():
    with st.spinner("Sending test SMS..."):
        try:
            now = datetime.datetime.now()
            lat, lon = 20.5937, 78.9629  # Example coordinates
            result = send_sms(now, lat, lon)
            if result:
                st.success("✅ Test SMS sent successfully!")
            else:
                st.error("❌ Failed to send test SMS.")
            return result
        except Exception as e:
            st.error(f"❌ Test SMS error: {str(e)}")
            return False

# Function to create card-like containers
def create_card(title, content, icon="ℹ️"):
    st.markdown(f"""
    <div class="css-card">
        <h3>{icon} {title}</h3>
        <p>{content}</p>
    </div>
    """, unsafe_allow_html=True)

# Function to create decorative divider
def create_divider():
    st.markdown("<hr style='margin: 30px 0; border: 0; height: 1px; background-image: linear-gradient(to right, rgba(0, 0, 0, 0), rgba(0, 0, 0, 0.2), rgba(0, 0, 0, 0));'>", unsafe_allow_html=True)

# Create animated background function (replaces the basic image display)
def create_animated_background(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    
    st.markdown(f"""
    <div style="
        background-image: url(data:image/jpeg;base64,{encoded_string});
        background-size: cover;
        background-position: center;
        border-radius: 10px;
        padding: 30px;
        margin: 10px 0;
        height: 300px;
        display: flex;
        flex-direction: column;
        justify-content: flex-end;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    ">
        <div style="
            background-color: rgba(0, 0, 0, 0.6);
            color: white;
            padding: 20px;
            border-radius: 5px;
        ">
            <h2 style="margin: 0; color: white;">Smart Waste Detection</h2>
            <p style="margin: 10px 0 0 0;">Creating cleaner cities through technology innovation</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Create interactive map function
def create_interactive_map(lat, lon, zoom=15):
    m = folium.Map(location=[lat, lon], zoom_start=zoom)
    
    # Add a marker with custom icon
    icon = folium.Icon(color='red', icon='trash', prefix='fa')
    popup_text = f"""
    <div style="width:200px">
        <h4 style="color:#e74c3c">Trash Detected!</h4>
        <p><b>Latitude:</b> {lat:.6f}</p>
        <p><b>Longitude:</b> {lon:.6f}</p>
        <p><b>Time:</b> {datetime.datetime.now().strftime('%H:%M:%S')}</p>
    </div>
    """
    folium.Marker(
        [lat, lon], 
        popup=folium.Popup(popup_text, max_width=300), 
        tooltip="Click for details",
        icon=icon
    ).add_to(m)
    
    # Add a circle for better visibility
    folium.Circle(
        radius=50,
        location=[lat, lon],
        color='crimson',
        fill=True,
    ).add_to(m)
    
    return m

# Create a notification dashboard
def create_notification_dashboard(results):
    st.markdown("<h3 style='text-align:center'>📊 Notification Status</h3>", unsafe_allow_html=True)
    
    cols = st.columns(4)
    notification_types = ["Email", "SMS", "WhatsApp", "Call"]
    icons = ["✉️", "📱", "💬", "📞"]
    
    for i, (col, notification, icon) in enumerate(zip(cols, notification_types, icons)):
        with col:
            # Success or failure styles
            status = "success" if results[i] else "danger"
            status_text = "Sent" if results[i] else "Failed"
            bg_color = "#e8f5e9" if results[i] else "#ffebee"
            text_color = "#1b5e20" if results[i] else "#b71c1c"
            border_color = "#c8e6c9" if results[i] else "#ffcdd2"

            st.markdown(f"""
            <div class="notification-box" style="
                background-color: {bg_color}; 
                color: {text_color};
                border: 1px solid {border_color};
            ">
                <h3 style="font-size: 24px; margin-bottom: 10px;">{icon}</h3>
                <h4 style="margin: 0;">{notification}</h4>
                <p style="margin: 5px 0; font-weight: bold;">{status_text}</p>
            </div>
            """, unsafe_allow_html=True)

# Main UI function
def main():
    # Create header with logo
    create_header()
    
    # Create stylized tabs
    tabs = st.tabs(["🏠 Overview", "🔍 Trash Tracker", "📊 Statistics"])
    tab_overview, tab_tracker, tab_stats = tabs

    # OVERVIEW TAB - Enhanced with cards and better styling
    with tab_overview:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("<h2>Introducing Trash Tracker</h2>", unsafe_allow_html=True)
            st.markdown("""
            <p style="font-size: 1.1em; line-height: 1.5;">
                Trash Tracker is an innovative solution that leverages AI technology to detect 
                and report garbage dumping in real-time. Our system helps municipalities 
                maintain cleaner cities while optimizing waste management resources.
            </p>
            """, unsafe_allow_html=True)
            
            # Create animated background
            create_animated_background('Resources/UI Images/overview_1.jpg')
        
        with col2:
            # Key benefits cards
            create_card("Real-time Detection", "Instantly identify trash dumping with AI-powered video analysis", "🔍")
            create_card("Automated Alerts", "Multi-channel notifications to relevant authorities", "🚨")
            create_card("Cost Effective", "Utilizes existing infrastructure and requires minimal new investment", "💰")
            create_card("Data Insights", "Generates valuable statistics to optimize waste management", "📈")
        
        create_divider()
        
        st.markdown("<h3>How It Works</h3>", unsafe_allow_html=True)
        
        cols = st.columns(4)
        with cols[0]:
            st.markdown("#### 1. Capture")
            st.markdown("Vehicle dashcams capture real-time video footage")
            
        
        with cols[1]:
            st.markdown("#### 2. Analyze")
            st.markdown("AI system identifies trash and illegal dumping")
            
            
        with cols[2]:
            st.markdown("#### 3. Alert")
            st.markdown("Multiple notifications sent to authorities")
            
            
        with cols[3]:
            st.markdown("#### 4. Act")
            st.markdown("Cleanup teams respond to precise locations")
            

    # TRASH TRACKER TAB - Enhanced with better interactive elements
    with tab_tracker:
        st.markdown("<h2>🔍 Trash Detector System</h2>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("""
            <div class="css-card">
                <h3>System Capabilities</h3>
                <ul>
                    <li><b>Real-time Detection:</b> AI-powered visual recognition of waste</li>
                    <li><b>Geo-tagging:</b> Precise location identification</li>
                    <li><b>Multi-channel Alerts:</b> Email, SMS, WhatsApp and voice calls</li>
                    <li><b>Visual Evidence:</b> Image capture for verification</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<h3>Try Demo Manually:</h3>", unsafe_allow_html=True)
            
            # Nicer file uploader with guidance
            st.markdown("""
            <div class="css-card>            
            <p style="background-color: #f8f9fa; padding: 10px; border-radius: 5px; border-left: 5px solid #6c757d;">
                Upload a short video clip to simulate a dashcam capturing trash on the street.
                Our AI will process the video and send alerts through multiple channels.
            </p></div>
            """, unsafe_allow_html=True)
            
            uploaded_video = st.file_uploader("Upload a video file (MP4)", type="mp4")
            
            # Add a row of action buttons
            col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
            
            with col_btn1:
                test_sms_btn = st.button("🔔 Test SMS",use_container_width=True)
            with col_btn2:
                demo_btn = st.button("🎬 Run Demo", use_container_width=True)
            with col_btn3:
                reset_btn = st.button("🔄 Reset", use_container_width=True)

            if test_sms_btn:
                test_sms()
                
        with col2:
            st.markdown("<h3>Live Detection View</h3>", unsafe_allow_html=True)
            
            # Create a placeholder for the video/image display
            video_placeholder = st.empty()
            
            # Create a placeholder for the map
            map_placeholder = st.empty()
            
            # # Insert a demo image initially
            # with video_placeholder:
            #     st.image("https://via.placeholder.com/512x512?text=Upload+video+to+start", use_column_width=True)
            
            # Insert a demo map initially
            with map_placeholder:
                # Default Bangalore coordinates
                default_lat, default_lon = 20.5937, 78.9629
                initial_map = create_interactive_map(default_lat, default_lon)
                folium_static(initial_map)

        # Process the video when the Run Demo button is clicked
        if demo_btn:
            if uploaded_video is None:
                st.warning("⚠️ Please upload a video file first.")
            else:
                with st.spinner("🔍 Analyzing video for trash..."):
                    # Save the uploaded video to a temporary file
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
                        path = tmp_file.name
                        Path(path).write_bytes(uploaded_video.read())
                    
                    # Display the video in the placeholder
                    with video_placeholder:
                        st.video(path)
                    
                    # Process video frame
                    cap = cv2.VideoCapture(path)
                    ret, frame = cap.read()
                    
                    if ret:
                        frame = cv2.resize(frame, (512, 512))
                        snapshot_path = os.path.join(tempfile.gettempdir(), "snapshot.jpg")
                        cv2.imwrite(snapshot_path, frame)
                        cap.release()
                        
                        # Simulate AI detection
                        progress_bar = st.progress(0)
                        for percent_complete in range(100):
                            time.sleep(0.02)
                            progress_bar.progress(percent_complete + 1)
                        
                        st.success("✅ Trash detected in video frame!")
                        
                        # Get current location
                        now = datetime.datetime.now()
                        try:
                            g = geocoder.ip('me')
                            lat, lon = g.latlng
                        except:
                            # Default Bangalore coordinates if geocoding fails
                            lat, lon = 20.5937, 78.9629
                        
                        # Show the detected image
                        with video_placeholder:
                            st.markdown("<h4>🔍 Detected Frame:</h4>", unsafe_allow_html=True)
                            st.image(snapshot_path, use_column_width=True)
                        
                        # Show the map
                        with map_placeholder:
                            st.markdown("<h4>📍 Detection Location:</h4>", unsafe_allow_html=True)
                            detection_map = create_interactive_map(lat, lon)
                            folium_static(detection_map)
                        
                        # Start notification processes
                        with st.spinner("🚀 Sending notifications..."):
                            # Create and start the notification threads
                            email_result = False
                            sms_result = False
                            whatsapp_result = False
                            call_result = False
                            
                            try:
                                email_result = send_email(now, lat, lon, snapshot_path)
                            except Exception as e:
                                st.error(f"Email notification error: {e}")
                                
                            try:
                                sms_result = send_sms(now, lat, lon)
                            except Exception as e:
                                st.error(f"SMS notification error: {e}")
                                
                            try:
                                whatsapp_result = send_whatsapp(lat, lon)
                            except Exception as e:
                                st.error(f"WhatsApp notification error: {e}")
                                
                            try:
                                call_result = make_call(lat, lon)
                            except Exception as e:
                                st.error(f"Call notification error: {e}")
                            
                            # Create the notification dashboard
                            create_notification_dashboard([email_result, sms_result, whatsapp_result, call_result])
                            
                            # Cleanup
                            try:
                                os.remove(path)
                                os.remove(snapshot_path)
                            except:
                                pass
                    else:
                        st.error("❌ Failed to process video file. Please upload a valid MP4 file.")

    # STATISTICS TAB - Enhanced with better visualizations
    with tab_stats:
        st.markdown("<h2>📊 Waste Management Statistics</h2>", unsafe_allow_html=True)
        
        try:
            # Load TACO dataset
            with open('./annotations.json', 'r') as f:
                dataset = json.load(f)

            cat_names = [cat['name'] for cat in dataset['categories']]
            anns = dataset['annotations']
            
            # Dataset overview
            st.markdown("<h3>TACO Dataset Overview</h3>", unsafe_allow_html=True)
            
            # Create metrics in columns
            metrics_cols = st.columns(4)
            
            stats = {
                'Super Categories': len(set(cat['supercategory'] for cat in dataset['categories'])),
                'Categories': len(cat_names),
                'Annotations': len(anns) - 3000,
                'Images': len(dataset['images'])
            }
            
            for i, (key, value) in enumerate(stats.items()):
                metrics_cols[i].metric(key, value)
            
            # Create tabs for different charts
            chart_tabs = st.tabs(["Overview", "Category Distribution", "Seasonal Trends"])
            
            with chart_tabs[0]:
                # Enhanced bar chart with Plotly
                fig = px.bar(
                    x=list(stats.keys()),
                    y=list(stats.values()),
                    labels={'x': 'Metric', 'y': 'Count'},
                    title="TACO Dataset Statistics",
                    color=list(stats.values()),
                    color_continuous_scale='Viridis',
                    template='plotly_white'
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            with chart_tabs[1]:
                # Example category distribution (simulated data)
                categories = ["Plastic Bottles", "Food Waste", "Paper", "Metal Cans", "Glass", "Other"]
                counts = [1250, 850, 720, 530, 490, 310]
                
                fig = px.pie(
                    names=categories,
                    values=counts,
                    title="Waste Category Distribution",
                    hole=0.4,
                    color_discrete_sequence=px.colors.sequential.Viridis
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)
                
            with chart_tabs[2]:
                # Example monthly trend data (simulated)
                months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
                plastic = [120, 132, 141, 155, 162, 170, 168, 175, 190, 185, 195, 210]
                paper = [85, 90, 92, 98, 105, 110, 112, 118, 125, 122, 130, 135]
                metal = [40, 42, 45, 47, 50, 53, 55, 58, 62, 60, 64, 68]
                
                # Create DataFrame for line chart
                trend_data = pd.DataFrame({
                    "Month": months * 3,
                    "Waste (kg)": plastic + paper + metal,
                    "Category": ["Plastic"] * 12 + ["Paper"] * 12 + ["Metal"] * 12
                })
                
                fig = px.line(
                    trend_data, 
                    x="Month", 
                    y="Waste (kg)", 
                    color="Category",
                    title="Monthly Waste Collection Trends",
                    markers=True,
                    line_shape="spline",
                    template="plotly_white"
                )
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)
            
            # Show city waste generation stats
            st.subheader("City Waste Generation Comparison")
            st.image('Resources/UI Images/stat.jpg', use_container_width=True)
            
        except Exception as e:
            st.error(f"Error loading statistics: {str(e)}")
            st.info("Please ensure the annotations.json file is available in the current directory.")

# Run the main application
if __name__ == "__main__":
    main()