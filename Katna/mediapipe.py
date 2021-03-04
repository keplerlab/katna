import subprocess
from Katna.config import MediapipeConfig
import os
from multiprocessing import Pool, Process, cpu_count
import Katna.helper_functions as helper
import ntpath
from Katna.exceptions import MediapipeAutoflipBuildNotFound


class MediaPipeAutoFlip:

    def __init__(self, build_folder_location):
        """
        Initializes build folder location for autoflip run.
        """
        self.build_cmd = os.path.join(build_folder_location, MediapipeConfig.AutoFlip.BUILD_CMD)

    
    def validate_autorun_build_path(self):
        """Checks if mediapipe autorun build path is valid.
        """

        if bool(self.build_cmd is None or os.path.exists(self.build_cmd) is False):
                raise MediapipeAutoflipBuildNotFound()

    def updated_autoflip_pbtxt(self, data):
        """
        TODO: Will update the autoflip pbtxt file based on the json data
        """
        pass

    def parse_mediapipe_config(self):
        """
        TODO: Will parse the mediapipe config JSON
        """
        return {}

    def launch_mediapipe_autoflip_process(self, input_file_path, output_file_path, output_aspect_ratio):
        """
        TODO: Will launch a subprocesses for the video at given file path
        """

        print(" Launched mediapipe autoflip pipeline for file %s with process %s, dump at %s: " % (input_file_path, os.getpid(), output_file_path))

        process = subprocess.check_output([self.build_cmd, "--calculator_graph_config_file=%s" % MediapipeConfig.AutoFlip.CONFIG_FILE_PBTXT,
                                           "--input_side_packets=input_video_path=%s,output_video_path=%s,aspect_ratio=%s" % (
                                           input_file_path,
                                           output_file_path,
                                           output_aspect_ratio)
                                           ])
        return (input_file_path, process)

    def run(self, input_file_path, output_file_path, output_aspect_ratio):
        """
        TODO: main method to run mediapipe autoflip for a single file.
        """
        data = self.parse_mediapipe_config()
        self.updated_autoflip_pbtxt(data)
        try:
            self.launch_mediapipe_autoflip_process(input_file_path, output_file_path, output_aspect_ratio)
        except subprocess.CalledProcessError as e:
            print("\n Subprocess error")
            print(str(e.output))
        except Exception as e:
            raise e
