# Description

_JsonFlexConfig_ allows for the management of configurations based on metadata describing all the parameters to be used. The configuration data is stored in a JSON file as a set of key/value pairs associating the name of each parameter with its value. Once loaded (and if the configuration data is valid), the `JsonFlexConfig` object can be queried for the value of a parameter (if not present, a default value can be returned). Parameter values can be modified, and the new values stored in the configuration file (only if explicitly requested). Sub-parameters with specific validation rules can be nested within parameters, enabling a sophisticated file structure.

Compared with more advanced configuration management libraries such as Pydantic, _JsonFlexConfig_ offers a similar level of interaction with configuration files, but is limited to handling JSON format. However, it provides a concise and highly readable declaration of standard rules within a single Python structure, which can be defined directly in the code without the need for external files. This approach bypasses some of the common complexities found in more advanced libraries, such as the need to implement multiple functions or subclasses or manage separate configuration files in (yet) another format. While tools like Pydantic excel in enabling the implementation of custom validators and supporting a variety of formats, which can be particularly useful in complex scenarios, _JsonFlexConfig_ remains a practical choice for many applications. Despite its simplicity, _JsonFlexConfig_ offers a sophisticated level of validation through standard rule definitions, typically surpassing that of ConfigParser (at least in its default configuration). One can leverage these advanced features using only Python (and JSON of course), without the need for additional files in other formats or complex code structures.


# General usage

To use _JsonFlexConfig_, four steps must be applied:
 1. Create Validation Rules<br>
    Define a metadata dictionary that outlines the validation rules. This metadata describes aspects such as parameter types, whether they are mandatory or optional, default values, etc. These rules will be used to load and validate the data.
 2. Instantiate `JsonFlexConfig`<br>
    Create a `JsonFlexConfig` object using the previously defined metadata.
 3. Load and Validate Data<br>
    Open a JSON configuration file with the `JsonFlexConfig` object. Alternatively, data can be loaded directly from a Python dictionary, providing it has the same structure as the data a JSON parser would create. The JSON file must contain a dictionary where each key is a string representing a parameter name, and the corresponding value is that parameter's content. The data will be validated according to the rules defined in the metadata. If any rule fails validation, an exception will be raised.
 4. Access Configuration Data<br>
    Once the data is validated, access its content using the parameter names.


# Common rules

A `JsonFlexConfig` object requires metadata that describes the expected format of the configuration file. This is a dictionary, associating a parameter's name to a format description. A format description is again a dictionary of all the rules applying to the parameter. Six different type of rules can be defined, in the form of pairs of keys (a string containing the name of the rule type) / values (the rule itself):
 * `"type"` (`type`):<br>
   Parameter's type. This must be the actual Python type. Any type is accepted, but only the following types provide type-specific rules validation: `int`, `float`, `list`, `str`, and `dict`.
 * `"mandatory"` (`bool`):<br>
   If defined and set to `True`, the parameter has to be defined and not `None` in the configuration file. 
 * `"default"` (object of the same type as the value of `"type"`, optional):<br>
   Only for non-mandatory parameters. If set, requesting for a parameter not in the configuration file will return the default value instead of `None`. 
 * `"values"` (`list` of objects of the same type as the value of `"type"`, optional):<br>
   List of all authorized values. Any value not in this list will raise an exception. 
 * `"forbidden_values"` (`list` of objects of the same type as the value of `"type"`, optional):<br>
   List of all forbidden_values values. Any value in this list will raise an exception. 
 * `"label"` (`str`):<br>
   String describing the parameter, at the developer's disposal for display purposes.

# Type-specific rules

When dealing with list parameters, four other rules can be applied:
 * `"content"` (`type` or `dict`):<br>
   Type of the items in the list. If defined, every item in the list must be of this type. If the list contains scalar values, `"content"` must be set to their corresponding `type`. If the list contains sequences of sub-parameters, `"content"` must be a dictionary defining the type of every sub-parameters, following the same structure as the general metadata. This means that a list can only contain elements of the same type, whether a scalar or a sequence.
 * `"size"` (`int`, optional):<br>
   number of objects in the list.
 * `"minsize"` (`int`, optional):<br>
   minimum number of objects in the list.
 * `"maxsize"` (`int`, optional):<br>
   maximum number of objects in the list.
   
When dealing with dictionary parameters, one additional rule can be applied:
  * `"content"`:<br>
    A dictionary containing metadata description of sub-parameters. This dictionary must contain a list of keys associated with the specific rules applied to each key. These specific pairs of names/rules follow the same structure as the general metadata. Each sub-parameter within the dictionary can have its specific rules, including type, mandatory status, and other constraints.

When dealing with string parameters, four other rules can be applied:
  * `"regex"` (`str`, optional):<br>
    regular expression that the string must match (in the `re` format)
  * `"size"` (`int`, optional):<br>
    number of objects in the list.
  * `"minsize"` (`int`, optional):<br>
    minimum number of objects in the list.
  * `"maxsize"` (`int`, optional):<br>
    maximum number of objects in the list.

