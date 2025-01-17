import json
import os
from typing import Dict, Optional
import logging

from gpt_index.storage.kvstore.types import (
    DEFAULT_COLLECTION,
    BaseInMemoryKVStore,
)


logger = logging.getLogger(__name__)

DATA_TYPE = Dict[str, Dict[str, dict]]


class SimpleKVStore(BaseInMemoryKVStore):
    """Simple in-memory Key-Value store.

    Args:
        persist_path (str): path to persist the store

    """

    def __init__(self, data: Optional[DATA_TYPE] = None) -> None:
        """Init a SimpleKVStore."""
        self._data: DATA_TYPE = data or {}

    def put(self, key: str, val: dict, collection: str = DEFAULT_COLLECTION) -> None:
        """Put a key-value pair into the store."""
        if collection not in self._data:
            self._data[collection] = {}
        self._data[collection][key] = val.copy()

    def get(self, key: str, collection: str = DEFAULT_COLLECTION) -> Optional[dict]:
        """Get a value from the store."""
        collection_data = self._data.get(collection, None)
        if not collection_data:
            return None
        if key not in collection_data:
            return None
        return collection_data[key].copy()

    def get_all(self, collection: str = DEFAULT_COLLECTION) -> Dict[str, dict]:
        """Get all values from the store."""
        return self._data.get(collection, {}).copy()

    def delete(self, key: str, collection: str = DEFAULT_COLLECTION) -> bool:
        """Delete a value from the store."""
        try:
            self._data[collection].pop(key)
            return True
        except KeyError:
            return False

    def persist(self, persist_path: str) -> None:
        """Persist the store."""
        dirpath = os.path.dirname(persist_path)
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)

        with open(persist_path, "w+") as f:
            json.dump(self._data, f)

    @classmethod
    def from_persist_path(cls, persist_path: str) -> "SimpleKVStore":
        """Load a SimpleKVStore from a persist path."""
        if not os.path.exists(persist_path):
            raise ValueError(f"No existing {__name__} found at {persist_path}.")

        logger.debug(f"Loading {__name__} from {persist_path}.")
        with open(persist_path, "r+") as f:
            data = json.load(f)
        return cls(data)
