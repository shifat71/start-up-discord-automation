 
from discord import Attachment
from dataclasses import dataclass, field
from typing import Literal


# Define status icons and corresponding messages
status_icons = {
        "approved": "✅ Approved",
        "rejected": "❌ Rejected",
        "pending": "🔄 Pending Approval"
    }

@dataclass
class Transaction:
    amount: int
    type: Literal["IN", "OUT"]
    description: str
    status: Literal["approved", "rejected", "pending"] = "pending"
    proof: Attachment = None