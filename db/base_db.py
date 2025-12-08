# Interface (abstract class)
# db/base_db.py

from abc import ABC, abstractmethod

class BaseDB(ABC):
    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def execute(self, query: str):
        """
        Execute a query.
        Returns: dict with keys:
            - success (bool)
            - rows (list of dict)
            - columns (list of str)
            - error (str, if any)
        """
        pass

    @abstractmethod
    def get_schema(self):
        """
        Returns a dict representation of the DB schema.
        Example:
        {
            "customers": ["id", "name", "email"],
            "orders": ["id", "customer_id", "amount"]
        }
        """
        pass
