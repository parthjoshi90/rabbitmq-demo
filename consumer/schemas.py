from pydantic import BaseModel

class Data(BaseModel):
    input: int
    output: int
    correlation_id: str