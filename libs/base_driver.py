from neo4j import GraphDatabase


class BaseGraphDatabase:
    def __init__(self, *, uri: str, username: str, password: str):
        self._driver = GraphDatabase.driver(uri, auth=(username, password))
        self._create_indexes()
        self._create_constraints()

    @property
    def session(self):
        return self._driver.session

    def close(self):
        self._driver.close()

    def _create_indexes(self):
        """Override this method to create custom indexes"""

    def _create_constraints(self):
        """Override this method to create custom constraints"""
