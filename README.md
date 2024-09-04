# Description

`JsonFlexConfig` allows for configuration management based on metadata describing all the parameters to be used. The configuration is stored in a JSON file as a set of key/value pairs that associates each parameter's name to its value. Once loaded (and if the configuration file is valid), the `JsonFlexConfig` object can be queried for the value of a parameter (if not present, a default value can be returned instead). The parameter values can be modified, and the new values can be stored back in the configuration file (only if explicitly requested). Sub-parameters with specific validation rules can be nested in parameters, allowing for sophisticated file structure.

Compared to more advanced configuration management libraries like Pydantic, this class offers a similar level of interaction with configuration files, but it is limited to handling JSON format. However, it provides a concise and highly readable declaration of standard rules within a single structure defined directly in the code without requiring external files. This approach avoids certain common complexities found in more advanced libraries, such as the potential need to define multiple subclasses in some cases or manage separate configuration files. While tools like Pydantic excel with their implementation of custom validators and support for various formats, which can be particularly useful in complex scenarios, this class is tailored for standard validation needs, making it a practical choice for simpler applications. Nonetheless, it maintains a high level of sophistication in validation with standard rule definitions, typically exceeding that of `ConfigParser` (at least when using it out of the box).


# General rules

A `JsonFlexConfig` object requires metadata that describes the expected format of the configuration file. This is a dictionary, associating a parameter's name to a format description. A format description is again a dictionary of all the rules applying to the parameter:
 * "type" (`type`):
   Parameter type. This must be the actual Python type. Any type is accepted, but only the following types provide type-specific rules validation: `int`, `float`, `list`, and `dict`.
 * "mandatory" (`bool`):
   If defined and set to `True`, the parameter has to be defined and not `None` in the configuration file.
 * "default" (object of type "type", optional):
   Only for non-mandatory parameters. If set, requesting for a parameter not in the configuration file will return the default value instead of `None`.
 * "values" (`list` of "type" objects, optional):
   List of all authorized values.
 * "label" (`str`):
   String describing the parameter, for display purposes.


Type-specific rules
===================
When dealing with list parameters, a few other rules can be applied:
 * "content_type" (`type`):
   Type of the items in the list. This key must be associated with the Python type. This means that it's not possible to store different types of objects in a single list (but dictionaries do allow this).
 * "size" (`int`, optional):
   number of objects in the list.

When dealing with numeric parameters (ìnt`or `float`), a few other rules
can be applied:
 * "min" (`int` or `float`, optional):
   Minimum value of the parameter.
 * "max" (`int` or `float`, optional):
   Maximum value of the parameter.
Note that defining a `float` parameter and providing an `int` bound is perfectly valid, since Python allows value comparision between those types.

When dealing with dictionary parameters, additional rules can be applied:
 * "content":
   A dictionary defining the rules for each sub-parameter within the dictionary. This allows for nested structures, where each sub-parameter can have its own validation rules, including type, mandatory status, and other constraints. This "content" section is a metadata description of sub-parameters that follows the same structure as the general metadata. It allows for nesting parameters with arbitrary depth, thus making dictionaries the most versatile structure for parameter management in
   `JsonFlexConfig`.


# Additional rules

In addition to these parameters, the metadata file can also define other parameters, which will be ignored by the parser and can take arbitrary forms, making them useful for extending this library's functions (for example, specifying widget type and attributes in order to automate the creation of the corresponding widget).


# Exceptions

When loading a configuration file or writing data to a configuration file, the following exception can be raised in case of invalid configuration data:
 * `BadNameException`: Raised when writing a param name not defined in the metadata
 * `BadValueTypeException`: Raised when a param value type is wrong
 * `MissingMandatoryException`: Raised when a mandatory param is missing
 * `ValueOutOfRangeException`: Raised when a param digital value is out of range
 * `UnauthorizedValueException`: Raised when a param digital value is not in the set of authorized values
 * `BadListTypeException`: Raised when a list param contains values of wrong type
 * `BadListSizeException`: Raised when a tuple param size is wrong
 * `InexistentParamException`: Raised when reading a param that is doesn't exist in the configuration data


# Example

Here is an example that creates metadata, loads a configuration file using the defined structure, and manipulates parameter values:
```python
configMetadata = {
    "database_path" : {
        "type": str,
        "mandatory": True,
        "label": "Path to the database",
        "ui": "DirPicker" #ignored by the parser
    },
    "lists": {
        "type": dict,
        "content": {
            "query": {
                "type": str,
                "mandatory": True
            },
            "type": {
                "type": str,
                "mandatory": True,
                "values": ("smart", "static")
            }
        },
        "label": None
    },
    'ui_language': {
        "type": str,
        "label": "Drive-In language",
        "default": "en",
        "values":["en", "fr"],
        "ui": "Select" #ignored by the parser
    }
}
manager = JsonFlexConfig(configMetadata)
manager.LoadConfig("my_config_file.json")

print(manager.GetParamValue("database_path")")
manager.SetParamValue("lists", {}) # erases the content of "lists"
manager.SaveConfig()
```

Applying this code to the following JSON file:
```json
{
    "database_path": "./db",
    "lists": {
        "All": {
            "query": "select *",
            "type": "smart"
        },
        "SF, Fantasy": {
            "query": "select * where genre='125'",
            "type": "smart"
        },
        "MCU": {
            "query": "1542",
            "type": "static"
        }
    }
}
```

displays:
```
./db
```

and replaces the content of "lists" with an empty dictionary.But with this JSON file, it doesn't work:
```json
{
    "database_path": "./db",
    "lists": {
        "All": {
            "query": "select *",
            "type": "smart"
        },
        "SF, Fantasy": {
            "query": "select * where genre='125'",
            "type": "smart"
        },
        "MCU": {
            "query": "1542"
        }
    }
}
```

Because the sub-parameter `lists.MCU` misses the parameter `type` which is mandatory according to the metadata. Loading this JSON file thus raises a
`MissingMandatoryException` with message:
```
Parameter error: missing mandatory "type" from "lists.MCU"
```