When dealing with numeric parameters (`int` or `float`), two additional rules can be applied:
 * `"min"` (`int` or `float`, optional):<br>
   Minimum value of the parameter.
 * `"max"` (`int` or `float`, optional):<br>
   Maximum value of the parameter.
   
Note that defining a `float` parameter and providing an `int` bound is perfectly valid, since Python allows value comparision between those types.

Important note: There is almost no verification done on the metadata, it's up to the user to ensure that it is correct. An error in metadata may lead to inconsistent behavior from _JsonFlexConfig_, for example if a value is at the same time in the list of authorized values and in the list of forbidden ones, or if a mandatory parameter has a default value. Mutually exclusive rules may also happen, for example if a `min` value is greater than a `max` value, or if a string size is incompatible with a RegEx.


# Additional metadata

In addition to these parameters, rules in the metadata file can also define other options, which will be ignored by the parser and can take arbitrary forms, making them useful for extending this library's functions (for example, specifying widget type and attributes in order to automate the creation of the corresponding widget).


# Exceptions

When loading a configuration file or writing data to a configuration file, the following exception can be raised in case of invalid configuration data:
 * `BadNameException`:<br>
    Raised when a param name is not defined in the metadata.
 * `BadValueTypeException`:<br>
    Raised when a scalar value does not match the expected type.
 * `MissingMandatoryException`:<br>
    Raised when a mandatory param is missing
 * `ValueOutOfRangeException`:<br>
    Raised when a digital param value is out of range.
 * `UnauthorizedValueException`:<br>
    Raised when a param value is not in the set of authorized values or is in the set of forbidden values.
 * `BadSequenceSizeException`:<br>
    Raised when a sequence param size is wrong
 * `InexistentParamException`:<br>
    Raised when reading a param that doesn't exist in the configuration data and for which there is no default value.
 * `RegexMismatchException`:<br>
    Raised when a string doesn't match a RegEx.

All exceptions include the complete path of the parameter that triggered the error, along with specific information such as expected values or size.
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
        "type": list,
        "content": {
            "type": dict,
            "content": {
                "name": {
                    "type": str,
                    "mandatory": True
                },
                "query": {
                    "type": str,
                    "mandatory": True
                },
                "mode": {
                    "type": str,
                    "mandatory": True,
                    "values": ("smart", "static") # `tuple` can be used
                                                  # instead of `list`
                }
            }
        },
        "label": None
    },
    'ui_language': {
        "type": str,
        "label": "Application language",
        "default": "en",
        "values":["en", "fr"],
        "ui": "Select" #ignored by the parser
    },
    "colors" :{
        "type": dict,
        "content": {
            "back": {
                "type": dict,
                "content": {
                    "regular": {
                        "type": list,
                        "size": 3,
                        "content": int,
                        "mandatory": True
                    },
                    "transparent": {
                        "type": list,
                        "size": 4,
                        "content": int
                    }
                }
            }
        }
    }
}

manager = JsonFlexConfig(configMetadata)
manager.LoadJson(json_code)

print(manager.GetParamValue("database_path"))
manager.SetParamValue("ui_language", "fr")
```
This code loads JSON files that can declare three parameters:
 * `"database_path"`: a String, that is mandatory.
 * `"lists"`: a list, which is also mandatory. In this list, every sub-parameter is a dictionary that contains the following key/value pairs:
     * `"name"`": a mandatory string
     * `"query"`": a mandatory string
     * `"type"`: a mandatory string, for which only two values are valid: `"smart"` and `"static"`.
 * `"ui-language"`: an optional string, for which only two values are valid: `"en"` and `"fr"`. If the parameter is not in the configuration file, requesting for `"ui-language"` returns `"en"`.
 * `"colors"`: an optional dictionary that contains the following key/value pairs:
     * `"regular"`": a mandatory list of three `int`
     * `"transparent"`": an optional list of four `int`

Applying this code to the following JSON file:
```json
{
    "database_path": "./db",
    "lists": [
        {
            "name": "All", 
            "query": "select *",
            "mode": "smart"
        },
        {
            "name": "SF, Fantasy",
            "query": "select * where genre='125'",
            "mode": "smart"
        },
        {
            "name": "MCU",
            "query": "1542",
            "mode": "smart"
        }
    ],
    "colors" :{
        "back": {
            "regular": [255, 255, 255]
        }
    }
}
```

displays:
```
./db
```

and add a new parameter `ui_language` set to `"fr"`. But with this JSON file, it doesn't work:
```json
{
    "database_path": "./db",
    "lists": [
        {
            "name": "All", 
            "query": "select *",
            "mode": "smart"
        },
        {
            "name": "SF, Fantasy",
            "query": "select * where genre='125'",
            "mode": "smart"
        },
        {
            "name": "MCU",
            "query": "1542",
        }
    ],
    "colors" :{
        "back": {
            "regular": [255, 255, 255]
        }
    }
}
```
Because the third sub-parameter of `lists` misses the parameter `mode` which is mandatory according to the metadata. Loading this JSON file thus raises a `MissingMandatoryException` with message: `Parameter error: missing mandatory "mode" in "{'name': 'MCU', 'query': '1542'}"`.
