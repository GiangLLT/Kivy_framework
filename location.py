import os
from kivy.app import App
from kivy.uix.label import Label
from kivy.clock import Clock
from plyer import gps
import requests
import json
from datetime import datetime
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload  # Add this line
from googleapiclient.http import MediaFileUpload

class LocationApp(App):
    def build(self):
        self.label = Label(text="Getting location...")
        self.start_tracking()
        return self.label

    def start_tracking(self):
        gps.configure(on_location=self.on_location, on_status=self.on_status)
        gps.start(minTime=60000, minDistance=0)  # 1 phút, 0 mét
        self.kml_file = "locations.kml"
        self.init_kml_file()
        self.creds = self.authenticate_google_drive()

    def init_kml_file(self):
        with open(self.kml_file, 'w') as f:
            f.write("""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document>
    <name>Locations</name>
""")

    def on_location(self, **kwargs):
        self.label.text = "Location: {}".format(kwargs)
        self.append_location_to_kml(kwargs)
        self.upload_to_google_drive(self.kml_file)
        
    def on_status(self, stype, status):
        self.label.text = "GPS status: {0} - {1}".format(stype, status)

    def append_location_to_kml(self, location_data):
        with open(self.kml_file, 'a') as f:
            f.write(f"""
    <Placemark>
        <TimeStamp><when>{datetime.utcnow().isoformat()}Z</when></TimeStamp>
        <Point>
            <coordinates>{location_data['lon']},{location_data['lat']},0</coordinates>
        </Point>
    </Placemark>
""")

    def authenticate_google_drive(self):
        SCOPES = ['https://www.googleapis.com/auth/drive.file']
        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        return creds

    def upload_to_google_drive(self, file_path):
        service = build('drive', 'v3', credentials=self.creds)
        file_metadata = {'name': os.path.basename(file_path)}
        media = MediaFileUpload(file_path, mimetype='application/vnd.google-earth.kml+xml')
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        print(f"File ID: {file.get('id')}")

if __name__ == '__main__':
    LocationApp().run()



# from kivy.app import App
# from kivy.uix.label import Label
# from kivy.clock import Clock
# from plyer import gps
# import requests
# import json

# class LocationApp(App):
#     def build(self):
#         self.label = Label(text="Getting location...")
#         self.start_tracking()
#         return self.label

#     def start_tracking(self):
#         gps.configure(on_location=self.on_location, on_status=self.on_status)
#         gps.start(minTime=60000, minDistance=0)  # 1 phút, 0 mét

#     def on_location(self, **kwargs):
#         self.label.text = "Location: {}".format(kwargs)
#         self.send_location(kwargs)
        
#     def on_status(self, stype, status):
#         self.label.text = "GPS status: {0} - {1}".format(stype, status)

#     def send_location(self, location_data):
#         url = 'http://yourserver.com/api/location'
#         headers = {'Content-Type': 'application/json'}
#         try:
#             response = requests.post(url, data=json.dumps(location_data), headers=headers)
#             if response.status_code == 200:
#                 print("Location sent successfully")
#             else:
#                 print("Failed to send location")
#         except Exception as e:
#             print(f"Error sending location: {str(e)}")

# if __name__ == '__main__':
#     LocationApp().run()