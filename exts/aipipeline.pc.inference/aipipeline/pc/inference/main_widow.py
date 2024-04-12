import omni.ui as ui
import logging
from aipipeline.pc.inference.infrastructure.clients.training_client import TrainingClient
from aipipeline.pc.inference.ui.api_config import APIConfigUI
from aipipeline.pc.inference.ui.multiple_pointcloud_inference import MultiplePointcloudInference
from aipipeline.pc.inference.utils.helper_functions import *
from aipipeline.pc.inference.ui.status_fetcher import Status
from aipipeline.pc.inference.ui.test_model import Test
from aipipeline.pc.inference.ui.train_model import TrainModel

class MainWindow(ui.Window):
    def __init__(self, title: str = None, **kwargs):
        super().__init__(title, **kwargs)
        self.logger: logging = logging.getLogger("Main Logger")
        self.client: TrainingClient = TrainingClient(*get_default_url_port_endpoint())
        self.frame.set_build_fn(self._build_window)

    def refresh(self):
        self.frame.rebuild()

    def _build_window(self):
        config_menu = APIConfigUI(self.client)
        train_model_menu = TrainModel(self.client)
        inference_multiple_menu = MultiplePointcloudInference(self.client)
        test_menu = Test(self.client)
        status_menu = Status(self.client, self.refresh) #, self.refresh

        with ui.ScrollingFrame():
            with ui.VStack():
                with ui.CollapsableFrame("Configuration", height=20):
                    with ui.Frame():
                        config_menu.build_ui()
                with ui.CollapsableFrame("Train", height=20):
                    with ui.Frame():
                        train_model_menu.build_ui()
                with ui.CollapsableFrame("Infer Multiple PCDS", height=20): 
                        inference_multiple_menu.build_ui()
                with ui.CollapsableFrame("Test", height=20): 
                    with ui.Frame():
                        test_menu.build_ui()
                with ui.CollapsableFrame("Status", height=100):
                        status_menu.build_ui()
                    
    def on_shutdown(self):
        pass