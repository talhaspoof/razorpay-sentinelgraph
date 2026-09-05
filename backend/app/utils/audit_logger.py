import json
import hashlib
import time
import os
from typing import Dict, Any, List

class CryptographicAuditLogger:
    """
    Immutable, hash-chained audit logger for all AI risk decisions and actions.
    Every log entry contains the SHA-256 hash of the previous log entry,
    ensuring tamper-evident compliance for fintech audits.
    """
    def __init__(self, log_path: str = "audit_trail.jsonl"):
        self.log_path = log_path
        self._prev_hash = "0" * 64
        self._in_memory_logs: List[Dict[str, Any]] = []
        self._init_hash()

    def _init_hash(self):
        if os.path.exists(self.log_path):
            try:
                with open(self.log_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    if lines:
                        last_entry = json.loads(lines[-1].strip())
                        self._prev_hash = last_entry.get("entry_hash", self._prev_hash)
            except Exception:
                pass

    def log_event(self, event_type: str, details: Dict[str, Any], actor: str = "SentinelAI_Agent") -> Dict[str, Any]:
        timestamp = time.time()
        
        payload_to_hash = {
            "timestamp": timestamp,
            "event_type": event_type,
            "actor": actor,
            "details": details,
            "prev_hash": self._prev_hash
        }
        
        serialized = json.dumps(payload_to_hash, sort_keys=True)
        current_hash = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
        
        log_entry = {
            **payload_to_hash,
            "entry_hash": current_hash
        }
        
        self._prev_hash = current_hash
        self._in_memory_logs.append(log_entry)
        
        # Append to persistent file
        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception:
            pass
            
        return log_entry

    def get_recent_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self._in_memory_logs[-limit:]

audit_logger = CryptographicAuditLogger()
