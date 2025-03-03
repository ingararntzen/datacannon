from src.server.db_mysql import MysqlDB
from src.server.db_sqlite import SqliteDB
from collections import OrderedDict


class ItemsService:

    def __init__(self, config):
        if config["db_type"] == "mysql":
            self._db = MysqlDB(config)
        elif config["db_type"] == "sqlite":
            self._db = SqliteDB(config)
        # this service does not include old state in diffs
        self.oldstate_included = False

    def get(self, app, chnl):
        return list(self._db.get_all(app, chnl))

    def replace(self, app, chnl, insert_items):
        # clear
        self._db.clear(app, chnl)
        # insert
        self._db.insert(app, chnl, insert_items)
        return insert_items

    def update(self, app, chnl, remove_ids, insert_items):
        # remove
        if remove_ids:
            self._db.remove(app, chnl, remove_ids)
        # insert
        if insert_items:
            self._db.insert(app, chnl, insert_items)
        # diffs
        diffs = OrderedDict()
        for _id in remove_ids:
            diffs[_id] = {"id": _id, "new": None}
        for item in insert_items:
            _id = item["id"]
            diffs[_id] = {"id": _id, "new": item}

        # return list of diffs
        return list(diffs.values())


def get_service(config):
    return ItemsService(config)
