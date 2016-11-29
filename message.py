from flywheel import Model, Field, STRING, NUMBER
from flywheel.fields.types import ListType


class Message(Model):
    id = Field(data_type=STRING, hash_key=True)
    total_parts = Field(data_type=NUMBER)
    parts = Field(data_type=ListType)
    message_sent = Field(data_type=NUMBER)

    def __init__(self, id, total_parts):
        super(Message, self).__init__()
        self.id = id
        self.parts = [None] * int(total_parts)
        self.message_sent = 0

