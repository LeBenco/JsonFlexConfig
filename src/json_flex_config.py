"""
MIT License

Copyright (c) 2024 Benjamin Cohen Boulakia

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
###############################################################################
############################## JSON Flex Config ###############################

class JsonFlexConfig:
    """
    # Description

    _JsonFlexConfig_ allows for the management of configurations based on
    metadata describing all the parameters to be used. The configuration data
    is stored in a JSON file as a set of key/value pairs associating the name
    of each parameter with its value. Once loaded (and if the configuration
    data is valid), the `JsonFlexConfig` object can be queried for the value of
    a parameter (if not present, a default value can be returned). Parameter
    values can be modified, and the new values stored in the configuration file
    (only if explicitly requested). Sub-parameters with specific validation
    rules can be nested within parameters, enabling a sophisticated file
    structure.

    Compared with more advanced configuration management libraries such as
    Pydantic, _JsonFlexConfig_ offers a similar level of interaction with
    configuration files, but is limited to handling JSON format. However, it
    provides a concise and highly readable declaration of standard rules within
    a single Python structure, which can be defined directly in the code
    without the need for external files. This approach bypasses some of the
    common complexities found in more advanced libraries, such as the need to
    define multiple subclasses or manage separate configuration files in (yet)
    another format. While tools like Pydantic excel in enabling the
    implementation of custom validators and supporting a variety of formats,
    which can be particularly useful in complex scenarios, _JsonFlexConfig_
    remains a practical choice for many applications. Despite its simplicity,
    _JsonFlexConfig_ offers a sophisticated level of validation through
    standard rule definitions, typically surpassing that of ConfigParser (at
    least in its default configuration). One can leverage these advanced
    features using only Python (and JSON of course), without the need for
    additional files in other formats or complex code structures.


    # General usage

    To use _JsonFlexConfig_, four steps must be applied:

    1. Create Validation Rules<br>
       Define a metadata dictionary that outlines the validation rules. This
       metadata describes aspects such as parameter types, whether they are
       mandatory or optional, default values, etc. These rules will be used to
       load and validate the data.
    2. Instantiate `JsonFlexConfig`<br>
       Create a `JsonFlexConfig` object using the previously defined metadata.
    3. Load and Validate Data<br>
       Open a JSON configuration file with the `JsonFlexConfig` object.
       Alternatively, data can be loaded directly from a Python dictionary,
       providing it has the same structure as the data a JSON parser would
       create. The JSON file must contain a dictionary where each key is a
       string representing a parameter name, and the corresponding value is
       that parameter's content. The data will be validated according to the
       rules defined in the metadata. If any rule fails validation, an
       exception will be raised.
    3. Access Configuration Data<br>
       Once the data is validated, access its content using the parameter names.

    # Common rules

    A `JsonFlexConfig` object requires metadata that describes the expected
    format of the configuration file. This is a dictionary, associating a
    parameter's name to a format description. A format description is again a
    dictionary of all the rules applying to the parameter. Six different type
    of rules can be defined, in the form of pairs of keys (a string containing
    the name of the rule type) / values (the rule itself):
     * `"type"` (`type`):
       Parameter's type. This must be the actual Python type. Any type is
       accepted, but only the following types provide type-specific rules
       validation: `int`, `float`, `list`, and `dict`.
     * `"mandatory"` (`bool`):
       If defined and set to `True`, the parameter has to be defined and not
       `None` in the configuration file.
     * `"default"` (object of the same type as the value of `"type"`, optional):
       Only for non-mandatory parameters. If set, requesting for a parameter
       not in the configuration file will return the default value instead of
       `None`.
     * `"values"` (`list` of objects of the same type as the value of `"type"`,
     optional):
       List of all authorized values. Any value not in this list will raise an
       exception.
     * `"forbidden_values"` (`list` of objects of the same type as the value of
     `"type"`, optional):
       List of all forbidden_values values. Any value in this list will raise
       an exception.
     * `"label"` (`str`):
       String describing the parameter, at the developer's disposal for display
       purposes.


    # Type-specific rules

    When dealing with list parameters, two other rules can be applied:
     * `"content"` (`type` or `dict`):<br>
       Type of the items in the list. If defined, every item in the list must
       be of this type. If the list contains simple values, "content" must be
       set to their corresponding `type`. If the list contains sub-parameters,
       "content" must be a dictionary defining the type of every
       sub-parameters, following the same structure as the general metadata.
     * `"size"` (`int`, optional):<br>
       number of objects in the list.
     * `"minsize"` (`int`, optional):<br>
       minimum number of objects in the list.
     * `"maxsize"` (`int`, optional):<br>
       maximum number of objects in the list.

    When dealing with numeric parameters (`int` or `float`), two additional
    rules can be applied:
     * `"min"` (`int` or `float`, optional):<br>
       Minimum value of the parameter.
     * `"max"` (`int` or `float`, optional):<br>
       Maximum value of the parameter.

    Note that defining a `float` parameter and providing an `int` bound is
    perfectly valid, since Python allows value comparision between those types.

    When dealing with dictionary parameters, one additional rule can be applied:
     * `"content"`:
       A dictionary containing metadata description of sub-parameters. This
       dictionary must contain a list of keys associated with the specific
       rules applied to each key. These specific rules follow the same
       structure as the general metadata. Each sub-parameter within the
       dictionary can have its specific rules, including type, mandatory
       status, and other constraints.

    Important note: There is almost no verification done on the metadata,
    it's up to the user to ensure that it is correct. An error in metadata may
    lead to inconsistent behavior from _JsonFlexConfig_, for example if a value
    is at the same time in the list of authorized values and in the list of
    forbidden ones, or if a mandatory parameter has a default value. Mutually
    exclusive rules may also happen, for example if a `min` value is greate
    than a `max` value.  

    # Additional metadata

    In addition to these parameters, rules in the metadata file can also define
    other options, which will be ignored by the parser and can take arbitrary
    forms, making them useful for extending this library's functions (for
    example, specifying widget type and attributes in order to automate the
    creation of the corresponding widget).


    # Exceptions

    When loading a configuration file or writing data to a configuration file,
    the following exception can be raised in case of invalid configuration data:
     * `BadNameException`: Raised when a param name is not defined in the
                           metadata.
     * `BadValueTypeException`: Raised when a param value type is wrong.
     * `MissingMandatoryException`: Raised when a mandatory param is missing
     * `ValueOutOfRangeException`: Raised when a digital param value is out of
                                   range.
     * `UnauthorizedValueException`: Raised when a param value is not in the
                                     set of authorized values or is in the set
                                     of forbidden values.
     * `BadListTypeException`: Raised when a list param contains values of
                               wrong type.
     * `BadListSizeException`: Raised when a tuple param size is wrong
     * `InexistentParamException`: Raised when reading a param that doesn't
                                   exist in the configuration data and for
                                   which there is no default value.


    # Example

    Here is an example that creates metadata, loads a configuration file using
    the defined structure, and manipulates parameter values:
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
            "label": "Drive-In language",
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
     * `"lists"`: a list, which is also mandatory. In this list, every
       sub-parameter is a dictionary that must contain:
         * `"name"`": a mandatory string
         * `"query"`": a mandatory string
         * `"type"`: a mandatory string, for which only two values are valid:
           `"smart"` and `"static"`.
     * `"ui-language"`: an optional string, for which only two values are
       valid: `"en"` and `"fr"`. If the parameter is not in the configuration
       file, requesting for `"ui-language"` returns `"en"`.

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

    and add a new parameter `ui_language` set to `"fr"`. But with this JSON
    file, it doesn't work:
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

    Because the third sub-parameter of `lists` misses the parameter `mode` which is
    mandatory according to the metadata. Loading this JSON file thus raises a
    `MissingMandatoryException` with message: `Parameter error: missing
    mandatory "mode" in "{'name': 'MCU', 'query': '1542'}"`
    """
    def __init__(self, config_metadata):
        self.configMetadata = config_metadata
    
    def GetMetadata(self):
        return self.configMetadata
    
    def LoadFile(self, config_path):
        with open(config_path, 'r', encoding="UTF-8") as f:
            self.LoadJson(f.read())    
            self.configPath = config_path
    
    def LoadJson(self, json_code):
        self.SetConfig(json.loads(json_code))
        self.previousConfig = None
    
    def SaveConfigToFile(self, config_path=None):
        if config_path is None:
            config_path = self.configPath
            
        with open(config_path, "w", encoding='utf8') as f:
            f.write(json.dumps(self.config, indent=4))
            
            self.previousConfig = None

    def DiscradChanges(self):
        if self.previousConfig is not None:
            self.config = self.previousConfig
            self.previousConfig = None

    def SetConfig(self, config):
        self._CheckValidConfig(config, self.configMetadata)
        self.config = config

    def GetConfig(self):
        return self.config

    def _CheckValidConfig(self, config, metadata, param_path=""):
        """
        Recursive function that validates the configuration data against the
        rules defined in the metadata. The function calls itself recursively
        for nested dictionary structures.
        
        This function performs the following verifications:
         1. Checks for mandatory parameters at the root level
         2. Verifies that all root parameters are defined in the metadata.
         3. Validates each parameter's value against general and specific rules
           in this order:
             a. Type validation against the expected type in metadata.
             b. Type-specific rules:
                 * For lists: size validation and element type checking.
                 * For dictionaries: recursive validation of sub-parameters.
                 * For numeric values: range checking (min/max).
             c. Validation against the set of authorized values, if specified.

        If any check fails to validate `config` against `metadata`, the
        corresponding exception is raised, and the validation process is
        interrupted.

        Parameters:
         * `config` (`dict`): The content of the configuration.
         * `metadata`: The rules that applies to the configuration data.
         * `param_path` (`str`, optional): The path to the parameter in the
           configuration, used by exceptions for error reporting.
        
        Raises:
         * `MissingMandatoryException`: If a mandatory parameter is not
                                        provided.
         * `BadValueTypeException`: If the type of `value` does not match the
                                    expected type.
         * `BadListSizeException`: If the size of a list does not match the
                                   expected size.
         * `BadCompositeTypeException`: If an element in a list is of the wrong
                                        type.
         * `BadNameException`: If a key in a dictionary is not recognized.
         * `ValueOutOfRangeException`: If a numeric value is outside the
                                       specified range.
         * `UnauthorizedValueException`: If the value is not in the set of
                                         authorized values or is in the set of
                                         forbidden values.
        All exceptions include the complete path of the parameter that
        triggered the error.
        """
        ## Raise an exception if mandatory root parameters are missing
        self.CheckMandatoryParam(config, metadata, param_path)
        
        ## Raise an exception if root parameters are not valid
        self.CheckParamNames(config, metadata, param_path)
        
        ## Check content of `config`
        for param in config:
            value = config.get(param)
            if value is not None:
                param_metadata = metadata[param]

                ######## GENERAL CHECK FOR TYPE 
                if type(value) != param_metadata["type"]:
                    raise BadValueTypeException(param, value,
                                                param_metadata["type"],
                                                param_path)        

                ######## LIST RULES CHECK
                if isinstance(value, list):            
                    ## Check if the size-specific list has the correct size
                    if "size" in param_metadata:
                        size = len(value)
                        expected_size = param_metadata["size"]
                        if size != expected_size:
                            raise BadListSizeException(param, size,
                                                       expected_size,
                                                       "not equal to",
                                                       param_path)
                    else:
                        if "minsize" in param_metadata:
                            size = len(value)
                            min_size = param_metadata["minsize"]
                            if size < min_size:
                                raise BadListSizeException(param, size,
                                                           min_size,
                                                           "bellow min size of",
                                                           param_path)
                        if "maxsize" in param_metadata:
                            size = len(value)
                            max_size = param_metadata["maxsize"]
                            if size > max_size:
                                raise BadListSizeException(param, size,
                                                           max_size,
                                                           "over max size of",
                                                           param_path)
                    
                    ## Check if the elements in list are of the right type
                    
                    expected_type = param_metadata.get("content")
                    # In case of simple type, check is performed directly on
                    # each value
                    if isinstance(expected_type, type):
                        for v in value:
                            if type(v) != expected_type:
                                raise BadListTypeException(param, v, type(value),
                                                           expected_type["content"],
                                                           param_path)
                    # In case of complex type, check content recursively for
                    # each sub-parameter
                    else:
                        for v in value:
                            full_param = (f"{param_path}.{v}"
                                      if param_path else v)
                            self._CheckValidConfig(v,  expected_type["content"],
                                                   full_param)

                ######## DICT RULES CHECK
                elif isinstance(value, dict):
                    if "content" in param_metadata:
                        ## Check for each sub-parameter individually
                        full_param = (f"{param_path}.{param}"
                                      if param_path else param)
                        self._CheckValidConfig(value, param_metadata["content"],
                                               full_param)

                ######## NUMERIC VALUE RULES CHECK
                elif isinstance(value, (int, float)):
                    if "min" in param_metadata and value < param_metadata["min"]:
                        raise ValueOutOfRangeException(param, value,
                                                       param_metadata["min"],
                                                       param_path)
                    if "max" in param_metadata and value > param_metadata["max"]:
                        raise ValueOutOfRangeException(param, value,
                                                       param_metadata["max"],
                                                       param_path)

                ######## GENERAL CHECK FOR SET OF AUTHORIZED VALUES
                if ("values" in param_metadata and
                    value not in param_metadata["values"]):
                    raise UnauthorizedValueException(param, value,
                                                     param_metadata["values"],
                                                     param_path)

                ######## GENERAL CHECK FOR SET OF FORBIDDEN VALUES
                if ("forbidden_values" in param_metadata and
                    value in param_metadata["forbidden_values"]):
                    raise UnauthorizedValueException(param, value, None,
                                                     param_path)

    def CheckParamNames(self, config, metadata, context=None):
        """
        Raises a `BadNameException` if a key in `config` is not recognized.
        
        Parameters:
         * `config`: the configutation to check.
         * `metadata`: the rules in which to search for all the param names.
         * `context`: the context to append to the paramater's name in the
           exception's error message. Ignored if `None`.
        
        Raises:
         * `BadNameException`
        """
        for param in config:
            if param not in metadata:
                raise BadNameException(param, context)

    def CheckMandatoryParam(self, config, metadata, context=None):
        """
        Raises a `MissingMandatoryException` if a mandatory parameter is not
        provided or defined as `None` which is considered as not defined.
        
        Parameters:
         * `config`: the configutation to check.
         * `metadata`: the rules in which to search for all the param names.
         * `context`: the context to append to the paramater's name in the
           exception's error message. Ignored if `None`.
        
        Raises:
         * `MissingMandatoryException`
        """
        mandatory = [param for param, value in metadata.items()
                     if "mandatory" in value and value["mandatory"]]
        for param in mandatory:
            if param not in config or config[param] is None:
                raise MissingMandatoryException(param, context)

    def GetParamValue(self, param):
        """
        Returns the parameter's value defined in the configuration, the
        default value if it is not defined but has a default value, and `None`
        if not defined and without default value.
        
        Raises:
         * `InexistentParamException` if the provided parameter's name can't be
           found in the metadata.
        """
        if param not in self.configMetadata:
            raise InexistentParamException(self.configPath, param)
        
        ## value of `param` or default value or `None`
        param_value = self.config.get(param,
                                      self.configMetadata[param].get("default"))

        if isinstance(param_value, list):
            return tuple(param_value)
        else:
                return param_value

    def GetParamLabel(self, param):
        """
        Returns the parameter's label definied i, or `None` if it' is not in
        the metadata.
        
        Raises:
         * `InexistentParamException` if the provided parameter's name can't be
           found in the metadata.
        """
        try:
            return self.configMetadata[param].get("label")
        except KeyError as e:
            raise InexistentParamException(self.configPath, param)

    def SetParamValue(self, param, value):
        """
        Set value to the parameter. I an exception is raised, the current
        configuration data is left unchanged.
        
        Raises:
         * `InexistentParamException`: If the provided parameter's name can't be
                                       found in the metadata.
         * `MissingMandatoryException`: If a mandatory parameter is not provided.
         * `BadValueTypeException`: If the type of `value` does not match the
                                    expected type.
         * `BadListSizeException`: If the size of a list does not match the
                                   expected size.
         * `BadListTypeException`: If an element in a list is of the wrong
                                   type.
         * `BadNameException`: If a key in a dictionary is not recognized.
         * `ValueOutOfRangeException`: If a numeric value is outside the
                                       specified range.
         * `UnauthorizedValueException`: If the value is not in the set of
                                         authorized values.
        All exceptions include the complete path of the parameter that
        triggered the error.
        """
        if param not in self.configMetadata:
            raise InexistentParamException(self.configPath, param)
            return
        
        if self.previousConfig is None:
            self.previousConfig = self.config

        new_config = self.config.copy()
        new_config[param] = value

        self._CheckValidConfig(new_config, self.configMetadata)
        
        self.config = new_config

  
################################################################################
################################## Exceptions ##################################

class ConfigException(Exception):
    """Base class for all other exceptions"""
    pass

class BadNameException(ConfigException):
    """Raised when a param value type is wrong"""
    def __init__(self, param, context=""):
        message = f'Parameter error: unknown name "{param}"'
        if context:
            message += f' in "{context}"'
        super().__init__(message)

class BadValueTypeException(ConfigException):
    """Raised when a param value type is wrong"""
    def __init__(self, param, value, expected_type, context):
        source = f'"{param}"'
        if context:
            source += f' in "{context}"'
        if isinstance(expected_type, type):
            expected_type_name = expected_type.__name__
        elif isinstance(expected_type, dict):
            expected_type_name = "one of the following types: " + ", ".join(str(k) for k in expected_type.keys())
        else:
            expected_type_name = str(expected_type)  # Convertir en chaîne si ce n'est pas un type

        self.message = (
            f'Type error on "{source}": wrong value ({value}, expecting {expected_type_name})'
        )
        super().__init__(self.message)


class MissingMandatoryException(ConfigException):
    """Raised when a param value type is wrong"""
    def __init__(self, param, context=None):
        message = f'Parameter error: missing mandatory "{param}"'
        if context:
            message += f' in "{context}"'
        super().__init__(message)

class ValueOutOfRangeException(ConfigException):
    """Raised when a param digital value is out of range"""
    def __init__(self, param, value, bound, context=""):
        source = f'"{param}"'
        if context:
            source += f' in "{contect}"'
        if value < bound:
            message = f'Value error on "{source}": wrong value ("{value}'\
                       +f', expecting greater or equal to {bound})'
        else:
            message = f'Value error on "{source}": wrong value ("{value}'\
                       +f', expecting lower or equal to {bound})'
        super().__init__(message)

class UnauthorizedValueException(ConfigException):
    """Raised when a param digital value is not in the set of authorized values
       or is in the set of forbidden values"""
    def __init__(self, param, value, authorized_values, context=""):
        source = f'"{param}"'
        if context:
            source += f' in {context}"'
        
        if authorized_values:
            message = f'Value error on {source}: wrong value ("{value}"'\
                     +f', expecting of one {authorized_values})'
        else:
            message = f'Value error on {source}: "{value}" in list'\
                      +' of forbidden values'\

        super().__init__(message)
        
class BadListTypeException(ConfigException):
    """Raised when a list param contains values of wrong type"""
    def __init__(self, param, v, comp_type, expected_type, context):
        source = f'"{param}"'
        if context:
            source += f' in {context}"'
        message = f'Type error on "{source}": wrong value ({v}'\
                 +f', expecting {comp_type.__name__}'\
                 +f' of {expected_type.__name__})'
        super().__init__(message)

class BadListSizeException(ConfigException):
    """Raised when a tuple param size is wrong"""
    def __init__(self, param, size, expected_size, expected_msg, context):
        source = f'"{param}"'
        if context:
            source += f' in "{context}"'
        message = f'Size error on "{source}":'\
                 +f' {size} {expected_msg} {expected_size}'
        super().__init__(message)

class InexistentParamException(ConfigException):
    """Raised when a tuple param size is wrong"""
    def __init__(self, file_path, param):
        message = "Param error in "+file_path+": \""+str(param)\
                 +"\" is not a valid option"
        super().__init__(message)


if __name__ == "__main__":
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
                        "values": ("smart", "static") # `tuple` can be used instead of `list`
                    }
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

    json_code = """
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
            "query": "1542"
        }
    ],
    "colors" :{
        "back": {
            "regular": [1, 2, 3]
        }
    }
}"""
    manager = JsonFlexConfig(configMetadata)
    manager.LoadJson(json_code)

    print(manager.GetParamValue("database_path"))
    manager.SetParamValue("ui_language", "fr")
