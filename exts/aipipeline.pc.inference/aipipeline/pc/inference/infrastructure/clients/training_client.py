import requests
from requests import RequestException, Response
import logging
from logging import Logger
import time
import json
import os
from typing import List
from pathlib import Path
#from circuitbreaker import CircuitBreaker, CircuitBreakerMonitor, CircuitBreakerError
from aipipeline.pc.inference.domain.exceptions.infrastructure_api_client_exception import *
from aipipeline.pc.inference.domain.models.models import *

class TrainingClient:
    url : str = None
    api_url : str = None
    port : int = None
    endpoints : dict = None
        
    def __init__(self, url, port, endpoints):

        # Set up logger
        self.logger : Logger = logging.getLogger(name = "Pointcloud Training Inference API Logger")
        logging.basicConfig(filename = "logs/client_logging.log", encoding = 'utf-8', level = logging.DEBUG)
        self.logger.debug("Initializing Pointcloud Training Inference API Client")

        self.MAX_RETRIES = 6

        TrainingClient.url = url
        TrainingClient.port = port
        TrainingClient.endpoints = endpoints
        TrainingClient.api_url = url + ":" + str(port)

    def _request_external_api_health(self) -> bool:
        self.logger.debug("Checking API health")
        try:
            request = requests.get(url = os.path.join(TrainingClient.api_url, TrainingClient.endpoints["health_endpoint"])) 
            return request
        except RequestException as e:
            raise e
        except Exception as ex:
            raise ex
        
        
    def check_external_api_health(self) -> bool:
        for i in range(10):
            try:
                request = self._request_external_api_health()
                if request:
                    return True
                time.sleep(2)
            except:
                pass
        raise ClientException(additional_info="Please check API port")
    
    def _get_external_call(self, url, request_body: dict, retry_count:int = 0) -> Response:
        try:
            self.logger.debug(f"Sending GET Request to Pointcloud Training Inference API on url: {url}")
            response = requests.get(url = url, params= request_body)
            return response
        except requests.exceptions.ConnectionError as e:
            self.logger.error(f"GET Request to Pointcloud Training Inference API on url: {url} failed; error: {e}")
            
            if retry_count < self.MAX_RETRIES:
                self.logger.debug(f"Retrying GET Request to Pointcloud Training Inference API url: {url}")
                time.sleep(2)
                return self._get_external_call(url = url, retry_count= retry_count+1)
            raise e
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error while trying to communicate with Pointcloud Training Inference API GET Request URL: {url}; Request Body: {request_body}; Exception Occured {e.__str__()}")
            raise e
        
    def _patch_external_call(self, url, request_body: dict, retry_count: int = 0) -> Response:
        try:
            self.logger.debug(f"Trying PATCH Request to Pointcloud Training Inference API on URL : {url}")
            response = requests.patch(url = url, params = request_body)
            return response
        except requests.exceptions.ConnectionError as e:
            self.logger.error(f"PATCH Request to Pointcloud Training Inference API on URL: {url} failed; error: {e}")

            if retry_count < self.MAX_RETRIES:
                self.logger.debug(f"Retrying PATCH Request to Pointcloud Training Inference API on URL: {url}")
                time.sleep(2)
                return self._post_external_call(url=url, request_body=request_body, retry_count=retry_count+1)
            raise e
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error while communicating with Pointcloud Training Inference API PATCH Request URL: {url}; Request Body: {request_body}; Exception Occured {e.__str__()}")
            raise e

    def _delete_external_call(self, url, request_body: dict, retry_count : int = 0) -> Response:
        try:
            self.logger.debug(f"Trying DELETE Request to Pointcloud Training Inference API on url: {url}")
            response = requests.delete(url = url, params = request_body)
            return response
        except requests.exceptions.RequestException as e:
            self.logger.error(f"DELETE Request to Pointcloud Training Inference API on URL: {url} failed; error: {e}")

            if retry_count < self.MAX_RETRIES:
                self.logger.debug(f"Retrying DELETE Request to Pointcloud Training Inference API on URL: {url}")
                time.sleep(2)
                return self._delete_external_call(url=url, request_body=request_body, retry_count=retry_count+1)
            raise e
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error while trying to communicate with Pointcloud Training Inference API DELETE Request on URL: {url}, Request Body: {request_body}; Exception Occured {e.__str__()}")
            raise e
        
    # endpoints: @Anthony kel wahde btekhod specific params, so i just created a common 
    def _handle_response(self, url: str, response: Response) -> Response:
        if response.status_code == 200:
            self.logger.debug(f"Pointcloud Training Inference API GET Request successful: {response.text}")
            return response.json()
        else:
            self.logger.error(f"Pointcloud Training Inference API GET Request {url} failed! {response.text}")
            raise ClientException(additional_info= response.text)
        
    def train_endpoint(self, params : TrainingParams) -> Response:
        self.logger.debug(f"POINTCLOUD TRAINING INFERENCE API Communication: Training Model")

        url: str = os.path.join(TrainingClient.api_url, TrainingClient.endpoints["train_endpoint"])
        params = dict(params)
        response : Response = self._get_external_call(url = url, request_body=params)
        return self._handle_response(url=url,response=response)

        
    def test_endpoint(self, params : TestParams) -> Response:
        self.logger.debug(f"POINTCLOUD TRAINING INFERENCE API Communication: Test Model")

        url: str = os.path.join(TrainingClient.api_url, TrainingClient.endpoints["test_endpoint"])
        params = dict(params)
        response : Response = self._get_external_call(url = url, request_body=params)

        if response.status_code != 200:
            self.logger.error(f"Pointcloud Training Inference API GET Request {url} failed! {response.text}")
            raise ClientException(additional_info=response.text)
        return response.json()
    
    def infer_endpoint(self, params : InferParams) -> Response:
        self.logger.debug(f"POINTCLOUD TRAINING INFERENCE API Communication: Test Model")

        url: str = os.path.join(TrainingClient.api_url, TrainingClient.endpoints["infer_endpoint"])
        params = dict(params)
        response = self._get_external_call(url = url, request_body=params)

        if response.status_code != 200:
            self.logger.error(f"Pointcloud Training Inference API GET Request {url} failed! {response.text}")
            raise ClientException(additional_info= "")
        return response.json()
    
    def stop_endpoint(self, params : StopParams) -> Response:
        self.logger.debug(f"POINTCLOUD TRAINING INFERENCE API Communication: Test Model")

        url: str = os.path.join(str(TrainingClient.api_url), TrainingClient.endpoints["stop_training_endpoint"])
        params = dict(params)
        response = self._delete_external_call(url = url, request_body=params)

        if response.status_code != 200:
            self.logger.error(f"Pointcloud Training Inference API GET Request {url} failed! {response.text}")
            raise ClientException(additional_info=response.text)
        return response.json()
    
    def rename_endpoint(self, params : RenameParams) -> Response:
        self.logger.debug(f"POINTCLOUD TRAINING INFERENCE API Communication: Test Model")

        url: str = os.path.join(str(TrainingClient.api_url), TrainingClient.endpoints["rename_training_endpoint"])
        params = dict(params)
        response = self._patch_external_call(url = url, request_body=params)

        if response.status_code != 200:
            self.logger.error(f"Pointcloud Training Inference API GET Request {url} failed! {response.text}")
            raise ClientException(additional_info=response.text)
        return response.json()
    
    def status_endpoint(self) -> Response:
        self.logger.debug(f"POINTCLOUD TRAINING INFERENCE API Communication: Test Model")

        url: str = os.path.join(str(TrainingClient.api_url), TrainingClient.endpoints["status_endpoint"])
        response = self._get_external_call(url = url, request_body=None)

        if response.status_code != 200:
            self.logger.error(f"Pointcloud Training Inference API GET Request {url} failed! {response.text}")
            raise ClientException(additional_info=response.text)
        return response.json()    
        
    # helper endpoints
    def get_available_gpu(self):
        response = requests.get(os.path.join(TrainingClient.api_url, TrainingClient.endpoints["gpus_endpoint"]))
        if response.status_code != 200:
            self.logger.error(f'Pointcloud Training Inference API GET Request {TrainingClient.endpoints["gpus_endpoint"]} failed! {response.text}')
            raise ClientException(additional_info=response.text)
        gpus = response.json()
        gpus_list = []
        for gpu in gpus:
            gpus_list.append(gpu)
        return gpus_list

    def get_files_endpoint(self, url : str):
        configs = []
        response = self._get_external_call(url = url, request_body=None)
        if response.status_code == 200:
            configs_json = json.loads(response.text)
        else:
            raise ClientException(additional_info=response.text)

        for i in range(len(configs_json)):
            configs.append(configs_json[i])

        return configs

    def find_clean_datasets_available(self):
        datasets = []
        response = self._get_external_call(url= os.path.join(str(TrainingClient.api_url),str(TrainingClient.endpoints["dataset_endpoint"])), request_body=None)
        self.logger.debug(os.path.join(str(TrainingClient.api_url), TrainingClient.endpoints["dataset_endpoint"]))
        if response.status_code == 200:
            self.logger.debug(f"Pointcloud Training Inference API GET Request successful: {response.text}")
            datasets_json = json.loads(response.text)
        else:
            self.logger.error(f"Pointcloud Training Inference API GET Request failed! {response.text}")
            raise ClientException(additional_info=response.text)
        
        for i in range(len(datasets_json)):
            datasets.append(datasets_json[i]["name"])

        return datasets

    def find_dataset_configs(self):
        dataset_configs = self.get_files_endpoint(os.path.join(TrainingClient.api_url, TrainingClient.endpoints["dataset_config_files_endpoint"]))

        return dataset_configs

    def find_training_configs(self):
        training_configs = self.get_files_endpoint(os.path.join(TrainingClient.api_url, TrainingClient.endpoints["training_config_files_endpoint"]))

        return training_configs

    def retrieve_available_trains(self):
        response = self._get_external_call(url = os.path.join(TrainingClient.api_url, TrainingClient.endpoints["status_endpoint"]), request_body=None)
        if response.status_code == 200:
            self.logger.debug(f"Pointcloud Training Inference API GET Request successful: {response.text}")
        else:
            self.logger.error(f"Pointcloud Training Inference API GET Request failed! {response.text}")
            raise ClientException(additional_info=response.text)
        json_data = json.loads(response.text)
        uuids = []
        training_names = []
        available_training_names = []
        available_training_uuids = []
        for train in json_data:
            uuids.append(train["uuid"])
            training_names.append(train["training_name"])
            if train["progress"] == 100:
                available_training_uuids.append(train["uuid"])
                available_training_names.append(train["training_name"])
            
        return {"uuid": uuids, "training_names" : training_names, "available_training_names": available_training_names}

    def retrieve_pcd_inference_files(self) -> List:
        return self.get_files_endpoint(os.path.join(TrainingClient.api_url, TrainingClient.endpoints["list_pcd_inference_files_endpoint"]))
    
    def change_url_port(self, url : str, port : int):
        """
        Set global URL, PORT, and endpoints of API of all clients
        """

        TrainingClient.url = url
        TrainingClient.port = port  
        TrainingClient.api_url = url + ":" + str(port)
        