import omni.ext
import omni.ui as ui
from aipipeline.pc.inference.main_widow import MainWindow

# Any class derived from `omni.ext.IExt` in top level module (defined in `python.modules` of `extension.toml`) will be
# instantiated when extension gets enabled and `on_startup(ext_id)` will be called. Later when extension gets disabled
# on_shutdown() is called.
class AipipelinePointcloudInferenceExtension(omni.ext.IExt):
    # ext_id is current extension id. It can be used with extension manager to query additional information, like where
    # this extension is located on filesystem.
    def __init__(self):
        super().__init__()
        self._window = None

    def on_startup(self, ext_id):
        print("[aipipeline.pc.inference] pointcloud training inference api startup")
        self._window = MainWindow(title = "Pointcloud Training and Inference API Pipeline")


    def on_shutdown(self):
        if self._window:
            self._window.on_shutdown()
            self._window.destroy()
            self._window =  None