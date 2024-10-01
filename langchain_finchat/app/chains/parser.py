from langchain_core.pydantic_v1 import BaseModel, Field

class IntentOutputParser(BaseModel):
    answer: str = Field(description="outputformat")
    sql: str = Field(description="outputformat")