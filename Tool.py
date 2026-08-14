from abc import ABC,abstractmethod
import logging
logger = logging.getLogger('Simple_Agent_Tool.Tool')
class BaseTool(ABC):
    
    name:str
    description:str
    properties:dict
    required:list
    def __init__(self,name:str,description:str,properties:dict,required:list):
        logger.info(f'初始化工具，工具名称：{name}')
        self.name=name
        self.description=description
        self.properties=properties
        self.required=required
    @abstractmethod
    def execute(self,arguments:dict)->str:
        pass
    def to_dict(self):
        logger.info(f'将工具转换为字典，工具名称：{self.name}')
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
        logger.info(f'初始化工具调用，工具调用ID：{tool_call_id}，工具名称：{tool_name}')
        self.tool_call_id=tool_call_id
        self.tool_name=tool_name
        self.arguments=arguments
    