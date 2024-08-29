import os
import sys
import jnius 
from jnius import autoclass
from kivy.app import App
from kivy.uix.label import Label
from kivy.utils import platform
import time

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
            request_permissions([Permission.CAMERA, Permission.RECORD_AUDIO, Permission.WRITE_EXTERNAL_STORAGE])

            # Use pyjnius to access Android specific APIs
            Environment = autoclass('android.os.Environment')
            external_storage_path = Environment.getExternalStorageDirectory().getAbsolutePath() + '/DataApp'

            if os.path.exists(external_storage_path):
                output_file = f"{external_storage_path}/test_video.mp4"
                path_label = Label(text=f"Đường dẫn lưu trữ: {external_storage_path}")
                if output_file:
                    time.sleep(2)
                    Label(text=f"Bắt đầu khởi tạo")
                    print("Bắt đầu khởi tạo")
                    recorder = CameraRecorder()
                    Label(text=f"Bắt đầu ghi hình")
                    print("Bắt đầu ghi hình")
                    recorder.start_recording(output_file)
                    Label(text=f"-----------------------------")
                    print("-----------------------------")
                    # Cho phép ghi hình trong một khoảng thời gian (ví dụ: 10 giây)
                    time.sleep(10)
                    Label(text=f"Đẫ xong")
                    print("Đẫ xong")
                    recorder.stop_recording()
                    Label(text=f"Dừng ghi hình")
                    print("Dừng ghi hình")
            else:
                path_label = Label(text="Thư mục lưu trữ không tồn tại")
                output_file = None
        else:
            path_label = Label(text="Thiết bị này không phải là Android")
            output_file = None
        
        # if output_file:
        #     time.sleep(2)
        #     print("Bắt đầu khởi tạo")
        #     recorder = CameraRecorder()
        #     print("Bắt đầu ghi hình")
        #     recorder.start_recording(output_file)
        #     print("-----------------------------")
        #     # Cho phép ghi hình trong một khoảng thời gian (ví dụ: 10 giây)
        #     time.sleep(10)
        #     print("Đẫ xong")
        #     recorder.stop_recording()
        #     print("Dừng ghi hình")
        
        return path_label

if __name__ == "__main__":
    CameraApp().run()
