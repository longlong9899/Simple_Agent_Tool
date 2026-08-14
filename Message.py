import logging
logger = logging.getLogger('Simple_Agent_Tool.Message')
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
        logger.info('初始化一条user消息')
        self.role = 'user'
        self.content=content

    def to_dict(self):
        logger.debug('解包一条user消息')
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
        logger.info('初始化一条system消息')
        self.role = 'system'
        self.content=content

    def to_dict(self):
        logger.debug('解包一条system消息')
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
        logger.info('初始化一条assistant消息')
        self.role = 'assistant'
        self.content=content

    def to_dict(self):
        logger.debug('解包一条assistant消息')
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
        logger.info('初始化一条assistant(tool_calls)消息')
        self.role = 'assistant'
        self.tool_calls=toolcalls

    def to_dict(self):
        logger.debug('解包一条assistant(tool_calls)消息')
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
        logger.info('初始化一条tool消息')
        self.role = 'tool'
        self.content=content
        self.tool_call_id=tool_call_id
    
    def to_dict(self):
        logger.debug('解包一条tool消息')
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
        logger.info('初始化历史消息')
        self.message_list=list()
        if message_all_original is None:
            logger.info('历史消息为空,默认初始化为空列表')
            return 
        logger.info('初始化历史消息,消息数量:%d'%len(message_all_original))
        try:
            for message in message_all_original:
                if(message['role']=='system'):
                    self.message_list.append(SystemMessage(message['content']))
                elif(message['role']=='user'):
                    self.message_list.append(HumanMessage(message['content']))
                elif(message['role']=='assistant'):
                    if message['content'] is not None:
                        self.message_list.append(AIMMessage(message['content']))
                    else:
                        self.message_list.append(AICallMessage(message['tool_calls']))

                elif(message['role']=='tool'):
                    self.message_list.append(ToolMessage(message['content'],message['tool_call_id']))
                else:
                    logger.error('历史消息格式错误,角色:%s'%message['role'])
                    continue
        except Exception as e:
            logger.error('历史消息初始化失败:%s'%str(e))
            logger.error('初始化历史消息失败')
            raise 
        logger.info('历史消息初始化成功')

    def add(self,addmessage:BaseMessage)->None:
        logger.info('添加一条消息')
        self.message_list.append(addmessage)

    def unpack(self):
        logger.debug('解包历史消息')
        ret=list()
        for message in self.message_list:
            ret.append(message.to_dict())
        #p#rint(ret)
        return ret
    def size(self):
        return len(self.message_list)
    def clear(self):
        logger.info('清空历史消息')
        self.message_list.clear()

         
    
