class Config:
    def __init__(self, project_id:str, inbox_label_id:str):
        self.project_id = project_id
        self.inbox_label_id = inbox_label_id

config = Config(project_id="blitzy-ocr-api", inbox_label_id="Label_4949462187849619681")