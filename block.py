import hashlib
from dataclasses import dataclass
from dataclasses_json import dataclass_json
import datetime


@dataclass_json
@dataclass
class Block:
    index: int
    timestamp: datetime.datetime
    proof: int
    previous_hash: str
    transactions: list

    def get_hash(self):
        serialized_block = self.to_json(sort_keys=True)
        encoded_block = serialized_block.encode()
        return hashlib.sha256(encoded_block).hexdigest()

