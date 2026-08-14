from openai import OpenAI,AsyncOpenAI
from .Message import SystemMessage,HumanMessage,BaseMessage,HistoryMessage,AIMMessage,ToolMessage,AICallMessage
from .Data import Data
import json
from .Tool import BaseTool,ToolCall
from pathlib import Path
import logging
logger=logging.getLogger('Simple_Agent_Tool.Model')
class Model:
    model: OpenAI
    history_message: HistoryMessage
    model_prompt:str
    history_summary_prompt:str
    data:Data
    user_id:str
    type:str
    json_output:bool
    model_name:str
    def __init__(self, api_key, base_url,model_name:str,model_prompt:str,user_id:str,json_output=False,save_path:Path=None):
        logger.info(f"初始化模型{model_name}")
        if(save_path is None):
            logger.error(f"初始化模型{model_name}失败：save_path不能为空")
            raise ValueError("save_path不能为空")
        
        try:
            self.model = OpenAI(
                api_key=api_key,
                base_url= base_url,
            )
            
        except Exception as e:
            logger.error(f"初始化模型{model_name}失败：{e}")
            raise
        self.model_name=model_name
        self.json_output=json_output
        if(json_output):
            self.type='json_object'
        else:
            self.type='text'
        self.user_id=user_id
        self.model_prompt=model_prompt
        self.history_summary_prompt=''
        #self.history_message.add( )
        self.data=Data(save_path/user_id)
       # self.history_message=HistoryMessage(self.data.load())
        self.load()
        logger.info(f"初始化模型{model_name}成功")

    def invoke(self,message:str):
        query=HumanMessage(message)
        self.history_message.add(query)
        final_message=[SystemMessage(self.model_prompt+'\n'+self.history_summary_prompt).to_dict()]+self.history_message.unpack()
        logger.info(f'调用模型{self.model_name}')
        if(self.json_output):
            try:
                response=self.model.chat.completions.create(
                    model= self.model_name,
                    messages= final_message,
                    response_format={'type':self.type},
                    #strem=
                )
            except Exception as e:
                logger.error(f"模型{self.model_name}调用失败：{e}")
                raise
        else:
            try:
                response=self.model.chat.completions.create(
                            model= self.model_name,
                            messages= final_message,
                             
                        )
            except Exception as e:
                logger.error(f"模型{self.model_name}调用失败：{e}")
                raise
        
        if(self.json_output):
            try:
                parsed=json.loads(response.choices[0].message.content)
            except json.JSONDecodeError:
                logger.error(f"模型{self.model_name}调用失败：{str(response.choices[0].message.content)[:10]}不是JSON格式")
                raise ValueError(f"模型{self.model_name}调用失败：{str(response.choices[0].message.content)[:10]}不是JSON格式")
        else:
            parsed=response.choices[0].message.content
        self.history_message.add(AIMMessage(response.choices[0].message.content))
        self.save()      
        logger.info(f"模型{self.model_name}运行成功")
        return parsed
    def save(self):
        
        save_body={'history_message':self.history_message.unpack()
                   ,'history_summary_prompt':self.history_summary_prompt,
                   'version':2}
        try:
            self.data.save(save_body)
            logger.info(f"模型{self.model_name}保存成功")
        except Exception as e:
            logger.error(f"模型{self.model_name}保存失败：{e}")
            raise
    def load(self):
        load_body=[]
        try:
            load_body=self.data.load()
        except Exception as e:
            logger.error(f"模型{self.model_name}加载失败：{e}")
            raise
        if isinstance(load_body, dict) and 'history_message' in load_body:
            self.history_message=HistoryMessage(load_body['history_message'])
            self.history_summary_prompt=load_body.get('history_summary_prompt','')
        elif isinstance(load_body, list):
            self.history_message=HistoryMessage(load_body)
            self.history_summary_prompt=''
        else:
            self.history_message=HistoryMessage()
            self.history_summary_prompt=''
