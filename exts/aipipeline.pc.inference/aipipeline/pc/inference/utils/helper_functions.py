import json
import omni
import omni.ui as ui
import os
from aipipeline.pc.inference.infrastructure.clients.training_client import TrainingClient


def register_option(ui_model : ui.ComboBox, options : list):
    """
    Record options from a ui.ComboBox
    """
    value_model = ui_model.model.get_item_value_model()
    current_index = value_model.as_int
    option = options[current_index]
    return option

def present_output(response_json : str) -> str:
    """
    Present output of response in a clean way
    """
    output = ""
    for data in response_json:
        output += f"{data}: {response_json[data]}"
        output += "\t"

    return output

def get_reset_glyph() -> ui:
    """
    Get reset glyph (icon) for reset buttons
    """
    return ui.get_custom_glyph_code("${glyphs}/menu_refresh.svg")

def get_delete_glyph() -> ui:
    url : str = ""
    endpoints : dict = {}
    port : int = 0

    manager = omni.kit.app.get_app().get_extension_manager()
    ext_id = manager.get_extension_id_by_module("aipipeline.pc.inference")
    ext_path = manager.get_extension_dict(ext_id)["path"]
    path = os.path.join(ext_path, "config/trash.svg") # ask anthony
    return ui.get_custom_glyph_code(path)

def refresh_gpu_id(gpu_ui : ui, client: TrainingClient):
    """
    Refresh GPU IDs
    """
    #Remove old contents of ui.ComboBox
    items = gpu_ui.model.get_item_children()
    for item in items:
        gpu_ui.model.remove_item(item)
    #Retrieve new training names available by sending a get request from the client

    available = client.get_available_gpu()
    if len(available)==0:
        return
    
    for id in available:
        #Update ComboBox
        gpu_ui.model.append_child_item(None, ui.SimpleIntModel(int(id)))

def refresh_file_paths(ui_entity : ui, retrieve_fn : callable):
    """
    Refresh either training configs or dataset configs 
    """
    # Remove old contents of ui.ComboBox
    items: omni.ui = ui_entity.model.get_item_children()
    for item in items:
        ui_entity.model.remove_item(item)
    # Retrieve new training names available by sending a get request from the client
    available: callable = retrieve_fn()
    for name in available:
        # Update ComboBox
        ui_entity.model.append_child_item(None, ui.SimpleStringModel(name))

def parse_response_json(response_json : json) -> str:
    """
    Parse responses
    """
    output : str = ""
    for train in response_json:
        for data in train:
            output += f"{data} : {train[data]}"
            output += "\t"
        output += "\n"
    return output

def get_default_url_port_endpoint():
    """
    Get default API URL
    """
    url : str = ""
    endpoints : dict = {}
    port : int = 0

    manager = omni.kit.app.get_app().get_extension_manager()
    ext_id = manager.get_extension_id_by_module("aipipeline.pc.inference")
    ext_path = manager.get_extension_dict(ext_id)["path"]
    with open(os.path.join(ext_path, "config/clients.json"), "r") as f: 
            json_data = json.load(f)
            endpoints = json_data["endpoints"]
            url = json_data["api_connectors"]["Default Configuration"]["url"]
            port = json_data["api_connectors"]["Default Configuration"]["port"]
    
    return [url, port, endpoints]
        
def pretty_output(data):
    """
    Make output neat
    """
    output: str = ""
    for label in data:
        output += str(label) + "\t"
    return output