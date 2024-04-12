import omni.ui as ui
from typing import List, Dict
import omni.kit.notification_manager as nm
import re
import pandas as pd
from omni.kit.window.popup_dialog import InputDialog
from aipipeline.pc.inference.utils.helper_functions import *
from aipipeline.pc.inference.infrastructure.clients.training_client import TrainingClient
from aipipeline.pc.inference.utils.training_info import *
from aipipeline.pc.inference.domain.models.models import StopParams, RenameParams

class Status:
    def __init__(self, client: TrainingClient, refresh: callable):
        self.client: TrainingClient = client
        self.refresh = refresh
        
    def search(self, search_bar, *args):
        """
        Use regex patterns to filter out statuses and update the ui
        """
        TrainingInfo.reset_ui_to_display()
        previous_result: List = []
        prompt: str = search_bar.model.get_value_as_string()
        split: List = prompt.split(":")
        new_split: List = []
        for part in split:
            subpart = part.split()
            for word in subpart:
                new_split.append(word)
        
        if not len(new_split)%2==0:
            return
        for key in TrainingInfo.get_keys():            
            for i in range(0,len(new_split),2): # Jump 2 each time to correctly get key and value from split list
                
                search_key_result: str = ""
                result: str = ""
                search_key_result = re.findall(f"(?i)({key})", new_split[i]) # Retrieve the corresponding key from the prompt
                if search_key_result: # If the key exists in the dataframe
                    new_split[i] = search_key_result[0].lower() # Lower case key in split just for neatness
                    new_df = TrainingInfo.df.set_index(key)
                    result = new_df.filter(regex=f"(?=.*{str(new_split[i+1])}).*$",axis=0)
                    if not result.empty: # If the value exists in the dataframe, append to TrainingInfo.ui_to_display list
                        current_result: List = []
                        for _, row in result.iterrows(): # For every training containing eg. gpu_id: 1, update the ui_to_display list
                            # Check if this condition is already in the entries_to_display list. If it is not, then there are no results that satisfy the conditions in the prompt
                            if key == "uuid":
                                uuid = row.name
                            else:
                                uuid = row["uuid"]
                            current_result.append(uuid)
                        for uuid in current_result:
                            if len(previous_result)==0:
                                continue
                            else:
                                if uuid not in previous_result:
                                    previous_result.remove(uuid)
                        previous_result=current_result
                                    
        # Display all trainings that match the search bar criteria
        for uuid in previous_result:
            TrainingInfo.append_ui_to_display(uuid)
        self.refresh()

    def build_ui(self):

        #def search(*args):
            

        def delete_logs_popup(uuid: str):
            ok_button = nm.NotificationButtonInfo("YES", on_complete= lambda: stop_training(uuid, True))
            cancel_button = nm.NotificationButtonInfo("NO", on_complete= lambda: stop_training(uuid, False))
            nm.post_notification(
                "Delete logs?",
                hide_after_timeout=False,
                duration=0,
                status=nm.NotificationStatus.INFO,
                button_infos=[ok_button, cancel_button],
            )

        def stop_training(uuid: str, delete_logs: bool):
            """
            Create stop training request
            """
            params: dict = {}
            params["delete_logs"] = delete_logs
            params["uuid"] = uuid
            api_params: StopParams = StopParams(**params)
            self.client.stop_endpoint(params=api_params)

            # Refresh UI
            self.refresh()

        def stop_popup(uuid: str):
            """
            Create UI popup to confirm if user wants to stop training
            """
            ok_button = nm.NotificationButtonInfo("YES", on_complete= lambda: delete_logs_popup(uuid))
            cancel_button = nm.NotificationButtonInfo("CANCEL", on_complete=None)
            nm.post_notification(
                "Are you sure you want to stop training?",
                hide_after_timeout=False,
                duration=0,
                status=nm.NotificationStatus.WARNING,
                button_infos=[ok_button, cancel_button],
            )

        def rename_popup(uuid: str):
            dialog = InputDialog(
                title="Rename Training",
                message="Please enter new training name: ",
                pre_label="New Name:  ",
                post_label="deep_cnn",
                ok_handler=lambda dialog: rename_training(uuid, dialog),
                )
            dialog.show()

        def rename_training(uuid: str, new_name: InputDialog):
            """
            Rename train by sending a PATCH request to client
            """
            params: Dict = {}
            params["new_training_path"] = new_name.get_value()
            params["uuid"] = uuid

            # Utilizing pydantic to pass parameters to client
            api_params: RenameParams = RenameParams(**params)

            # Create PATCH request
            self.client.rename_endpoint(params=api_params)
            new_name.hide()
            # Refresh UI
            self.refresh()

        def get_status_button():
            """
            Get statuses once button pressed
            """

            # Reset UI list to display
            TrainingInfo.reset_ui_to_display()

            # Create GET requestand update DataFrame that contains all trainings
            get_status()
            # Add uuids to TrainingInfo.ui_to_display
            for data in TrainingInfo.df.iterrows():
                uuid = data[1]["uuid"]
                if not uuid in TrainingInfo.get_ui_to_display():
                    TrainingInfo.append_ui_to_display(uuid)

            # Refresh UI
            self.refresh()

        def get_status():
            """
            Send GET request and update Dataframe containing all trainings
            """
            response_json = self.client.status_endpoint()
            search_table_result_df = pd.DataFrame.from_dict(response_json)
            TrainingInfo.get_trainings(search_table_result_df)

        # Update first dataframe containing all trainings to perform search properly
        get_status()
        # Build UI
        with ui.VStack(height=100):
            ui.Button("Get Status of Trainings", clicked_fn = get_status_button)
            with ui.HStack():
                ui.Label("Search: ", width=20)
                search_bar = ui.StringField(tooltip = "Search")
            ui.Button("Search", clicked_fn=lambda: self.search(search_bar))
            if not TrainingInfo.df.empty:
                for uuid in TrainingInfo.get_ui_to_display():
                    row = TrainingInfo.df.set_index("uuid").loc[uuid]
                    with ui.HStack():
                        ui.Label(row.to_string())    
                        status = TrainingInfo.df.set_index("uuid").loc[uuid].status
                        if status=="Done":
                            ui.Button("Delete Logs", clicked_fn=lambda: delete_logs_popup(uuid), height=40, width=120)
                        else:
                            ui.Button("Stop Training", clicked_fn = lambda: stop_popup(uuid), height =40, width=120)
                        ui.Button("Rename Training", clicked_fn = lambda: rename_popup(uuid), height =40, width=120) #, new_name
            