class Model_no_history:
    model: OpenAI
    model_prompt:str
    user_id:str
    type:str
    json_output:bool
    model_name:str
    def __init__(self, api_key, base_url,model_name:str,model_prompt:str,user_id:str,json_output=False):
        logger.info(f"初始化模型{model_name}")
        try:
            self.model = OpenAI(
                api_key=api_key,
                base_url= base_url,
            )
            
        except Exception as e:
            logger.error(f"初始化模型{model_name}失败：{e}")
            raise
        self.model_name=model_name
        self.json_output=json_output
        if(json_output):
            self.type='json_object'
        else:
            self.type='text'
        self.user_id=user_id
        self.model_prompt=model_prompt
        #self.history_message.add( )

    def invoke(self,message:str):
        query=HumanMessage(message)
        final_message=[SystemMessage(self.model_prompt).to_dict()]+[query.to_dict()]
        logger.info(f'调用模型{self.model_name}')
        if(self.json_output):
            try:
                response=self.model.chat.completions.create(
                    model= self.model_name,
                    messages= final_message,
                    response_format={'type':self.type},
                #strem=
                )
            except Exception as e:
                logger.error(f"模型{self.model_name}调用失败：{e}")
                raise
        else:
            try:
                response=self.model.chat.completions.create(
                            model= self.model_name,
                            messages= final_message,
                                
                        )
            except Exception as e:
                logger.error(f"模型{self.model_name}调用失败：{e}")
                raise
        if(self.json_output):       
            try:
                return json.loads(response.choices[0].message.content)
            except json.JSONDecodeError:
                logger.error(f"模型{self.model_name}调用失败：{str(response.choices[0].message.content)[:10]}不是JSON格式")
                raise ValueError(f"模型{self.model_name}调用失败：{str(response.choices[0].message.content)[:10]}不是JSON格式")
        return response.choices[0].message.content
class Model_With_Tool:
    model: OpenAI
    history_message: HistoryMessage
    model_prompt:str
    history_summary_prompt:str
    data:Data
    user_id:str
    model_name:str
    tools:list[BaseTool]
    tools_map:map #{name:Basetool}
    def __init__(self, api_key, base_url,model_name:str,model_prompt:str,user_id:str,Tools:list,save_path:Path=None):
        logger.info(f"初始化模型{model_name}")
        if(save_path is None):
            logger.error(f"初始化模型{model_name}失败：save_path不能为空")
            raise ValueError("save_path不能为空")
        try:
            self.model = OpenAI(
            api_key=api_key,
                base_url= base_url,
            )
            
        except Exception as e:
            logger.error(f"初始化模型{model_name}失败：{e}")
            raise
        self.tools=list()
        self.model_name=model_name
        self.tools=Tools
        self.tools_map={}
        for tool in Tools:
            self.tools_map[tool.name]=tool
        self.user_id=user_id
        self.model_prompt=model_prompt
        self.history_summary_prompt=''
        self.data=Data(save_path/user_id)

        self.load()
        logger.info(f"模型{model_name}初始化完成")
    def run(self,message:str|None=None):
        '''需要解包'''
        if(message is not None):
            query=HumanMessage(message)
            self.history_message.add(query)
        final_message=[SystemMessage(self.model_prompt+'\n'+self.history_summary_prompt).to_dict()]+self.history_message.unpack()
         
        logger.info(f'调用模型{self.model_name}')
        try:
            response=self.model.chat.completions.create(
                        model= self.model_name,
                        messages= final_message,
                        tools=[t.to_dict() for t in self.tools]
                            
                    )
        except Exception as e:
            logger.error(f"模型{self.model_name}调用失败：{e}")
            raise
        
        tool_calls=[]
        if(response.choices[0].message.tool_calls is None):
            logger.info(f"模型{self.model_name}调用成功，不包含工具调用")
            self.history_message.add(AIMMessage(response.choices[0].message.content))
        else:
            logger.info(f"模型{self.model_name}调用成功，包含工具调用")
            self.history_message.add(AICallMessage([tc.model_dump() for tc in response.choices[0].message.tool_calls]))
            try:
                for tool_call in response.choices[0].message.tool_calls:
                    tool_calls.append(ToolCall(tool_call.id,tool_call.function.name,json.loads(tool_call.function.arguments)))
            except Exception as e:
                logger.error(f"解析工具调用参数失败：{e}")
                raise
        self.save()
        logger.info(f"模型{self.model_name}运行成功")
        return response.choices[0].message.content, tool_calls
    def save(self):
        save_body={'history_message':self.history_message.unpack()
                    ,'history_summary_prompt':self.history_summary_prompt,
                    'version':2}
        try:
            self.data.save(save_body)
            logger.info(f"模型{self.model_name}保存成功")
        except Exception as e:
            logger.error(f"模型{self.model_name}保存失败：{e}")
            raise
    def load(self):
        try:
            load_body=self.data.load()
            logger.info(f"模型{self.model_name}加载成功")
        except Exception as e:
            logger.error(f"模型{self.model_name}加载失败：{e}")
            raise
        if isinstance(load_body, dict) and 'history_message' in load_body:
            self.history_message=HistoryMessage(load_body['history_message'])
            self.history_summary_prompt=load_body.get('history_summary_prompt','')
        elif isinstance(load_body, list):
            self.history_message=HistoryMessage(load_body)
            self.history_summary_prompt=''
        else:
            self.history_message=HistoryMessage()
            self.history_summary_prompt=''
    def addTool(self,tool:BaseTool):
        self.tools.append(tool)
        self.tools_map[tool.name]=tool
    def call_tool(self, tool_call: ToolCall):
        try:
            tool = self.tools_map[tool_call.tool_name]   # 可能 KeyError（工具不存在）
            ans = tool.execute(tool_call.arguments)      # 可能抛异常（工具执行失败）
            logger.info(f"模型{self.model_name}调用工具{tool_call.tool_name}成功")
        except KeyError:
            ans = f"错误：工具 {tool_call.tool_name} 不存在"
            logger.error(f"模型{self.model_name}调用工具{tool_call.tool_name}失败：工具不存在")
        except Exception as e:
            ans = f"错误：工具 {tool_call.tool_name} 执行失败 - {e}"
            logger.error(f"模型{self.model_name}调用工具{tool_call.tool_name}失败：工具执行失败")
        self.history_message.add(ToolMessage(ans, tool_call.tool_call_id))
        self.save()
        return ans
