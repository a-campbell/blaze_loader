import blaze as bz

from sqlalchemy import select
import json

import os
from weakref import WeakKeyDictionary


class LazyAttr(object):

    def __init__(self, get):
        self._get = get
        self._cache = WeakKeyDictionary()

    def __get__(self, instance, owner):
        if instance is None:

            return self
        try:
            return self._cache[instance]
        except KeyError:
            self._cache[instance] = val = self._get(instance)
            return val


def load(db_info_path=None):
    class _quanto_blaze(object):

        db_infos = load_infos_from_json(db_info_path=db_info_path)
        locals_ = locals()

        for name, db_info in db_infos.iteritems():
            @LazyAttr
            def _lazyattr(self, _name=name, _db_info=db_info):
                db = _db_info.get('db')
                table = _db_info.get('table')
                schema = _db_info.get('schema', None)
                datashape = _db_info.get('datashape', None)
                columns = _db_info.get('columns', None)

                try:
                    bz_data = _add_blaze_data(_name,
                                              db,
                                              table,
                                              schema=schema,
                                              datashape=datashape,
                                              columns=columns)

                    return bz_data
                except Exception:
                    raise AttributeError(
                        "Could not load {}. Check your connection info"
                        "to make sure you have the creds you need."
                        .format(_name))

            locals_[name] = _lazyattr

            del _lazyattr
            del name
            del db_info

    return _quanto_blaze()


def print_db_infos():
    db_infos = load_infos_from_json()
    dbs = []
    for k, v in db_infos.iteritems():
        db_str = str(k) + ": " + str(v['table'])
        dbs.append(db_str)

    dbs_str = "\n".join(dbs)
    return "databases loaded: \n" + dbs_str


def _add_blaze_data(name, db, table, schema=None,
                    datashape=None, columns=None):
    resource = make_blaze_resource(db, table, schema)
    bz_data = make_blaze_data_obj(resource, columns, datashape)

    return bz_data


def save_blaze_infos(name, db, table, schema=None,
                     datashape=None, columns=None):
        db_infos = load_infos_from_json()

        new_info_dict = {
            'db': db,
            'table': table,
            'schema': schema,
            'datashape': datashape,
            'columns': columns
        }

        db_infos[name] = new_info_dict

        _write_infos_to_json(db_infos)
        print( name + ": " + str(new_info_dict) + " SAVED")


def _write_infos_to_json(db_infos):
    location = os.path.realpath(os.path.join(os.getcwd(),
                                os.path.dirname(__file__)))
    f_path = location + "/databases.json"
    with open(f_path, 'wb') as f:
        json.dump(db_infos, f)


def load_infos_from_json(db_info_path=None):
    try:
        if db_info_path is None:
            location = os.path.realpath(os.path.join(os.getcwd(),
                                        os.path.dirname(__file__)))
            db_info_path = location + "/databases.json"

        with open(db_info_path, 'rb') as f:
            db_infos = json.load(f)
    except:
        print( "Warning: No saved databases found.")
        db_infos = {}

    return db_infos


def make_blaze_resource(db, table, schema):
    hs_s = getattr(host_settings, db)
    conn_str = hs_s + "::" + table

    t = bz.resource(conn_str, schema=schema)

    return t


def make_blaze_data_obj(resource, columns, datashape):
    if columns is not None:
        s = []
        for col in columns:
            s.append(resource.c[col])
        data = select(s)
    else:
        data = resource

    bz_data = bz.Data(data, dshape=datashape)

    return bz_data
