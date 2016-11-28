from flywheel import Model, Field, STRING, NUMBER

class Message(Model):
    id = Field(data_type=STRING, hash_key=True)
    total_parts = Field(data_type=NUMBER)
    parts = Field(data_type=LIST)

    def __init__(self, total_parts):
        parts = [None] * total_parts
