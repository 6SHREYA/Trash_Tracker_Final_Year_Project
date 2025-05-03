# TrashTracker: AI-Enhanced Waste Surveillance and Notification System

## 📌 Project Overview

**TrashTracker** is an AI-powered waste detection and management system designed to monitor public areas (like streets, parks, and beaches) in real time. The system identifies mixed waste (e.g., plastic bottles, food containers), scores its severity, and alerts waste management authorities for timely intervention. It integrates surveillance, computer vision, machine learning, and smart notification mechanisms to improve environmental cleanliness and operational efficiency.

---

## 🌟 Key Features

- 🔍 **Real-Time Waste Detection**: Uses Convolutional Neural Networks (CNN) to detect various types of waste from surveillance camera feeds.
- 📊 **Intelligent Severity Scoring**: Assigns scores based on waste type, location criticality, and density.
- 📲 **Automated Notifications**: Alerts authorities via email and mobile notifications with relevant data and images.
- ⏱️ **Escalation Mechanism**: Sends higher-priority alerts if waste isn't cleared within 6 hours.
- 📁 **Incident Logging**: Maintains logs for monitoring, analysis, and future optimization.
- 🔧 **Scalable & Adaptive**: Easily integrates with multiple data sources and adapts to different environments using ML feedback.

---

## 🛠️ Tech Stack

- **Frontend**: Streamlit (for dashboard interface)
- **Backend**: Python
- **AI/ML**: OpenCV, TensorFlow/Keras (CNN model)
- **Notification**: SMTP (Email), Push Notification APIs
- **Deployment**: Render / Localhost

---

## ⚙️ Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/6SHREYA/Trash_Tracker_Final_Year_Project
   
2. **Clone the repository**
    ```cmd
   pip install -r requirements.txt
    
4. **Clone the repository**
    ```cmd
   streamlit run app.py

## 🚀 How It Works

- **Detection**: Real-time image feeds are analyzed using a CNN model to detect visible waste.
- **Scoring**: A dynamic algorithm calculates a severity score based on waste density, type, and criticality of the location.
- **Notification**: If the score exceeds a threshold, an alert with an image, timestamp, and location is sent to municipal authorities.
- **Escalation**: If no action is taken within a set time (e.g., 6 hours), a more urgent alert is triggered.
- **Logging**: Each incident is recorded in a log file for future analysis and training.

---

## 📈 Future Enhancements

- Integration with drone-based surveillance
- Web-based admin portal with heatmaps and analytics
- Feedback-based model improvement
- Integration with city government databases
- Mobile app for real-time monitoring and acknowledgment

---

## 👥 Authors

- **Shreya Garg** 
- **Saloni**  
- **Shivani Yadav**  
