import os
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.utils import platform
from jnius import autoclass

if platform == 'android':
    from android.permissions import request_permissions, Permission

# Load necessary Java classes
PythonActivity = autoclass('org.kivy.android.PythonActivity')
Camera = autoclass('android.hardware.Camera')
SurfaceView = autoclass('android.view.SurfaceView')
MediaRecorder = autoclass('android.media.MediaRecorder')
Environment = autoclass('android.os.Environment')
File = autoclass('java.io.File')

class CameraRecorder(object):
    def __init__(self):
        self.camera = None
        self.surface_view = None
        self.media_recorder = None
        self.is_recording = False

    def start_recording(self, output_file):
        try:
            # Open camera
            self.camera = Camera.open(Camera.CameraInfo.CAMERA_FACING_BACK)
            
            # Create and set up SurfaceView
            self.surface_view = SurfaceView(PythonActivity.mActivity)
            self.camera.setPreviewDisplay(self.surface_view.getHolder())
            self.camera.startPreview()
            
            # Configure MediaRecorder
            self.media_recorder = MediaRecorder()
            self.camera.unlock()
            self.media_recorder.setCamera(self.camera)
            self.media_recorder.setAudioSource(MediaRecorder.AudioSource.CAMCORDER)
            self.media_recorder.setVideoSource(MediaRecorder.VideoSource.CAMERA)
            self.media_recorder.setOutputFormat(MediaRecorder.OutputFormat.MPEG_4)
            self.media_recorder.setVideoEncoder(MediaRecorder.VideoEncoder.DEFAULT)
            self.media_recorder.setAudioEncoder(MediaRecorder.AudioEncoder.DEFAULT)
            self.media_recorder.setOutputFile(output_file)
            self.media_recorder.prepare()
            self.media_recorder.start()
            self.is_recording = True
        except Exception as e:
            print(f"Error during start_recording: {e}")
            self.stop_recording()

    def stop_recording(self):
        try:
            if self.is_recording:
                self.media_recorder.stop()
                self.media_recorder.reset()
                self.media_recorder.release()
                self.camera.lock()
                self.camera.release()
                self.surface_view.getHolder().removeCallback(self.surface_view.getHolder())
                self.is_recording = False
        except Exception as e:
            print(f"Error during stop_recording: {e}")

class CameraApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')
        self.path_label = Label(text="")

        self.button = Button(text="Start Recording")
        self.button.bind(on_press=self.toggle_recording)
        
        layout.add_widget(self.path_label)
        layout.add_widget(self.button)

        if platform == 'android':
            request_permissions([Permission.CAMERA, Permission.RECORD_AUDIO, Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])

            download_path = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS).getAbsolutePath()
            if not os.path.exists(download_path):
                os.makedirs(download_path)
                
            self.output_file = f"{download_path}/test_video.mp4"
            self.path_label.text = f"Storage path: {self.output_file}"
        else:
            self.path_label.text = "This is not an Android device"
            self.output_file = None
        
        self.recorder = CameraRecorder()

        return layout

    def toggle_recording(self, instance):
        if not self.recorder.is_recording:
            self.recorder.start_recording(self.output_file)
            self.button.text = "Stop Recording"
        else:
            self.recorder.stop_recording()
            self.button.text = "Start Recording"

if __name__ == "__main__":
    CameraApp().run()
