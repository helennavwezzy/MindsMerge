import atexit

import envy
from libs.base_driver import BaseGraphDatabase


class SocialGraphDB(BaseGraphDatabase):
    def _create_constraints(self):
        with self.session() as session:
            session.run(
                """
                CREATE CONSTRAINT username_unique IF NOT EXISTS
                FOR (u:User)
                REQUIRE u.name IS UNIQUE
                """
            )
            session.run(
                """
                CREATE CONSTRAINT user_email_unique IF NOT EXISTS
                FOR (u:User)
                REQUIRE u.email IS UNIQUE
                """
            )
            session.run(
                """
                CREATE CONSTRAINT post_id_unique IF NOT EXISTS
                FOR (p:Post)
                REQUIRE p.id IS UNIQUE
                """
            )
            session.run(
                """
                CREATE CONSTRAINT comment_id_unique IF NOT EXISTS
                FOR (c:Comment)
                REQUIRE c.id IS UNIQUE
                """
            )
            session.run(
                """
                CREATE CONSTRAINT topic_name_unique IF NOT EXISTS
                FOR (t:Topic)
                REQUIRE t.name IS UNIQUE
                """
            )

    def close(self):
        self._driver.close()


driver = SocialGraphDB(
    uri=envy.NEO4J_URI,
    username=envy.NEO4J_USERNAME,
    password=envy.NEO4J_PASSWORD,
)

atexit.register(driver.close)