class AsyncModel_With_Tool(Model_With_Tool):
    def __init__(self, api_key, base_url,model_name:str,model_prompt:str,user_id:str,Tools:list,save_path:Path=None):
        if(save_path is None):
            logger.error(f"异步模型{model_name}初始化失败：save_path不能为空")
            raise ValueError("save_path不能为空")
        try:
            self.model = AsyncOpenAI(
                api_key=api_key,
                base_url= base_url,
            )
            logger.info(f"异步模型{model_name}初始化成功")
        except Exception as e:
            logger.error(f"异步模型{model_name}初始化失败：{e}")
            raise
        self.tools=list()
        self.model_name=model_name
        self.tools=Tools
        self.tools_map={}
        for tool in Tools:
            self.tools_map[tool.name]=tool
        self.user_id=user_id
        self.model_prompt=model_prompt
        self.history_summary_prompt=''
        self.data=Data(save_path/user_id)
        self.load()
     
    async def run(self,message:str|None=None):
        '''需要解包'''
        if(message is not None):
            query=HumanMessage(message)
            self.history_message.add(query)
        final_message=[SystemMessage(self.model_prompt+'\n'+self.history_summary_prompt).to_dict()]+self.history_message.unpack()
            
        try:
            response=await self.model.chat.completions.create(
                        model= self.model_name,
                        messages= final_message,
                        tools=[t.to_dict() for t in self.tools]
                            
                    )
        except Exception as e:
            logger.error(f"异步模型{self.model_name}运行失败：{e}")
            raise
        
        tool_calls=[]
        if(response.choices[0].message.tool_calls is None):
            self.history_message.add(AIMMessage(response.choices[0].message.content))
        else:
            self.history_message.add(AICallMessage([tc.model_dump() for tc in response.choices[0].message.tool_calls]))
            for tool_call in response.choices[0].message.tool_calls:
                tool_calls.append(ToolCall(tool_call.id,tool_call.function.name,json.loads(tool_call.function.arguments)))
        self.save()
        logger.info(f"异步模型{self.model_name}运行成功")
        return response.choices[0].message.content, tool_calls
