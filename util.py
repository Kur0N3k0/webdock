from flask_pymongo import pymongo

def deserialize_json(cls=None, data=None):
    if data == None:
        return None
        
    if isinstance(data, list):
        r = []
        for item in data:
            instance = object.__new__(cls)
            for key, value in item.items():
                setattr(instance, key, value)
            r += [instance]
        return r
    elif isinstance(data, pymongo.cursor.Cursor):
        cursor: pymongo.cursor.Cursor = data
        r = []
        for i in range(cursor.count()):
            instance = object.__new__(cls)
            for key, value in cursor.next():
                setattr(instance, key, value)
            r += [instance]
        return r
    else:
        instance = object.__new__(cls)
        for key, value in data.items():
            setattr(instance, key, value)

        return instance