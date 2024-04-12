import omni.ui as ui
from typing import List, Dict
from aipipeline.pc.inference.infrastructure.clients.training_client import TrainingClient
from aipipeline.pc.inference.utils.helper_functions import *
from aipipeline.pc.inference.domain.models.models import *

class MultiplePointcloudInference:

    def __init__(self, client : TrainingClient):

        self.params: Dict = {
            "point_cloud_path": None, 
            "training_name": None
        }
        self.list_pcd: List[str] = []
        self.list_checkboxes: List[ui.CheckBox.model]= []
        self.valid_params: bool = False
        self.client: TrainingClient = client

    def build_ui(self):


        def register_training_name():
            """
            Register training name from training name ui using helper function register option for ui.ComboBox
            """
            self.params["training_name"] = register_option(training_name_ui, self.client.retrieve_available_trains()["training_names"])

        
        def evaluate():
            """
            Perform multiple inferences on a list of pointclouds
            """
            register_training_name()
            if self.params["training_name"]:
                for box in self.list_checkboxes:
                    if box[0].as_bool:
                        self.list_pcd.append(box[1])
                for pcd in self.list_pcd:
                    self.params["point_cloud_path"] = pcd
                    api_params = InferParams(**self.params)
                    info_label.text = ""
                    self.client.infer_endpoint(params=api_params)
                if len(self.list_pcd)==0:
                    info_label.text = "Select at least one PCD"
                    info_label.style = {"color" : ui.color(255,0,0)}
                    return
                info_label.text = "Evaluating training"
                info_label.style = {"color" : ui.color(0,255,0)}
            else:
                info_label.text = "Make sure to pick a training name"
                info_label.style = {"color" : ui.color(255,0,0)}

        with ui.VStack():

            ui.Label("Training Name", style = {"color" : ui.color(200, 162, 200)})
            with ui.HStack(width=600):
                training_name_ui: ui.ComboBox = ui.ComboBox(0, *self.client.retrieve_available_trains()["training_names"])
                ui.Button(f"{get_reset_glyph()}", width =20, clicked_fn = refresh_file_paths(training_name_ui, lambda: self.client.retrieve_available_trains()["training_names"]), tooltip = "Refresh names")

            with ui.HStack(height=10, width=1300):
                list_pcd: List = self.client.retrieve_pcd_inference_files()
            for pcd in list_pcd:
                with ui.VStack():
                    with ui.HStack(width=600):
                        ui.Label(str(pcd), style = {"color" : ui.color(200, 0, 200)})
                        checkbox: ui.CheckBox = ui.CheckBox(width=100)
                        self.list_checkboxes.append([checkbox.model, pcd])
            with ui.VStack():
                ui.Button("Evaluate", clicked_fn = evaluate)
                info_label: ui.Label = ui.Label("", style={"color": ui.color(255, 255, 0)})