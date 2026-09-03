from enum import Enum
from typing import Any, List
import json
import jsonpickle
from datetime import datetime

class SerializableEnum(Enum):

    # factory method to be used when deserializing
    @classmethod
    def create(cls, source:Any):
        return cls.from_string(source) if isinstance(source, str) else source

    @classmethod
    def from_string(cls, string: str):
        for v in cls:
            if str(v.value) == string:
                return v
        return None

    def __getstate__(self) -> dict:
        return str(self.value)

class UriRefEnum(SerializableEnum):
    """Enum base class for URIRef entries.

    Upon deserialization, tries to replace prefixes if any,
    to correctly match the value.

    Subclasses must provide '_prefixes' and '_namespace' to actually match them correctly.
    They might optionaly set '_serialize_with_prefix' to True, which will serialize using
    the first prefix.

    WARNING: Prefixes are matter of JSON-LD context, so they might changed based on the implementation.
    Use with caution.
    """
    @classmethod
    def _prefixes(cls) -> List[str]:
        return []

    @classmethod
    def _namespace(cls) -> str:
        return None

    # whether to serialize using prefix or full URI
    # when set to True, _prefixes must not be empty, only the first prefix is used
    # default is False - use full URI
    @classmethod
    def _serialize_with_prefix(cls) -> bool:
        return False

    @classmethod
    def from_string(cls, string: str):
        prefixes = cls._prefixes()
        if len(prefixes) and cls._namespace():
            for prefix in prefixes:
                if string.startswith(f"{prefix}:"):
                    return super().from_string(
                        string.replace(f"{prefix}:", cls._namespace(), 1)
                    )
        return super().from_string(string)

    def __getstate__(self) -> dict:
        ret = str(self.value)
        cls = self.__class__
        if cls._serialize_with_prefix and len(cls._prefixes()) and cls._namespace():
            ret = ret.replace(cls._namespace(), f"{cls._prefixes()[0]}:")
        return ret

class SerializableObject:

    # objects can define properties to json keys mapping
    # which is used in serialization and deserialization as well
    # this is a class property, so shared across all instances of the same class
    props_to_json_keys = {}

    # objects can define properties which will not be serialized and deserialized
    props_to_ignore = []

    # if to serialize atributes with None values to resulting JSON
    # default is False
    SERIALIZE_NULLS = False

    def __init__(self) -> None:
        pass

    def __str__(self):
        # the complicated expression is to represent dictionary values with str() method
        # cause default in python is with repr() which won't print the nested objects nicely
        return f"<{self.__class__.__name__}:" + " {%s}"%', '.join("%r: %s"%p for p in self.__dict__.items()) + ">"

    # factory method to be used when deserializing
    # source may be string representation of JSON, or dictionary representation of the object
    # or the object instance itself (for easier constructors of the objects)
    @classmethod
    def create(cls, source:Any):
        if isinstance(source, cls):
            return source
        if isinstance(source, str):
            source = json.loads(source)
        return cls.from_dictionary(source) if isinstance(source, dict) else None

    # this must be used to created instances of data classes when deserializing from json dictionaries
    @classmethod
    def from_dictionary(cls, d: dict):
        fixed = d.copy()
        to_delete = []
        for k,v in cls.props_to_json_keys.items():
            if v in fixed:
                fixed[k] = fixed[v]
                to_delete.append(v)
        # combine with props to ignore..
        to_delete.extend(cls.props_to_ignore)

        for k in to_delete:
            if k in fixed: del fixed[k]

        return cls(**fixed)

    def __getstate__(self) -> dict:
        state = dict(self.__dict__)
        keys_to_remove = []
        for k, v in self.__class__.props_to_json_keys.items():
            if k in state:
                state[v] = state[k]
                keys_to_remove.append(k)

        if not self.__class__.SERIALIZE_NULLS:
            for k, v in state.items():
                if v is None and k not in keys_to_remove:
                    keys_to_remove.append(k)

        # combine keys to remove with ignore list
        keys_to_remove.extend(self.__class__.props_to_ignore)

        for k in keys_to_remove:
            if k in state: del state[k]

        return state

class DatetimeHandler(jsonpickle.handlers.BaseHandler):
    def flatten(self, obj, data):
        ret = obj.isoformat(timespec='milliseconds').replace("+00:00", "Z")
        return ret
    def restore(self, obj):
        return datetime.fromisoformat(obj)

jsonpickle.handlers.registry.register(datetime, DatetimeHandler)
