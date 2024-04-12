import pandas as pd

class TrainingInfo:
    ui_to_display: list= []
    df: pd.DataFrame = pd.DataFrame()

    def __init__(self):
        self.uuid = None
        self.gpu_id = None
        self.get_status = None
        self.training_name = None 
        self.status = None
        self.results_ready = None
        self.start_time = None
        self.end_time = None
    
    def get_keys():
        list = ["uuid", "gpu_id", "training_name", "status", "end_time", "start_time"]
        return list
    
    def get_ui_to_display():
        return TrainingInfo.ui_to_display
    
    def append_ui_to_display(item):
        TrainingInfo.ui_to_display.append(item)
    
    def remove_ui_display(item):
        TrainingInfo.ui_to_display.remove(item)
    
    def reset_ui_to_display():
        TrainingInfo.ui_to_display = []

    def get_trainings(search_table_result_df: pd.DataFrame):
        # If there are no statuses, show nothing and stop everything
        if search_table_result_df.empty:
            return
        # Record the desired keys only in the Status.df dataframe
        for key in TrainingInfo.get_keys():
            if key in search_table_result_df.columns:
                TrainingInfo.df[key] = search_table_result_df[key]
                if key=="gpu_id":
                    TrainingInfo.df[key] = search_table_result_df[key]
        # Make entries for end time and start time neat
        if TrainingInfo.df["end_time"][0]:
            time = TrainingInfo.df["end_time"][0].split('T')
            TrainingInfo.df["end_time"] = f"{time[0]}    {time[1]}"
        if TrainingInfo.df["start_time"][0]:
            time = TrainingInfo.df["start_time"][0].split('T')
            TrainingInfo.df["start_time"] = f"{time[0]}    {time[1]}"
