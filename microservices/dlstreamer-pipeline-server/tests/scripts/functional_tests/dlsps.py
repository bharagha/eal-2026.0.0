#
# Apache v2 license
# Copyright (C) 2024-2025 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
# 

import subprocess
import os
import time
import unittest
import dlsps_utils as dlsps_module 
from configs import *

JSONPATH = os.path.dirname(os.path.abspath(__file__)) + '/../configs/dlsps_config.json'

class generate_repo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path = os.path.dirname(os.path.abspath(__file__))
        cls.dlsps_utils = dlsps_module.dlsps_utils()
        time.sleep(10)

    def test_generate_repo(self):
        self.dlsps_utils.generate_repo_dlsps()

class test_dlsps_cases(unittest.TestCase):
    """
    Functional test cases for the DL Streamer Pipeline Server.

    This class uses the `dlsps_utils` module to configure, run, and validate
    the DL Streamer Pipeline Server. It includes setup, execution, and teardown
    steps for the tests.
    """

    @classmethod
    def setUpClass(cls):
        """
        Sets up the test environment before running the test cases.

        Initializes the `dlsps_utils` instance and sets the path for the test scripts.
        """
        cls.path = os.path.dirname(os.path.abspath(__file__))
        cls.dlsps_utils = dlsps_module.dlsps_utils()

    def test_dlsps(self):
        """
        Executes the functional test for the DL Streamer Pipeline Server.

        Steps:
        1. Reads the test case configuration from a JSON file.
        2. Updates the Docker Compose and DL Streamer configuration.
        3. Builds and runs the DL Streamer Pipeline Server.
        4. Sends a POST request to start a pipeline and validates its status.
        5. Checks container logs for expected keywords.

        Assertions:
            Asserts that all expected keywords are found in the container logs.

        Environment Variables:
            TEST_CASE (str): Name of the test case to execute.
        """
        test_case = os.environ['TEST_CASE']
        key, value = self.dlsps_utils.json_reader(test_case, JSONPATH)
        if value.get("device_type") == "dGPU":
            if not self.dlsps_utils.check_for_device():
                self.skipTest("Intel(R) Arc(TM) device not found. Skipping the test case.")
        self.dlsps_utils.add_proxy_to_docker_compose(value)
        if value.get("type_r")=="minio": 
            self.dlsps_utils.change_docker_compose_for_minio(value)
        else:
            self.dlsps_utils.change_docker_compose_for_standalone()
        if value.get("type") == "wrong_mqtt_host" or value.get("type") == "wrong_mqtt_port" or value.get("type") == "wrong_s3_host" or value.get("type") == "wrong_s3_port" or value.get("type") == "wrong_s3_username" or value.get("type") == "wrong_s3_password" or value.get("type") == "wrong_opcua_host" or value.get("type") == "wrong_opcua_port" or value.get("type") == "wrong_opcua_username" or value.get("type") == "wrong_opcua_password":
            self.dlsps_utils.change_env(value)
        if value.get("instance") == "multifilesrc_multipipeline_gvadetect":
            self.dlsps_utils.change_config_multipipeline(value)
        else:
            self.dlsps_utils.change_config_for_dlsps_standalone(value)
        
        self.dlsps_utils.common_service_steps_dlsps()
        time.sleep(2)
        if value.get("type") == "multipipeline_gvadetect":
            self.dlsps_utils.execute_curl_command_multipipeline(value)
        elif value.get("type") == "workload1" or value.get("type") == "workload5" or value.get("type") == "workload6" or value.get("type") == "workload1_add_tensor_data" or value.get("type") == "workload1_GPU" or value.get("type") == "workload1_1" or value.get("type") == "workload1_2" or value.get("type") == "workload1_3"or value.get("type") == "workload1_4" or value.get("type") == "workload2" or value.get("type") == "workload2_GPU" or value.get("type") == "workload2_1" or value.get("type") == "workload2_2" or value.get("type") == "workload2_3" or value.get("type") == "workload2_4" or value.get("type") == "workload2_5" or value.get("type") == "workload2_publish_frame_false_add_tensor_data_false" or value.get("type") == "workload2_publish_frame_false_add_tensor_data_true" or value.get("type") == "workload2_publish_frame_true_add_tensor_data_false" or value.get("type") == "workload2_publish_frame_true_add_tensor_data_true":
            self.dlsps_utils.execute_curl_command_workload(value)
        elif value.get("type") == "workload1_multiinstance" or value.get("type") == "workload1_multiinstance_GPU" or value.get("type") == "workload1_multiinstance_CPUandGPU":
            self.dlsps_utils.execute_curl_command_multiinstance_workload1(value)
        elif value.get("type") == "multiinstance":
            self.dlsps_utils.execute_curl_command_multiinstance(value)
        elif value.get("type") == "rtsp_server_instances_CPU" or value.get("type") == "rtsp_server_instances_GPU" or value.get("type") == "rtsp_server_instances_CPU_and_GPU" or value.get("type") == "video_instances_CPU" or value.get("type") == "video_instances_GPU" or value.get("type") == "video_instances_CPU_and_GPU":
            self.dlsps_utils.execute_curl_command_multiinstance_rtsp(value)
        elif value.get("type") == "workload2_1_wrong_detection" or value.get("type") == "workload2_1_wrong_classification" or value.get("type") == "workload2_1_wrong_backend":
            self.dlsps_utils.execute_curl_command_input_error(value)
        elif value.get("type") == "axis_rtsp_camera" or value.get("type") == "axis_rtsp_camera_GPU":
            self.dlsps_utils.execute_curl_command_axis_camera(value)
        elif value.get("type_r") == "minio_wrong":
            self.dlsps_utils.execute_curl_command_minio_wrong(value)
        elif value.get("type") == "minio":
            self.dlsps_utils.execute_curl_command_minio(value)
        elif value.get("type_r") == "opcua" or value.get("type") == "opcua_config":
            self.dlsps_utils.execute_curl_command_opcua(value)
        else:
            self.dlsps_utils.execute_curl_command(value)
        self.assertTrue(self.dlsps_utils.container_logs_checker_dlsps("dlsps",test_case,value))
        if value.get("type") == "mqtt_gvadetect" or value.get("type") == "gvapython_mqtt_udfloader":
            self.dlsps_utils.run_mosquitto_subclient_and_check_logs(value)
        if value.get("type") == "verify_metadata_OPCUA" or value.get("type") == "verify_metadata_OPCUA_config":
            time.sleep(5)
            self.dlsps_utils.run_opcua_subclient_and_check_logs(value)

        
    @classmethod
    def tearDownClass(cls):
        """
        Cleans up the test environment after running the test cases.

        Steps:
        1. Stops and removes Docker containers and volumes.
        2. Restores the original `docker-compose.yml` and `config.json` files.
        """
        os.chdir('{}'.format(cls.dlsps_utils.dlsps_path))
        subprocess.run('docker compose down -v', shell=True, executable='/bin/bash', check=True)
        subprocess.run('git checkout docker-compose.yml', shell=True, executable='/bin/bash', check=True)
        os.chdir('{}'.format(cls.dlsps_utils.dlsps_path + "/../configs/default"))
        subprocess.run('git checkout config.json', shell=True, executable='/bin/bash', check=True)
        time.sleep(5)
