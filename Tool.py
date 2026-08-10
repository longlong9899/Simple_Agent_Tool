from abc import ABC,abstractmethod

class BaseTool(ABC):
    
    name:str
    description:str
    properties:dict
    required:list
    def __init__(self,name:str,description:str,properties:dict,required:list):
        self.name=name
        self.description=description
        self.properties=properties
        self.required=required
    @abstractmethod
    def execute(self,arguments:dict)->str:
        pass
    def to_dict(self):
        return {
                'type':'function',
                'function':{
                            'name':self.name,
                            'description':self.description,
                            'parameters':{
                                        'type':'object',
                                        'properties':self.properties,
                                        'required':self.required
                                        }
                            }
                }
class ToolCall:
    tool_call_id:str
    tool_name:str
    arguments:dict
    def __init__(self,tool_call_id:str,tool_name:str,arguments:dict):
        self.tool_call_id=tool_call_id
        self.tool_name=tool_name
        self.arguments=arguments
    