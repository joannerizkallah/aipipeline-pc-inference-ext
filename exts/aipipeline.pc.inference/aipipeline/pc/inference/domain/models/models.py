from pydantic import BaseModel

class TrainingParams(BaseModel):
    training_name : str
    dataset_path : str
    training_config_file_path : str
    dataset_config_file_path : str
    resume_training : bool
    gpu_id : int


class TestParams(BaseModel):
    training_name : str
    dataset_path : str
    dataset_config_file_path : str
    gpu_id : int


class InferParams(BaseModel):
    point_cloud_path : str
    training_name: str

class StopParams(BaseModel):
    uuid : str
    delete_logs : bool

class RenameParams(BaseModel):
    uuid : str
    new_training_path : str

class StatusUuidParams(BaseModel):
    uuid: str

