import blaze as bz

from sqlalchemy import select
import json

import os


class LazyAttr(object):
    def __init__(self, get):
        self._get = get
        self._cache = {}

    def __get__(self, instance, owner):
        if instance is None:
            return self
        try:
            return self._cache[instance]
        except KeyError:
            val = self._get(instance)
            self._cache[instance] = val

            return val


def load(target_info_path=None, config=None):
    class _blaze_loader(object):
        target_infos = _load_infos_from_json(target_info_path=target_info_path)
        locals_ = locals()

        for name, target_info in target_infos.iteritems():
            @LazyAttr
            def _lazyattr(self, _name=name, _target_info=target_info, 
                          config=config):
                target = _target_info.get('target')
                table = _target_info.get('table')
                schema = _target_info.get('schema', None)
                datashape = _target_info.get('datashape', None)
                columns = _target_info.get('columns', None)

                try:
                    bz_data = _add_blaze_data(_name,
                                              target,
                                              table=table,
                                              schema=schema,
                                              datashape=datashape,
                                              columns=columns,
                                              config=config)

                    return bz_data

                except Exception:
                    raise AttributeError(
                        "Could not load {}. Check your connection info"
                        "to make sure you have the creds you need."
                        .format(_name))

            locals_[name] = _lazyattr

            del _lazyattr
            del name
            del target_info

        def __str__(self):
            target_infos = _load_infos_from_json()
            targets = []
            for k, v in target_infos.iteritems():
                target_str = str(k) + ": " + str(v['target'])
                if v['table'] is not None:
                    target_str += " " + str(v['table'])
                targets.append(target_str)

            targets_str = "\n".join(targets)
            return "databases loaded: \n" + targets_str

    return _blaze_loader()



def _add_blaze_data(name, target, table=None, schema=None,
                    datashape=None, columns=None, config=None):
    resource = _make_blaze_resource(target, table=table,
                                    schema=schema, config=config)
    bz_data = _make_blaze_data_obj(resource, columns=columns,
                                   datashape=datashape)

    return bz_data


def save_blaze_infos(name, target, table=None, schema=None,
                     datashape=None, columns=None, target_info_path=None):
        target_infos = _load_infos_from_json()

        new_info_dict = {
            'target': target,
            'table': table,
            'schema': schema,
            'datashape': datashape,
            'columns': columns
        }

        target_infos[name] = new_info_dict

        _write_infos_to_json(target_infos, target_info_path=target_info_path)
        print(name + ": " + str(new_info_dict) + " SAVED")


def _write_infos_to_json(target_infos, target_info_path=None):
    if target_info_path is None:
        location = os.path.realpath(os.path.join(os.getcwd(),
                                    os.path.dirname(__file__)))
        target_info_path = location + "/databases.json"

    with open(target_info_path, 'wb') as f:
        json.dump(target_infos, f)


def _load_infos_from_json(target_info_path=None):
    try:
        if target_info_path is None:
            location = os.path.realpath(os.path.join(os.getcwd(),
                                        os.path.dirname(__file__)))
            target_info_path = location + "/databases.json"

        with open(target_info_path, 'rb') as f:
            target_infos = json.load(f)
    except:
        print("Warning: No saved databases found.")
        target_infos = {}

    return target_infos


def _make_blaze_resource(target, table=None, schema=None,
                         config=None):
    if config is not None:
        conn_str = getattr(config, target)
    else:
        conn_str = target

    if table is not None:
        conn_str = conn_str + "::" + table

    t = bz.resource(conn_str, schema=schema)

    return t


def _make_blaze_data_obj(resource, columns=None, datashape=None):
    if columns is not None:
        s = []
        for col in columns:
            s.append(resource.c[col])
        data = select(s)
    else:
        data = resource

    bz_data = bz.Data(data, dshape=datashape)

    return bz_data
