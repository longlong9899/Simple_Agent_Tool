 
class BaseMessage():
    '''
        基础消息类
        并提供to_dict方法，用于解包消息
        不允许实例化
    '''
    content:str
     
    def to_dict(self):
        raise NotImplementedError
    
    
class HumanMessage(BaseMessage):
    '''
    人类消息类
    提供to_dict方法，用于解包消息
    允许实例化
    提供__init__方法，用于初始化消息

    '''
    role:str 
    def __init__(self,content:str):
        self.role = 'user'
        self.content=content

    def to_dict(self):
        return {'role':self.role,'content':self.content}
    
    
class SystemMessage(BaseMessage):
    '''
    系统消息类
    提供to_dict方法，用于解包消息
    允许实例化
    提供__init__方法，用于初始化消息
    
    '''
    role:str 
    def __init__(self,content:str):
        self.role = 'system'
        self.content=content

    def to_dict(self):
        return {'role':self.role,'content':self.content}
     
    
class AIMMessage(BaseMessage):
    '''
    AIM消息类
    提供to_dict方法，用于解包消息
    允许实例化
    提供__init__方法，用于初始化消息
    
    '''
    role:str 
    def __init__(self,content:str):
        self.role = 'assistant'
        self.content=content

    def to_dict(self):
        return {'role':self.role,'content':self.content}
class AICallMessage(BaseMessage):
    '''
    AIM消息类
    提供to_dict方法，用于解包消息
    允许实例化
    提供__init__方法，用于初始化消息
    
    '''
    role:str 
    def __init__(self,toolcalls:list[dict]):
        self.role = 'assistant'
        self.tool_calls=toolcalls

    def to_dict(self):
        return {'role':self.role,'tool_calls':self.tool_calls,'content':None}
class ToolMessage(BaseMessage):
    '''
    工具消息类
    提供to_dict方法，用于解包消息
    允许实例化
    提供__init__方法，用于初始化消息
    '''
    role:str 
    content:str
    tool_call_id:str
    def __init__(self,content:str,tool_call_id:str):
        self.role = 'tool'
        self.content=content
        self.tool_call_id=tool_call_id
    
    def to_dict(self):
        return {'role':self.role,'tool_call_id':self.tool_call_id,'content':self.content,}
    
class HistoryMessage:
    '''
    历史消息类
    提供add方法，用于添加消息
    提供unpack方法，用于解包消息    
    允许实例化
    提供__init__方法，用于初始化消息

    '''
    message_list:list[BaseMessage]
    
    def __init__(self,message_all_original:list|None=None):
        self.message_list=list()
        if message_all_original is None:
            return 
        for message in message_all_original:
            if(message['role']=='user'):
                self.message_list.append(HumanMessage(message['content']))
            elif(message['role']=='assistant'):
                if message['content'] is not None:
                    self.message_list.append(AIMMessage(message['content']))
                else:
                    self.message_list.append(AICallMessage(message['tool_calls']))

            elif(message['role']=='tool'):
                self.message_list.append(ToolMessage(message['content'],message['tool_call_id']))

    def add(self,addmessage:BaseMessage)->None:
        self.message_list.append(addmessage)

    def unpack(self):
        ret=list()
        for message in self.message_list:
            ret.append(message.to_dict())
        #p#rint(ret)
        return ret

         
    
