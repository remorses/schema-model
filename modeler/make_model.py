from .support import fallback, merge, resolve_refs, silent
import fastjsonschema
import json


def make_model(
        schema: dict,
        name: str = 'Model',
        uri: str = '',
        store: dict = {},
        # immutable: bool = False,
    ):
    """
    import yaml

    schema = yaml.load(open('types/model.yml').read())

    Model = make_model(
        schema=schema,
        immutable=True,
        # set_defaults=True # if schema has a default and property is not presetn it will use the default value
    )
    """
    # if not schema:
    #     raise Exception('schema is needed to instantiate a model')

    uri = uri or schema.get('$id', '')

    schema = resolve_refs(schema, uri, store=store)

    if schema.get('type', '') == 'object':
        schema['title'] = schema.get('title', '') \
            .replace(' ','_') \
            .replace('.','_') \
            .replace('/','_') \
            .replace('-','_') or name


    # print('schema', schema)

    switch = {
        'object':  make_object,
        'array':   make_array,
        'number':  make_number,
        'integer':  make_number,
        'string':  make_string,
        'boolean': make_boolean,
    }

    data_types = merge_types(schema)

    # print(data_types)

    maker = fallback(
        *[(lambda: switch[data_type](schema), TypeError) for data_type in data_types],
        lambda: lambda x: x
    )
    # print(maker)

    return maker


def merge_types(schema):
    types = []

    schemas = schema.get('anyOf', []) or \
        schema.get('allOf', []) or \
        schema.get('oneOf', []) or \
        [schema]

    for schema in schemas:
        if 'type' in schema:
            types += [schema['type']]

        elif any(x in schema for x in ('allOf', 'anyOf', 'oneOf')):
            types += merge_types(schema)

    return list(set(types))



make_string = lambda schema: lambda value: value

make_number = lambda schema: lambda value: value

make_boolean = lambda schema: lambda value: value

make_array = lambda schema: \
    lambda value: fallback(
        (lambda: [make_model(schema.get('items', {}))(**v) for v in value], TypeError),
        (lambda: [make_model(schema.get('items', {}))(v) for v in value],TypeError),
    )



def format_slots(self):
    return f"({', '.join([str(k) + '=' + str(self[k]) for k in [*self.__slots__, *self.__additional__.keys()] if k in self])})"


class Meta(type):
    def __new__(cls, name, bases, dct):
        dct.update({'__slots__': list(dct.get('_schema', {}).get('properties', {}).keys())})
        validate = fastjsonschema.compile(dct.get('_schema', {}))
        dct.update({'_validate': lambda self: validate(self._serialize())})
        x = super().__new__(cls, name, bases, dct)
        return x


class Model(metaclass=Meta):

    __metaclass__ = Meta

    __setattr__ = lambda self, name, v: object.__setattr__(self, name, v) if name in self.__slots__  \
        else self.__additional__.__setitem__(name, v)

    __getattribute__ = lambda self, name: fallback(
        lambda: object.__getattribute__(self, name,),
        lambda: self.__additional__.get(name)
    )

    __delattr__ = lambda self, name: object.__delattr__(self, name,) if name in self.__slots__  \
        else self.__additional__.__delitem__(name)

    __setitem__ = __setattr__

    __getitem__ = __getattribute__

    __delitem__ = __delattr__

    __repr__ = lambda self: f'{self.__class__.__name__}{format_slots(self)}'

    __iter__ = lambda self: iter((*[x for x in self.__slots__ if x in self], *[y for y in self.__additional__ ]))

    __contains__ = lambda self, x: (x in self.__slots__ or x in self.__additional__) and \
        (silent(lambda: self[x])() or self.__additional__.get(x, False))


    _schema = {}

    __additional__ = {}

    __slots__ = tuple()

    _compiled = lambda: None

    def __init__(self, **kwargs):

        # print('__slot__', self.__slots__)
        # print('_schema', self._schema)

        schema = self._schema

        print(kwargs)

        properties = schema.get('properties', {})

        for k, v in kwargs.items():
                fallback(
                    (lambda: setattr(self, k, make_model(schema=properties.get(k, {}))(**v)), TypeError),
                    (lambda: setattr(self, k, make_model(schema=properties.get(k, {}))(v)), TypeError),
                )
                print(k)
        print(self.__additional__)

    def _validate(self):
        self._compiled(self._serialize())

    #     raise Exception(f'{k} is not in properties, can\' instantaite the Model')

    def _serialize(self):
        result = dict()
        for slot in self:
            result[slot] = self[slot]._serialize() if hasattr(self[slot], '_serialize') else self[slot]
        return result

    def _json(self):
        return json.dumps(self._serialize(), indent=2)



def merge_properties(schema):
    properties = {}

    schemas = schema.get('anyOf', []) or \
        schema.get('allOf', []) or \
        schema.get('oneOf', []) or \
        [schema]

    for schema in schemas:
        if 'properties' in schema:
            for k, v in schema['properties'].items():
                properties = merge(properties, {k:v})
    return properties

make_object = lambda schema: type(
    schema.get('title', 'Object'),
    (Model,),
    {
        '__slots__': tuple(merge_properties(schema).keys()),
        '_schema': schema,
    },
)
