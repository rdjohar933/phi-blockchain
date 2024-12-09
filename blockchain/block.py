import hashlib
import json
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, config
from datetime import datetime
from marshmallow import fields

from transaction import Transaction


@dataclass_json
@dataclass
class Block:
    index: int
    timestamp: float
    proof: int
    previous_hash: str
    transactions: list[Transaction]

#make get_hash incensitive to order of transactions
    def get_hash(self):
        serialized_block = self.to_json(sort_keys=True)
        encoded_block = serialized_block.encode()
        return hashlib.sha256(encoded_block).hexdigest()

