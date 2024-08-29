import os
import time
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.clock import Clock
from jnius import autoclass
from kivy.utils import platform

if platform == 'android':
    from android.permissions import request_permissions, Permission

# Load necessary Java classes
PythonActivity = autoclass('org.kivy.android.PythonActivity')
Camera = autoclass('android.hardware.Camera')
SurfaceView = autoclass('android.view.SurfaceView')
MediaRecorder = autoclass('android.media.MediaRecorder')
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
            self.camera = Camera.open()
            
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

# Example usage in Kivy app
class CameraApp(App):
    def build(self):
        if platform == 'android':
            request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])

            internal_storage_path = PythonActivity.mActivity.getFilesDir().getAbsolutePath() + '/DataApp'
            # external_storage_path = os.path.expanduser('~/storage')
            if os.path.exists(internal_storage_path):
                output_file = f"{internal_storage_path}/test_video.mp4"
                path_label = Label(text=f"External storage path: {internal_storage_path}")
            else:
                path_label = Label(text="External storage path does not exist")
                output_file = None
        else:
            path_label = Label(text="This is not an Android device")
            output_file = None
        
        if output_file:
            recorder = CameraRecorder()
            recorder.start_recording(output_file)
            # Let it record for a while (e.g., 10 seconds)
            time.sleep(10)
            recorder.stop_recording()
        
        return path_label

if __name__ == "__main__":
    CameraApp().run()
