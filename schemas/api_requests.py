from pydantic import BaseModel

class JournalEntryRequest(BaseModel):
    user_id: str
    text: str
