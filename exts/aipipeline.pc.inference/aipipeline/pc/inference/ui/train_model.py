import omni.ui as ui
from typing import List, Dict
from aipipeline.pc.inference.utils.helper_functions import *
from aipipeline.pc.inference.infrastructure.clients.training_client import TrainingClient
from aipipeline.pc.inference.domain.models.models import TrainingParams

class TrainModel:

    def __init__(self, client : TrainingClient):
        self.resume_options: List = ["--", False, True]
        self.params: Dict = {
            "training_name" : None,
            "dataset_path" : None,
            "training_config_file_path" : None,
            "dataset_config_file_path" : None,
            "resume_training" : None,
            "gpu_id" : None
        }
        self.client: TrainingClient = client
        
    def build_ui(self):

        def refresh_gpus():
            refresh_gpu_id(gpu_id_ui, self.client)

        def refresh_dataset_config_ui():
            refresh_file_paths(dataset_config_file_path_ui, self.client.find_dataset_configs)
        
        def refresh_training_config_ui():
            refresh_file_paths(training_config_file_path_ui, self.client.find_training_configs)

        def refresh_clean_datasets_ui():
            refresh_file_paths(dataset_path_ui, self.client.find_clean_datasets_available)

        def run_train_endpoint():
            """
            Run training endpoint according to values from comboboxes and intfield
            """
            # Assign parameters used in get requests
            self.params["training_name"] = training_name_ui.model.get_value_as_string()
            self.params["gpu_id"] = register_option(gpu_id_ui, self.client.get_available_gpu())
            self.params["dataset_path"] = register_option(dataset_path_ui, self.client.find_clean_datasets_available())
            self.params["training_config_file_path"] = register_option(training_config_file_path_ui, self.client.find_training_configs())
            self.params["dataset_config_file_path"] = register_option(dataset_config_file_path_ui, self.client.find_dataset_configs())
            self.params["resume_training"] = register_option(resume_training_ui, self.resume_options)

            # Utilizing pydantic to pass parameters to client
            api_params: TrainingParams = TrainingParams(**self.params)
            response_json: json = self.client.train_endpoint(params = api_params)

            # Change label coloring according to response status code
            training_response_label.text = present_output(response_json=response_json)
            training_response_label.style = {"color": ui.color(0, 255, 0)}

        with ui.VStack(height=10):

            ui.Label("Training Name", style={"color": ui.color(200, 162, 200)})
            training_name_ui: ui.StringField = ui.StringField()

            ui.Label("Dataset Path (relative to datasets/clean/)", style = {"color": ui.color(200, 162, 200)})
            with ui.HStack(height=10, width=1000):
                dataset_path_ui: ui.ComboBox = ui.ComboBox(0, *self.client.find_clean_datasets_available())
                ui.Button(f"{get_reset_glyph()}", width =20, clicked_fn = refresh_clean_datasets_ui, tooltip = "Refresh datasets")
                
            ui.Label("Training Config File Path (relative to config_files/training_config/)", style = {"color" : ui.color(200,162,200)})
            with ui.HStack(height=10, width=1000):
                training_config_file_path_ui: ui.ComboBox = ui.ComboBox(0, *self.client.find_training_configs())
                ui.Button(f"{get_reset_glyph()}", width=20, clicked_fn = refresh_training_config_ui, tooltip = "Refresh training configs")
            
            ui.Label("Dataset Config File Path (relative to config_files/dataset_config/)", style = {"color" : ui.color(200,162,200)})
            with ui.HStack(height=10, width=1000):
                dataset_config_file_path_ui : ui.ComboBox = ui.ComboBox(0, *self.client.find_dataset_configs())
                ui.Button(f"{get_reset_glyph()}", width =20, clicked_fn = refresh_dataset_config_ui, tooltip = "Refresh dataset configs")

            ui.Label("Resume Training Option", style = {"color" : ui.color(200,162,200)})
            with ui.HStack(height=10, width=1000):
                resume_training_ui: ui.ComboBox = ui.ComboBox(0, "--", "False", "True")

            ui.Label("GPU ID", style = {"color" : ui.color(200,162,200)})
            with ui.HStack(height=10, width=100):
                gpu_id_ui: ui.ComboBox = ui.ComboBox(0, *self.client.get_available_gpu())
                ui.Button(f"{get_reset_glyph()}", width =20, clicked_fn = refresh_gpus, tooltip = "Refresh GPUs available")

            ui.Button("Run Training", clicked_fn = run_train_endpoint) 
            training_response_label: ui.Label = ui.Label("", style={"color": ui.color(200, 162, 200)})