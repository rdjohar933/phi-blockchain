from dataclasses import dataclass
from dataclasses_json import dataclass_json
import datetime



@dataclass_json
@dataclass
class Transaction:
    sender: str
    receiver: str
    amount: float
