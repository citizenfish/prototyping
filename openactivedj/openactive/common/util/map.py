from dateutil.parser import parse as dparse
import pytz
import re
from jsonpath_ng.ext import parse
from functools import reduce


def openactive_item_mapper(**kwargs):
    r = kwargs.get('item')
    mappings = kwargs.get('mappings')
    org = kwargs.get('org')
    kind = r.get('kind', 'errors')
    record = {}

    try:
        kind = kind.lower()  # to cope with Event, event etc...
        # to cope with scheduledsession.sessionseries or facilityuse/slot etc...
        kind = re.split(r'[^a-zA-Z]', kind)[0]
    except Exception as error:
        kind = 'errors'

    # Only deal with kinds that are registered in mappings
    if kind not in mappings:
        return None, None

    state = r.get('state')

    # No point mapping deleted records
    if state == 'deleted':
        return kind, {'oa_org': org, 'oa_id': r.get('id'), 'published': False, 'state': 'deleted',
                      'modified': int(r.get('modified')), 'rawdata': r}

    # Map incoming data to our schema

    model_map = mappings[kind]
    if model_map:

        for key, value in model_map.items():

            if key == 'model':
                continue

            # Enter json packet stored for debug
            if key == 'rawdata' and value == '*':
                record[key] = r
                continue

            # 'oa_org' = 'f{{variable}}' or oa_org = 'fixed value'
            if isinstance(value, str):
                record[key] = eval(f"f'{value}'")

            # 'title': {'paths': ['title', 'data.title'], 'default' : ''}
            elif isinstance(value, dict) and 'paths' in value:
                val = None
                for path in value['paths']:
                    try:
                        # jsonpath
                        if path[0] == '$':
                            jp = parse(path)
                            val = [match.value for match in jp.find(r)]
                        else:
                            # standard key1.key2.key3 method
                            keys = path.split('.')
                            val = reduce(lambda acc, i: acc[i], keys, r)
                        if val:
                            break
                    except (KeyError, TypeError):
                        pass

                # Carry out any type conversions
                if 'type' in value:
                    record[key] = cnv(val, value['type'])
                else:
                    record[key] = val

                # Set defaults as last resort
                if record[key] is None and 'default' in value:
                    record[key] = value['default']

            # Fixed numerics
            elif isinstance(value, int) or isinstance(value, float):
                record[key] = value

            # Nothing found
            else:
                record[key] = None

    return kind, record


def cnv(item, type):
    type_map = {
        'int': int,
        'float': float,
        'str': str,
    }

    # Boolean checks can work on None values
    if type == 'exists':
        if item:
            return True
        return False

    # No point doing anything if there's no data
    if item is None:
        return None

    # Force a specific type
    if type in type_map:
        try:
            return type_map[type](item)
        except ValueError:
            return None
        except TypeError:
            return None

    # Convert to an array
    elif type == 'array':
        if isinstance(item, list):
            return item
        elif isinstance(item, (str, int, float)):
            return [item]
        else:
            return []

    # Pick the first item in an array and return as a value
    elif type == 'array_first':
        if isinstance(item, list):
            return item[0]

    # Convert date/time strings to a date, if many are returned then choose the first
    elif type == 'datetime' or type == 'time':
        if isinstance(item, (str, list)):
            item = item[0] if isinstance(item, list) and len(item) > 0 else None if isinstance(item, list) else item

            if item:
                try:
                    parsed_date = dparse(item)

                    if parsed_date.tzinfo is None:
                        parsed_date = parsed_date.replace(tzinfo=pytz.UTC)

                    if type == 'time':
                        return parsed_date.time()

                    return parsed_date

                except ValueError:
                    pass

    return None


def insert_blocks(model_map, reusable_blocks):
    for model, fields in model_map.items():
        for block_key in reusable_blocks:
            if block_key in fields:
                block = reusable_blocks[block_key]
                fields.update(block)
                del fields[block_key]
