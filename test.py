import sys
from PIL import Image
import tensorflow as tf
import numpy as np
import cv2, geocoder
import os, smtplib
import time
import datetime
from twilio.rest import Client
import yagmail
from geopy.geocoders import Nominatim

tf.compat.v1.disable_eager_execution()

# Twilio credentials (✅ Fixed)
TWILIO_SID = 'ACe91623fd25f7469c81a0e35add822bc2'
TWILIO_AUTH = 'b68be38bc93812e02fd8399585fb6d82'

# Email app password (✅ Use App Password only)
EMAIL_ADDRESS = "trashtrackerproject@gmail.com"
EMAIL_PASSWORD = "kecvuuderioxpsqk"  # ✅ App Password (Not Gmail login password)


def sms(t1, lat, lon):
    try:
        geolocator = Nominatim(user_agent="geoapiExercises")
        location = geolocator.reverse(f"{lat},{lon}")
        address = ",".join(list(location.raw['address'].values()))
        google_maps_link = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
        body = f"🚨 Attention Required!!\nScrap detected\nTime: {t1}\nLocation: {google_maps_link}\nAddress: {address}"
        client = Client(TWILIO_SID, TWILIO_AUTH)
        client.messages.create(body=body, from_='+15513832453', to='+919999889373')
        print("✅ SMS sent.")
    except Exception as e:
        print("❌ SMS Error:", e)


def call(lat, lon):
    try:
        client = Client(TWILIO_SID, TWILIO_AUTH)
        call = client.calls.create(
            twiml="<Response><Say>🚨 Garbage Detected! Attention Required.</Say></Response>",
            from_='+15513832453',
            to='+919999889373'
        )
        print(f"✅ Call SID: {call.sid}")
    except Exception as e:
        print("❌ Call Error:", e)


def whatsapp1(lat, lon):
    try:
        client = Client(TWILIO_SID, TWILIO_AUTH)
        message = client.messages.create(
            body='🚨 Scrap Detected!',
            persistent_action=[f'geo:{lat},{lon}|Scrap Location'],
            from_='whatsapp:+14155238886',
            to='whatsapp:+919999889373'
        )
        print(f"✅ WhatsApp SID: {message.sid}")
    except Exception as e:
        print("❌ WhatsApp Error:", e)


def email_generate(t1, t2, lat, lon):
    try:
        geolocator = Nominatim(user_agent="geoapiExercises")
        location = geolocator.reverse(f"{lat},{lon}")
        address = ",".join(list(location.raw['address'].values()))
        google_maps_link = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
        subject = "🚨 Trash Alert Notification"
        html = f"""
        <h2>🚨 Attention Required!!</h2>
        <p><strong>Address:</strong> {address}</p>
        <p><a href="{google_maps_link}">Location on Google Maps</a></p>
        <p><strong>Scrap detected Time:</strong> {t1}</p>
        """
        yag = yagmail.SMTP(EMAIL_ADDRESS, EMAIL_PASSWORD)
        yag.send(to="shreya06lg@gmail.com", subject=subject, contents=[html, yagmail.inline("./kill.jpg")])
        print("✅ Email sent.")
    except Exception as e:
        print("❌ Email Error:", e)


# --- Model Setup ---
def load_graph(model_file):
    graph = tf.Graph()
    graph_def = tf.compat.v1.GraphDef()
    with open(model_file, "rb") as f:
        graph_def.ParseFromString(f.read())
    with graph.as_default():
        tf.import_graph_def(graph_def)
    return graph


def read_tensor_from_image_file(file_name, input_height=224, input_width=224, input_mean=128, input_std=128):
    file_reader = tf.io.read_file(file_name)
    image_reader = tf.image.decode_jpeg(file_reader, channels=3)
    float_caster = tf.cast(image_reader, tf.float32)
    dims_expander = tf.expand_dims(float_caster, 0)
    resized = tf.compat.v1.image.resize_bilinear(dims_expander, [input_height, input_width])
    normalized = tf.divide(tf.subtract(resized, [input_mean]), [input_std])
    sess = tf.compat.v1.Session()
    result = sess.run(normalized)
    return result


def load_labels(label_file):
    with open(label_file, "r") as f:
        return [line.strip() for line in f.readlines()]


# --- Detection Logic ---
file_name = "kill.jpg"
model_file = "files/retrained_graph.pb"
label_file = "files/retrained_labels.txt"

video_reader = cv2.VideoCapture("D:\\JIT\\garbage_detector_kaggle\\videos\\1 - Made with Clipchamp.mp4")
li = []

try:
    c = 2
    while True:
        ret, image_1 = video_reader.read()
        if not ret:
            break
        if c > 1:
            cv2.imwrite("kill.jpg", image_1)
            c -= 1
        for _ in range(10): video_reader.grab()

        t = read_tensor_from_image_file("kill.jpg")
        graph = load_graph(model_file)
        input_name = "import/input"
        output_name = "import/final_result"
        input_operation = graph.get_operation_by_name(input_name)
        output_operation = graph.get_operation_by_name(output_name)

        with tf.compat.v1.Session(graph=graph) as sess:
            results = sess.run(output_operation.outputs[0], {input_operation.outputs[0]: t})
        results = np.squeeze(results)

        labels = load_labels(label_file)
        top_k = results.argsort()[-5:][::-1]

        for i in top_k:
            if labels[i] == "not clean":
                li.append(results[i])

except Exception as e:
    print("❌ Video Processing Error:", e)

if li:
    density = sum(li) / len(li)
    print(f"🧼 Dirtiness Score: {density:.2f}")
    g = geocoder.ip('me')
    lat, lon = g.latlng
    ct = datetime.datetime.now()

    if density < 0.96:
        sms(ct, lat, lon)
    elif density < 0.98:
        whatsapp1(lat, lon)
    else:
        email_generate(ct, 0, lat, lon)

else:
    print("✅ No trash detected.")
