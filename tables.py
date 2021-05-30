from sqlalchemy import MetaData, Table, Column, String, DateTime


metadata = MetaData()


def create_tables(engine):
    metadata.create_all(engine)


class Community(object):
    table = Table(
        'communities', metadata,
        Column('id', String(50), primary_key=True),
    )

    def __init__(self, engine):
        self.engine = engine

    def update_communities(self, communities):
        self.engine.execute(self.table.delete())
        self.engine.execute(self.table.insert(), [{'id': x}
                                                  for x in communities])


class ActivityLog(object):
    table = Table(
        'activity_log', metadata,
        Column('incident', String(50), primary_key=True),
        Column('incident_dt', DateTime()),
        Column('nature', String(50)),
        Column('address', String(50)),
        Column('community', String(50)),
    )

    def __init__(self, engine):
        self.engine = engine

    def add_new(self, activities):
        self.engine.execute(self.table.insert(), activities)
