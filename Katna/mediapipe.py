import subprocess
import Katna.config as app_config
import os
from multiprocessing import Pool, Process, cpu_count
import Katna.helper_functions as helper
import ntpath
import string
import random
import shutil
import re
from Katna.exceptions import MediapipeAutoflipBuildNotFound

AutoFlipConf = app_config.MediaPipe.AutoFlip


class MediaPipeAutoFlip:

    def __init__(self, build_folder_location, models_folder_location):
        """
        Initializes build folder location for autoflip run.
        """
        self.build_cmd = os.path.join(build_folder_location, AutoFlipConf.BUILD_CMD)
        self.SOURCE_MODEL_FOLDER_LOCATION = models_folder_location
        self.DESTINATION_MODEL_FOLDER_LOCATION = AutoFlipConf.MODELS_FOLDER_LOCATION
        self.RERUN_COUNT = 0

    def _create_models_folder(self):
        """Creates model folder
        """
        # make the model folder dir if it doesn't exist
        if not os.path.isdir(self.DESTINATION_MODEL_FOLDER_LOCATION):
            os.makedirs(self.DESTINATION_MODEL_FOLDER_LOCATION, exist_ok=True)

    def validate_models_folder_location(self):
        """Validates model folder location

        :raises Exception: [description]
        """

        if os.path.exists(self.SOURCE_MODEL_FOLDER_LOCATION) is False:
            raise Exception("Model folder path is invalid. No such directory")

    def _create_softlink(self):
        """Creates simlink from source to destination
        """

        self.validate_models_folder_location()
        source_folder_location = self.SOURCE_MODEL_FOLDER_LOCATION
        destination_folder_location = self.DESTINATION_MODEL_FOLDER_LOCATION

        for item in os.listdir(source_folder_location):
            source_item_location = os.path.join(source_folder_location, item)
            destination_item_location = os.path.join(destination_folder_location, item)
            if not os.path.islink(destination_item_location):
                os.symlink(source_item_location, destination_item_location)


    def _generate_temp_pbtxt_filename(self):
        """Generate random filename of length N

        :return: filename generated randomly
        :rtype: str
        """
        #initializing size of string  
        N = 7
        
        # using random.choices() 
        # generating random strings  
        res = ''.join(random.choices(string.ascii_uppercase +
                                    string.digits, k = N)) 

        return str(res) + ".pbtxt"

    def validate_autoflip_build_path(self):
        """Checks if autoflip build path is valid

        :raises MediapipeAutoflipBuildNotFound: [description]
        """

        if bool(self.build_cmd is None or os.path.exists(self.build_cmd) is False):
                raise MediapipeAutoflipBuildNotFound()

    def _create_pbtxt_folder(self):
        """Creates temp folder to store pbtxt file
        """

        # make the temp dir if it doesn't exist
        if not os.path.isdir(AutoFlipConf.TMP_PBTXT_FOLDER_PATH):
            os.mkdir(AutoFlipConf.TMP_PBTXT_FOLDER_PATH)

    def _create_tmp_pbtxt_file(self):
        """Creates temperary pbtxt file

        :return: filepath of the pbtxt file
        :rtype: str
        """

        # generate filename and filepath of the temp pbtxt file
        filename = self._generate_temp_pbtxt_filename()
        filepath = os.path.join(AutoFlipConf.TMP_PBTXT_FOLDER_PATH, filename)
        
        # copy contents into a new pbtxt file
        # shutil.copyfile(app_config.MediaPipe.AutoFlip.CONFIG_FILE_PBTXT, filepath)

        return filepath

    def _delete_folder(self, folder_path):
        """Deletes temp files folder

        :param dir_path: path of temp folder
        :type dir_path: str
        """
        if os.path.isdir(folder_path):
            shutil.rmtree(folder_path, ignore_errors=True)

    def generate_autoflip_pbtxt(self, data):
        """Generates temp pbtxt file based on configuration data

        :param data: JSON containing mediapipe config
        :type data: dict
        :return: path to pbtxt file
        :rtype: str
        """
        filepath = self._create_tmp_pbtxt_file()
        mapping = AutoFlipConf.get_pbtxt_mapping()

        STABALIZATION_THRESHOLD = data[AutoFlipConf.STABALIZATION_THRESHOLD_KEYNAME]
        BLUR_AREA_OPACITY = data[AutoFlipConf.BLUR_AREA_OPACITY_KEYNAME]
        ENFORCE_FEATURES = data[AutoFlipConf.ENFORCE_FEATURES_KEYNAME]

        # write the contents of the file
        with open(filepath, "a") as f_temp:

            with open(app_config.MediaPipe.AutoFlip.CONFIG_FILE_PBTXT, "r") as f_pbtxt:

                # flag to set is_required in pbtxt as we move line by line
                set_is_required = False

                # for each line run the following checks
                for line in f_pbtxt.readlines():
                    feature_matched = next((prop_name for prop_name in AutoFlipConf.ENFORCE_FEATURES.keys() if re.search(r'%s' % prop_name, line)), False)

                    if re.search(r'%s*' % mapping[AutoFlipConf.BLUR_AREA_OPACITY_KEYNAME], line):
                        f_temp.write(line.replace(str(AutoFlipConf.DEFAULT_BLUR_AREA_OPACITY), str(BLUR_AREA_OPACITY)))

                    elif re.search(r'%s*' % mapping[AutoFlipConf.STABALIZATION_THRESHOLD_KEYNAME], line):
                        f_temp.write(line.replace(str(AutoFlipConf.DEFAULT_MOTION_STABALIZATION_THRESHOLD), str(STABALIZATION_THRESHOLD)))
                    elif feature_matched:

                        # if the features matched is set true
                        if ENFORCE_FEATURES[feature_matched]:
                            # if you encounter is_required.. 
                            set_is_required = True
                        else:
                            set_is_required = False
                            
                        f_temp.write(line)

                    elif re.search(r'is_required*', line):
                        if set_is_required:
                            f_temp.write(line.replace("false", "true"))
                            set_is_required = False
                        else:
                            f_temp.write(line)
                    else:
                        f_temp.write(line)


        return filepath


    def parse_mediapipe_config(self):
        """Parse mediapipe conf

        :return: JSON with mediapipe config
        :rtype: dict
        """
        conf = app_config.MediaPipe.AutoFlip.get_conf()
        return conf

    def launch_mediapipe_autoflip_process(self, input_file_path, output_file_path, output_aspect_ratio, graph_file_pbtxt = None):
        """Launches subproocess to run autoflip

        :param input_file_path: [description]
        :type input_file_path: [type]
        :param output_file_path: [description]
        :type output_file_path: [type]
        :param output_aspect_ratio: [description]
        :type output_aspect_ratio: [type]
        :param graph_file_pbtxt: [description], defaults to None
        :type graph_file_pbtxt: [type], optional
        :return: [description]
        :rtype: [type]
        """

        print("Launched mediapipe autoflip pipeline for file %s" % (input_file_path))

        if graph_file_pbtxt is None:
            graph_file_pbtxt = AutoFlipConf.CONFIG_FILE_PBTXT

        process = subprocess.check_output([self.build_cmd, "--calculator_graph_config_file=%s" % graph_file_pbtxt,
                                           "--input_side_packets=input_video_path=%s,output_video_path=%s,aspect_ratio=%s" % (
                                           input_file_path,
                                           output_file_path,
                                           output_aspect_ratio)
                                           ],
                                           stderr=subprocess.STDOUT,
                                           )

    def exit_clean(self):
        """Removes the models folder and the temp directory
        """
        self._delete_folder(AutoFlipConf.TMP_PBTXT_FOLDER_PATH)
        self._delete_folder(self.DESTINATION_MODEL_FOLDER_LOCATION)

    def prepare_pipeline(self):
        """Initializes mediapipe models and tmp directories

        :raises e: Exception that simlink could not be created
        """
        self.validate_autoflip_build_path()
        self._create_models_folder()
        try:
            self._create_softlink()
        except Exception as e:
            print("\nFailed to create simlink to link models folder. Add all files from %s to %s" % (self.SOURCE_MODEL_FOLDER_LOCATION, self.DESTINATION_MODEL_FOLDER_LOCATION))
            raise e

        self._create_pbtxt_folder()

    def _run(self, pbx_filepath, input_file_path, output_file_path, output_aspect_ratio):
        """Private run method which launchs the mediapipe pipeline and manages rerun
        if required.

        :param pbx_filepath: [description]
        :type pbx_filepath: [type]
        :param input_file_path: [description]
        :type input_file_path: [type]
        :param output_file_path: [description]
        :type output_file_path: [type]
        :param output_aspect_ratio: [description]
        :type output_aspect_ratio: [type]
        :raises e: [description]
        :raises e: [description]
        :raises e: [description]
        """

        try:
            self.launch_mediapipe_autoflip_process(input_file_path, output_file_path, output_aspect_ratio, pbx_filepath)
        except subprocess.CalledProcessError as e:

            if (e.returncode == -11):
                self.RERUN_COUNT += 1
                if self.RERUN_COUNT <= AutoFlipConf.RERUN_LIMIT:
                    print("Segmentation Fault : Re-executing the pipeline - Attempt %s" % str(self.RERUN_COUNT))
                    self._run(pbx_filepath, input_file_path, output_file_path, output_aspect_ratio)
                else:
                    print("Segmentation Fault : Re-run limit reached.")
                    raise e
            else:
                raise e
        except Exception as e:
            raise e
                    

    def run(self, input_file_path, output_file_path, output_aspect_ratio):
        """Main handler for running autoflip via subprocess

        :param input_file_path: [description]
        :type input_file_path: [type]
        :param output_file_path: [description]
        :type output_file_path: [type]
        :param output_aspect_ratio: [description]
        :type output_aspect_ratio: [type]
        :raises e: [description]
        """
        self.RERUN_COUNT = 0
        data = self.parse_mediapipe_config()
        pbx_filepath = self.generate_autoflip_pbtxt(data)
        try:
            self._run(pbx_filepath, input_file_path, output_file_path, output_aspect_ratio)
        except Exception as e:
            raise e
        
            