class AsyncModel(Model):
    def __init__(self, api_key, base_url,model_name:str,model_prompt:str,user_id:str,json_output=False,save_path:Path=None):
        if(save_path is None):
            logger.error(f"异步模型{model_name}初始化失败：save_path不能为空")
            raise ValueError("save_path不能为空")
        try:
            self.model = AsyncOpenAI(
                api_key=api_key,
                base_url= base_url,
            )
            logger.info(f"异步模型{model_name}初始化成功")
        except Exception as e:
            logger.error(f"异步模型{model_name}初始化失败：{e}")
            raise
        self.model_name=model_name
        self.json_output=json_output
        if(json_output):
            self.type='json_object'
        else:
            self.type='text'
        self.user_id=user_id
        self.model_prompt=model_prompt
        self.history_summary_prompt=''
        #self.history_message.add( )
        self.data=Data(save_path/user_id)
        # self.history_message=HistoryMessage(self.data.load())
        self.load()
    async def invoke(self,message:str):
        query=HumanMessage(message)
        self.history_message.add(query)
        final_message=[SystemMessage(self.model_prompt+'\n'+self.history_summary_prompt).to_dict()]+self.history_message.unpack()
        if(self.json_output):
            try:
                response=await self.model.chat.completions.create(
                model= self.model_name,
                messages= final_message,
                response_format={'type':self.type},
                #strem=
            )
            except Exception as e:
                logger.error(f"异步模型{self.model_name}运行失败：{e}")
                raise
        else:
            try:
                response=await self.model.chat.completions.create(
                            model= self.model_name,
                            messages= final_message,
                                
                        )
                logger.info(f"异步模型{self.model_name}运行成功")
            except Exception as e:
                logger.error(f"异步模型{self.model_name}运行失败：{e}")
                raise
        
        
        if(self.json_output):
            try:
                parsed=json.loads(response.choices[0].message.content)
            except json.JSONDecodeError:
                logger.error(f"异步模型{self.model_name}运行失败：{str(response.choices[0].message.content)[:10]}不是JSON格式")
                raise ValueError(f"异步模型{self.model_name}运行失败：{str(response.choices[0].message.content)[:10]}不是JSON格式")
        else:
            parsed=response.choices[0].message.content
        self.history_message.add(AIMMessage(response.choices[0].message.content))
        self.save()
        logger.info(f"异步模型{self.model_name}运行成功")
        return parsed
class AsyncModel_no_history(Model_no_history):
    def __init__(self, api_key, base_url,model_name:str,model_prompt:str,user_id:str,json_output=False):
        try:
            self.model = AsyncOpenAI(
                api_key=api_key,
                base_url= base_url,
            )
            logger.info(f"异步模型{model_name}初始化成功")
        except Exception as e:
            logger.error(f"异步模型{model_name}初始化失败：{e}")
            raise
        self.model_name=model_name
        self.json_output=json_output
        if(json_output):
            self.type='json_object'
        else:
            self.type='text'
        self.user_id=user_id
        self.model_prompt=model_prompt
        #self.history_message.add( )
    
    async def invoke(self,message:str):
        query=HumanMessage(message)
        final_message=[SystemMessage(self.model_prompt).to_dict()]+[query.to_dict()]
        if(self.json_output):
            try:
                response=await self.model.chat.completions.create(
                    model= self.model_name,
                    messages= final_message,
                    response_format={'type':self.type},
                    #strem=
                )
                logger.info(f"异步模型{self.model_name}运行成功")
            except Exception as e:
                logger.error(f"异步模型{self.model_name}运行失败：{e}")
                raise
        else:
            try:
                response=await self.model.chat.completions.create(
                            model= self.model_name,
                            messages= final_message,
                                
                        )
                logger.info(f"异步模型{self.model_name}运行成功")
            except Exception as e:
                logger.error(f"异步模型{self.model_name}运行失败：{e}")
                raise
        if(self.json_output):       
            try:
                return json.loads(response.choices[0].message.content)
            except json.JSONDecodeError:
                logger.error(f"异步模型{self.model_name}运行失败：{str(response.choices[0].message.content)[:10]}不是JSON格式")
                raise ValueError(f"异步模型{self.model_name}运行失败：{str(response.choices[0].message.content)[:10]}不是JSON格式")
                
        return response.choices[0].message.content
