import omni.ui as ui
import omni
from typing import List, Dict
from aipipeline.pc.inference.infrastructure.clients.training_client import TrainingClient
from aipipeline.pc.inference.utils.helper_functions import *

class ApiConfig:
    api_url : str = None
    port : int = None
    def __init__(self, name: str, url:str, port:int):
        self.name: str = name
        self.url: str = url
        self.port: int = port
        

class APIConfigUI:
    def __init__(self, client : TrainingClient):
        self.list_new_configs: Dict = {}
        self.list_configs: Dict = {}
        self.list_config_names: List[str] = []
        self.client: TrainingClient = client
        url, port, _ = get_default_url_port_endpoint()
        self.config: ApiConfig = ApiConfig(name = "default", url=url, port=port)
        self.configs_ui: ui.ComboBox = None

    def build_ui(self):

        def show_configs():
            """
            Show configs available in clients.json
            """
            manager = omni.kit.app.get_app().get_extension_manager()
            ext_id = manager.get_enabled_extension_id("aipipeline.pc.inference")
            ext_path = manager.get_extension_dict(ext_id)["path"]
            with open(os.path.join(ext_path, "config/clients.json"), "r") as f: 
                json_data = json.load(f)

                for config in json_data["api_connectors"]:
                        url = json_data["api_connectors"][config]["url"]
                        port = json_data["api_connectors"][config]["port"]
                        self.list_config_names.append(config)

                        new_config = ApiConfig(name = config, url=url, port=port)
                        self.list_configs.update({new_config.name :{"url": new_config.url, "port" : new_config.port}})
            return self.list_configs
    
        def save_config():
            """
            Saves configuration in list_configs, updates the combobox ui, and writes the config to clients.json 
            """
            self.list_new_configs: Dict = {}
            name: str = name_ui.model.get_value_as_string()
            url: str = url_ui.model.get_value_as_string()
            port: int = port_ui.model.get_value_as_int()

            if name and url and port:
                new_config: ApiConfig = ApiConfig(name = name, url=url, port=port)
                self.list_config_names.append(name)
                self.list_new_configs.update({new_config.name :{"url": new_config.url, "port" : new_config.port}})
                self.list_configs.update({new_config.name :{"url": new_config.url, "port" : new_config.port}})
                
                # Remove old contents of ui.ComboBox
                items = self.configs_ui.model.get_item_children()
                for item in items:
                    self.configs_ui.model.remove_item(item)
                # Retrieve new training names available by sending a get request from the client
                for name in self.list_configs:
                    # Update ComboBox
                    self.configs_ui.model.append_child_item(None, ui.SimpleStringModel(name)) 

                write_config(self.list_new_configs)
            else:
                # If user forgets one of the inputs, don't do anything and send a message
                self.status_label.style = {"color" : ui.color(255,0,0)}
                self.status_label.text = "Enter config name, api url, and port number"
        
        def change_config(*args):
            """
            Retrieve configuration selected from drop down box and create a client instance with that configuration
            """
            option = register_option(self.configs_ui, self.list_config_names)
            option_get = self.list_configs.get(option)
            self.config = ApiConfig(name = option, url=option_get["url"], port=option_get["port"])
            self.client.change_url_port(url=self.config.url, port=self.config.port)
            self.status_label.text = f"Changed config to: {self.config.name}, {self.config.url}, {self.config.port}"
            self.status_label.style = {"color": ui.color(0,255,0)}

        def write_config(list_configs : dict):
            """
            Write config to config/clients.json
            """

            # Obtain path of extension
            manager = omni.kit.app.get_app().get_extension_manager()
            ext_id = manager.get_enabled_extension_id("aipipeline.pc.inference")
            ext_path = manager.get_extension_dict(ext_id)["path"]

            # Write new config in clients.json
            with open(os.path.join(ext_path, "config/clients.json"), 'r+') as file:
                # First we load existing data into a dict.
                file_data = json.load(file)
                # Join new_data with file_data inside emp_details
                file_data["api_connectors"].update(list_configs)
                # Convert back to json.
                file.seek(0)
                json.dump(file_data, file, indent=4) 

        def delete_config():
            """
            Delete currently selected configuration from clients.json
            """
            manager = omni.kit.app.get_app().get_extension_manager()
            ext_id = manager.get_enabled_extension_id("aipipeline.pc.inference")
            ext_path = manager.get_extension_dict(ext_id)["path"]
            option = register_option(self.configs_ui, self.list_config_names)

            self.list_config_names.remove(option)
            items = self.configs_ui.model.get_item_children()
            for item in items:
                self.configs_ui.model.remove_item(item)


            # Retrieve updated training names available by sending a get request from the client
            for name in self.list_config_names:
                # Update ComboBox
                self.configs_ui.model.append_child_item(None, ui.SimpleStringModel(name))
            with open(os.path.join(ext_path, "config/clients.json"), 'r+') as file:
                # First we load existing data into a dict.
                file_data = json.load(file)
                # Delete selected config
                file_data["api_connectors"].pop(str(option))
                # Convert back to json.
                file.seek(0)
            
        with ui.VStack(height=30):
            with ui.HStack(width = 800):
                ui.Label("Name of Config", style = {"color" : ui.color(200, 162, 200)})
                name_ui = ui.StringField()
            ui.Separator(height=20)

            with ui.HStack(width = 800):
                ui.Label("Enter API URL", style = {"color" : ui.color(200, 162, 200)})
                url_ui = ui.StringField()
            ui.Separator(height=20)

            with ui.HStack(width = 800):
                ui.Label("Enter Port Number", style = {"color" : ui.color(200, 162, 200)})
                port_ui = ui.StringField()
            ui.Button("Add Config", clicked_fn = save_config, width = 500)
            
            with ui.HStack(width=700):
                label = ui.Label("Select Config:", style = {"color" : ui.color(200, 162, 200)})
                self.configs_ui = ui.ComboBox(0, *show_configs())
                ui.Button(f"{get_reset_glyph()}", width =20, clicked_fn = delete_config, tooltip = "Delete config")
                self.configs_ui.model.add_item_changed_fn(change_config)
            self.status_label: ui.Label = ui.Label(f"Current config is: {self.client.api_url}")