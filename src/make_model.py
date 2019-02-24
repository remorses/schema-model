from .support import fallback


def make_model(
    schema: dict,
    name: str = 'Model',
    immutable: bool = False,
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
    schema['title'] = shema.get('title').replace(' ','_') or name

    switch = {
        'object': lambda: make_object(schema),
        'array': lambda: make_array(schema),
        'number': lambda: make_number(schema),
        'string': lambda: make_string(schema),
        'boolean': lambda: make_boolean(schema),
    }
    
    switch[schema.get('type')]()
    



make_string = lambda schema: lambda value: string_validation(schema, value) and str(value)

make_number = lambda schema: lambda value: number_validation(schema, value) and value

make_boolean = lambda schema: lambda value: number_validation(schema, value) and value

make_object = lambda schema: type(
    schema.get('title', 'Object'),
    (Object,),
    make_object_attributes(schema),
)

def make_object_attributes(schema):
    schema = schema.get('anyOf', {}) or \
        schema.get('allOf', {}) or \
        schema.get('oneOf', {}) or \
        schema
        
    properties = schema.get('properties', {}) 
    required = schema.get('required', ())
    
    return {
        '__slots__': tuple(properties.keys()),
        '_properties': properties,
        '_required': required,
    }

make_array = lambda schema: \
    lambda value: array_validation and \
    fallback(
        lambda: [make_model(schema.get('items', {}))(**v) for v in value],
        lambda: [make_model(schema.get('items', {}))(v) for v in value],
    )()


def number_validation(schema, value):
    if not isinstance(v, int) and not isinstance(v, float):
        raise ValueError(
                'The attribute "{0}" must be an int or float, but was "{1}"'.format(k, type(value)))
    
    return True

def string_validation(schema, value):
    if type_ == 'string' and not isinstance(v, str):
        raise ValueError('The attribute "{0}" must be a string, but was "{1}"'.format(k, type(value)))
    
    return True
        

def boolean_validation(schema, value):
    if type_ == 'boolean' and not isinstance(v, bool):
        raise ValueError('The attribute "{0}" must be an int, but was "{1}"'.format(k, type(value)))
    
    return True


def array_validation(schema, value):

    if not isinstance(value, (list, tuple,)):
        raise ValueError('The attribute "{0}" must be an array, but was "{1}"'.format(k, type(value)))
    
    return True


def object_validation(schema, **kwargs):
        
    for k, v in kwargs.items():
    
        if k not in properties:
            raise ValueError(
                    'The model "{0}" does not have an attribute "{1}"'.format(self.__class__.__name__, k))
                    
    for key in schema.get('required', []):
        if key not in kwargs:
            raise ValueError('The attribute "{0}" is required'.format(key))

            
    return True

    
class Object:
	
	__setitem__ = object.__setattr__
	
	__getitem__ = object.__getattribute__ 
	
	__delitem__ = object.__delattr__
	
	__slots__ = tuple()
    
    _schema = {}

    def __init__(self, *, **kwargs):
        
        schema = self._schema
        
        assert object_validation(schema, value)
        
        properties = schema.get('properties', {})
        
        for k, v in kwargs.items():
                        
            fallback(
                lambda: setattr(self, k, make_model(schema=properties[k])(**v)),
                lambda: setattr(self, k, make_model(schema=properties[k])(v)),
            )()
            
            
        
                
                
