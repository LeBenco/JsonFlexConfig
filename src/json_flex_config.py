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
################################ Config Manager ###############################

class JsonFlexConfig:
    """
    Description
    ===========
    `JsonFlexConfig` allows for configuration management based on metadata
    describing all the parameters to be used. The configuration is stored in a
    JSON file as a set of key/value pairs that associates each parameter's name
    to its value. Once loaded (and if the configuration file is valid), the
    JsonFlexConfig can be queried for the value of a parameter. If not present,
    a default value can be returned instead). The parameter values can be
    modified, and the new values can be stored back in the configuration file
    (only if explicitly requested). Sub-parameters with specific validation
    rules can be nested in parameters, allowing for sophisticated file
    structure.
    
    Compared to more advanced configuration management libraries like Pydantic,
    this class offers a similar level of interaction with configuration files,
    but it is limited to handling JSON format. However, it provides a concise
    and highly readable declaration of standard rules within a single structure
    defined directly in the code without requiring external files. This
    approach avoids certain common complexities found in more advanced
    libraries, such as the potential need to define multiple subclasses in some
    cases or manage separate configuration files. While tools like Pydantic
    excel with their implementation of custom validators and support for
    various formats, which can be particularly useful in complex scenarios,
    this class is tailored for standard validation needs, making it a practical
    choice for simpler applications. Nonetheless, it maintains a high level of
    sophistication in validation with standard rule definitions, typically
    exceeding that of `ConfigParser` (at least when using it out of the box).
    

    General rules
    =============
    A `JsonFlexConfig` object requires metadata that describes the expected
    format of the configuration file. This is a dictionary, associating a
    parameter's name to a format description. A format description is again a
    dictionary of all the rules applying to the parameter:
     * "type" (`type`):
       Parameter type. This must be the actual Python type. Any type is
       accepted, but only the following types provide type-specific rules
       validation: `int`, `float`, `list`, and `dict`.
     * "mandatory" (`bool`):
       If defined and set to `True`, the parameter has to be defined and not
       `None` in the configuration file.
     * "default" (object of type "type", optional):
       Only for non-mandatory parameters. If set, requesting for a parameter
       not in the configuration file will return the default value instead
       of `None`.
     * "values" (`list` of "type" objects, optional):
       List of all authorized values.
     * "label" (`str`):
       String describing the parameter, for display purposes.


    Type-specific rules
    ===================
    When dealing with list parameters, a few other rules can be applied:
     * "content_type" (`type`):
       Type of the items in the list. This key must be associated with the
       Python type. This means that it's not possible to store different types
       of objects in a single list (but dictionaries do allow this).
     * "size" (`int`, optional):
       number of objects in the list.

    When dealing with numeric parameters (ìnt`or `float`), a few other rules
    can be applied:
     * "min" (`int` or `float`, optional):
       Minimum value of the parameter.
     * "max" (`int` or `float`, optional):
       Maximum value of the parameter.
    Note that defining a `float` parameter and providing an `int` bound is
    perfectly valid, since Python allows value comparision between those types.

    When dealing with dictionary parameters, additional rules can be applied:
     * "content":
       A dictionary defining the rules for each sub-parameter within the
       dictionary. This allows for nested structures, where each sub-parameter
       can have its own validation rules, including type, mandatory status, and
       other constraints. This "content" section is a metadata description of
       sub-parameters that follows the same structure as the general metadata.
       It allows for nesting parameters with arbitrary depth, thus making
       dictionaries the most versatile structure for parameter management in
       `JsonFlexConfig`.


    Additional rules
    ================
    In addition to these parameters, the metadata file can also define other
    parameters, which will be ignored by the parser and can take arbitrary
    forms, making them useful for extending this library's functions (for
    example, specifying widget type and attributes in order to automate the
    creation of the corresponding widget).


    Example
    =======
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
    
    and replaces the content of "lists" with an empty dictionary.But with this
    JSON file, it doesn't work:
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
    
    Because the sub-parameter `lists.MCU` misses the parameter `type` which is
    mandatory according to the metadata. Loading this JSON file thus raises a
    `MissingMandatoryException` with message:
    ```
    Parameter error: missing mandatory "type" from "lists.MCU"
    ```
    """
    def __init__(self, config_metadata):
        self.configMetadata = config_metadata
    
    def GetMetadata(self):
        return self.configMetadata
    
    def LoadConfig(self, config_path):
        with open(config_path, 'r', encoding="UTF-8") as f:
            self.SetConfig(json.loads(f.read()))
            
            self.configPath = config_path
            self.previousConfig = None
    
    def SaveConfig(self, config_path=None):
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
                                         authorized values.
        All exceptions include the complete path of the parameter that
        triggered the error.
        """
        ## Raise an exception if mandatory root parameters are missing
        self.CheckMandatoryParam(config, metadata)
        
        ## Raise an exception if root parameters are not valid
        self.CheckParamNames(config, metadata)
        
        ## Check content of `config`
        for param in config:
            value = config.get(param)
            if value is not None:
                param_metadata = metadata[param]
                
                ## Used to show the full path of the parameter in exception messages
                full_param = f"{param_path}.{param}" if param_path else param

                ######## GENERAL CHECK FOR TYPE 
                if type(value) != param_metadata["type"]:
                    raise BadValueTypeException(param, value, param_metadata["type"], full_param)        

                ######## LIST RULES CHECK
                if isinstance(value, list):            
                    ## Check if the size-specific list has the correct size
                    if "size" in param_metadata:
                        size = len(value)
                        expected_size = param_metadata["size"]
                        if size != expected_size:
                            raise BadListSizeException(param, size, expected_size, full_param)
                    
                    ## Check if the elements in list are of the right type
                    for v in value:
                        expected_type = param_metadata["content_type"]
                        if type(v) != expected_type:
                            raise BadListTypeException(param, v, type(value), expected_type, full_param)

                ######## DICT RULES CHECK
                elif isinstance(value, dict) and "content" in param_metadata:
                    ## Check for each sub-parameter individually
                    for entry_name, entry_value in value.items():
                        self._CheckValidConfig(entry_value, param_metadata["content"], full_param)

                ######## NUMERIC VALUE RULES CHECK
                elif isinstance(value, (int, float)):
                    if "min" in param_metadata and value < param_metadata["min"]:
                        raise ValueOutOfRangeException(param, value, param_metadata["min"], full_param)
                    if "max" in param_metadata and value > param_metadata["max"]:
                        raise ValueOutOfRangeException(param, value, param_metadata["max"], full_param)

                ######## GENERAL CHECK FOR SET OF AUTHORIZED VALUES
                if "values" in param_metadata and value not in param_metadata["values"]:
                    raise UnauthorizedValueException(full_param, value, param_metadata["values"], full_param)

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
        Returns the parameter's value definied in the configuration, or the
        default value if it is not defined.
        
        Raises:
         * `InexistentParamException` if the provided parameter's name can't be
           found in the configuration file and doesn't have a default value.
        """
        try:
            param_value = self.config.get(param, self.configMetadata[param].get("default"))
            if isinstance(param_value, list):
                return tuple(param_value)
            else:
                return param_value
        except KeyError as e:
            raise InexistentParamException(self.configPath, param)

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
        Set value to the parameter.
        
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
            message += f' in "{param}"'
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
    """Raised when a param digital value is not in the set of authorized values"""
    def __init__(self, param, value, authorized_values, context=""):
        source = f'"{param}"'
        if context:
            source += f' in {context}"'
        message = f'Value error on "{source}": wrong value ({value}'\
                       +f', expecting of one {authorized_values})'
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

class BadCompositeSizeException(ConfigException):
    """Raised when a tuple param size is wrong"""
    def __init__(self, param, size, expected_size):
        message = "Type error on \""+str(param)\
                 +"\": wrong size ("+str(size)\
                 +", expecting tuple"\
                 +" of "+str(expected_size)+" elements)"
        super().__init__(message)

class InexistentParamException(ConfigException):
    """Raised when a tuple param size is wrong"""
    def __init__(self, file_path, param):
        message = "Param error in "+file_path+": \""+str(param)\
                 +"\" is not a valid option"
        super().__init__(message)
