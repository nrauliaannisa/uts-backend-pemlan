from pydantic import BaseModel

class ProgressInput(BaseModel):
    pages_read_today: int

class TargetInput(BaseModel):
    target_days: int