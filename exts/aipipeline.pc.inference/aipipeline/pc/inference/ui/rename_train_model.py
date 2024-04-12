import omni.ui as ui
from aipipeline.pc.inference.utils.helper_functions import *
from aipipeline.pc.inference.infrastructure.clients.training_client import TrainingClient
from aipipeline.pc.inference.domain.models.models import RenameParams

class RenameTrain:

    def __init__(self, client : TrainingClient):
        
        self.params : dict = {
            "uuid" : None,
            "new_training_path" : None
        }

        self.response_label : ui.Label = None
        self.client : TrainingClient = client
    def build_ui(self):

        def refresh():
            """
            Refresh contents of drop down box
            """
            #Remove old contents of ui.ComboBox
            items = uuid_ui.model.get_item_children()
            for item in items:
                uuid_ui.model.remove_item(item)
            
            #Retrieve new training uuids available by sending a get request from the client
            available_trains = self.client.retrieve_available_trains()["uuid"]
            for uuid in available_trains:
                #Update ComboBox
                uuid_ui.model.append_child_item(None, ui.SimpleStringModel(uuid))

        def change_name():
            """
            Change name of training
            """
            
            #Assign parameters used in PATCH request
            self.params["new_training_path"] = new_training_path_ui.model.get_value_as_string()
            self.params["uuid"] = register_option(uuid_ui, self.client.retrieve_available_trains()["uuid"])

            #Utilizing pydantic to pass parameters to client
            api_params = RenameParams(**self.params)

            #Create PATCH request
            response = self.client.rename_endpoint(params=api_params)

            #Change label coloring according to response status code
            self.response_label.text = f"Successfully renamed training"
            self.response_label.style = {"color" : ui.color(0,255,0)}

        with ui.VStack(height = 12):
            with ui.HStack(height = 10, width = 1000):
                ui.Label("Enter uuid")
                uuid_ui : ui.ComboBox = ui.ComboBox(0, *self.client.retrieve_available_trains()["uuid"])

                ui.Button(f"{get_reset_glyph()}", width =20, clicked_fn = refresh, tooltip = "Refresh names")
            with ui.HStack(height = 10, width =1000):
                ui.Label("Enter new training path")
                new_training_path_ui : ui.StringField = ui.StringField()

            self.response_label = ui.Label("")
            ui.Button("Rename Training Logs Directory", clicked_fn = change_name)
