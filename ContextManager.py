from .Model import Model_no_history,AsyncModel_no_history,Model
from .Message import HistoryMessage
from abc import ABC,abstractmethod
class ContextManager(ABC):
    model:Model
    max_context_token:int=850000
    conversion_ratio:float=1.4
    reverse_ratio:float=0.5
    summary_prompt='''请阅读下方人机对话记录，提炼全部关键信息、约定、诉求，整理生成对话摘要。

约束要求：
1. 直接输出原生Markdown文本，不要添加任何开场白、解释、多余话术，不要用```代码块包裹；
2. 严格遵循下面固定结构模板输出，层级不能改动，没有对应内容的模块可以保留标题，内容填写【无】；
# 历史对话摘要
## 核心讨论主题
概括本次对话整体在讨论什么内容
## 重要共识 & 确定事项
- 逐条列出双方敲定、达成一致的内容、约定、规则
## 用户诉求 / 用户关注点
- 逐条整理用户提出的需求、疑问、想法
## 待解决问题 / 未完成事项
'''
    api_key:str
    base_url:str
    model_name:str
    def __init__(self,model:Model):
        self.model=model
    def is_context_over(self):
        s=str()
        for message in self.model.history_message.unpack():
            if message['role']=='assistant' and message['content']==None:
                s+=f'{message['role']}{message['tool_calls']}None'
            else:
                s+=f'{message['role']}{message['content']}'
        return len(s)>self.max_context_token*self.conversion_ratio
    def config(self,max_context_token:int=None,conversion_ratio:float=None,reverse_ratio:float=None,summary_prompt:str=None
               ,api_key:str=None,base_url:str=None,model_name:str=None):
        if max_context_token is not None:
            self.max_context_token=max_context_token
        if conversion_ratio is not None:
            self.conversion_ratio=conversion_ratio
        if reverse_ratio is not None:
            self.reverse_ratio=reverse_ratio
        if summary_prompt is not None:
            self.summary_prompt=summary_prompt
        if api_key is not None:
            self.api_key=api_key
        if base_url is not None:
            self.base_url=base_url
        if model_name is not None:
            self.model_name=model_name
    def compress_by_summary(self)->str:
        summary_model=Model_no_history(self.api_key,self.base_url,self.model_name,self.summary_prompt,'summary')
        temp_list=self.model.history_message.unpack()
        split_index=self.split_index()
        up_list=temp_list[0:split_index]
        down_list=temp_list[split_index:]
        query='原摘要总结：'+self.model.history_summary_prompt+'\n'+'新上下文：\n'
        for message in up_list:
            if message['role']=='assistant' and message['content']==None:
                query+=f'{message['role']} {message['tool_calls']}None\n'
            elif message['role']=='user':
                query+=f'{message['role']} {message['content']}\n'
            elif message['role']=='assistant':
                query+=f'{message['role']} {message['content']}\n'
            elif message['role']=='tool':
                query+=f'{message['role']} {message['tool_call_id']} {message['content']}\n'
        summary=summary_model.invoke(query)
        self.model.history_message=HistoryMessage(down_list)
        self.model.history_summary_prompt=summary
        self.model.save()
        return summary
    async def async_compress_by_summary(self)->str:
            summary_model=AsyncModel_no_history(self.api_key,self.base_url,self.model_name,self.summary_prompt,'summary')
            temp_list=self.model.history_message.unpack()
            split_index=self.split_index()
            up_list=temp_list[0:split_index]
            down_list=temp_list[split_index:]
            query='原摘要总结：'+self.model.history_summary_prompt+'\n'+'新上下文：\n'
            for message in up_list:
                if message['role']=='assistant' and message['content']==None:
                    query+=f'{message['role']} {message['tool_calls']}None\n'
                elif message['role']=='user':
                    query+=f'{message['role']} {message['content']}\n'
                elif message['role']=='assistant':
                    query+=f'{message['role']} {message['content']}\n'
                elif message['role']=='tool':
                    query+=f'{message['role']} {message['tool_call_id']} {message['content']}\n'
            summary=await summary_model.invoke(query)
            self.model.history_message=HistoryMessage(down_list)
            self.model.history_summary_prompt=summary
            self.model.save()
            return summary
        
    def compress_by_delete(self):
        len=self.model.history_message.size()
        temp_list=self.model.history_message.unpack()
        split_index=self.split_index()
        #up_list=temp_list[0:split_index]
        down_list=temp_list[split_index:]
        self.model.history_message=HistoryMessage(down_list)

        #delete_len=len-int(len*self.reverse_ratio)
        self.model.save()
    def compress(self):
        '可重写函数，默认走摘要压缩'
        return self.compress_by_summary()
        #return None
    def clear(self):
        self.model.history_message.clear()
        self.model.save()
    def split_index(self):
        len=self.model.history_message.size()
        reverse_len=int(len*self.reverse_ratio)
        temp_list=self.model.history_message.unpack()
        split_index=0
        for i in range(reverse_len-1,-1,-1):
            if temp_list[i]['role']=='user':
                split_index=i
                break
        return split_index

