from flywheel import Model, Field, STRING, STRING_SET, NUMBER


class Message(Model):
    id = Field(data_type=STRING, hash_key=True)
    total_parts = Field(data_type=NUMBER)
    parts = Field(data_type=STRING_SET)

    def __init__(self, total_parts):
        super(Message, self).__init__()
        self.parts = [None] * total_parts
