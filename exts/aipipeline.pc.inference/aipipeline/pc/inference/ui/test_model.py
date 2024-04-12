import omni.ui as ui
from typing import Dict
from aipipeline.pc.inference.utils.helper_functions import *
from aipipeline.pc.inference.infrastructure.clients.training_client import TrainingClient
from aipipeline.pc.inference.domain.models.models import TestParams

class Test:
    def __init__(self, client: TrainingClient):
        self.params: Dict = {
            "training_name" : None,
            "dataset_path" : None,
            "dataset_config_file_path" : None,
            "gpu_id" : None
        }
        self.client: TrainingClient = client
    def build_ui(self):
        
        def test():
            """
            Test training on pointcloud dataset
            """
            #Assign parameters used in GET request
            self.params["dataset_path"] = register_option(dataset_path_ui, self.client.find_clean_datasets_available())
            self.params["dataset_config_file_path"] = register_option(dataset_config_file_path_ui, self.client.find_dataset_configs())
            self.params["training_name"] = register_option(training_name_ui, self.client.retrieve_available_trains()["training_names"])
            self.params["gpu_id"] = register_option(gpu_id_ui, self.client.get_available_gpu())

            #Utilizing pydantic to pass parameters to client
            api_params: TestParams = TestParams(**self.params)

            #Create GET request
            response_json: json = self.client.test_endpoint(params = api_params)

            #Change label coloring 
            self.response_text.text = present_output(response_json)
            self.response_text.style = {"color": ui.color(0, 255, 0)}


        with ui.VStack(height = 10):

            ui.Label("Training Name", style = {"color" : ui.color(200,162,200)})
            with ui.HStack(height=10,width=1000):
                training_name_ui: ui.ComboBox = ui.ComboBox(0, *self.client.retrieve_available_trains()["training_names"])
                ui.Button(f"{get_reset_glyph()}", width=20, clicked_fn = refresh_file_paths(training_name_ui, lambda: self.client.retrieve_available_trains()["training_names"]), tooltip = "Refresh names")
            
            ui.Label("Dataset Path (relative to datasets/clean)", style = {"color" : ui.color(200,162,200)})
            with ui.HStack(height=10,width=1000):
                dataset_path_ui: ui.ComboBox = ui.ComboBox(0, *self.client.find_clean_datasets_available())
                ui.Button(f"{get_reset_glyph()}", width=20, clicked_fn = refresh_file_paths(dataset_path_ui, self.client.find_clean_datasets_available), tooltip = "Refresh datasets")

            ui.Label("Dataset Config File Path (relative to config_files/dataset_config)", style = {"color" : ui.color(200,162,200)})
            with ui.HStack(height=10,width=1000):
                dataset_config_file_path_ui: ui.ComboBox = ui.ComboBox(0, *self.client.find_dataset_configs())
                ui.Button(f"{get_reset_glyph()}", width=20, clicked_fn = refresh_file_paths(dataset_config_file_path_ui, self.client.find_dataset_configs), tooltip = "Refresh dataset configs")

            ui.Label("GPU ID", style = {"color" : ui.color(200,162,200)})
            with ui.HStack(height=10,width=100):
                gpu_id_ui: ui.ComboBox = ui.ComboBox(0, *self.client.get_available_gpu())
                ui.Button(f"{get_reset_glyph()}", width=20, clicked_fn = refresh_gpu_id(gpu_id_ui, self.client), tooltip = "Refresh GPUs")

            ui.Button("Test Model on Dataset", clicked_fn = test)
            with ui.ScrollingFrame(height = 50):
                self.response_text: ui.Label = ui.Label("Testing results show up here")

