from openai import OpenAI
from .Message import SystemMessage,HumanMessage,BaseMessage,HistoryMessage,AIMMessage
from .Data import Data
import json
from pathlib import Path
class Model:
    model: OpenAI
    history_message: HistoryMessage
    model_prompt:str
    data:Data
    user_id:str
    type:str
    json_output:bool
    model_name:str
    def __init__(self, api_key, base_url,model_name:str,model_prompt:str,user_id:str,json_output=False,save_path:Path=None):
        if(save_path is None):
            raise ValueError("save_path不能为空")
            
        self.model = OpenAI(
            api_key=api_key,
            base_url= base_url,
        )
        self.model_name=model_name
        self.json_output=json_output
        if(json_output):
            self.type='json_object'
        else:
            self.type='text'
        self.user_id=user_id
        self.model_prompt=model_prompt
        #self.history_message.add( )
        self.data=Data(save_path/user_id)
        self.history_message=HistoryMessage(self.data.load())

    def invoke(self,message:str):
        query=HumanMessage(message)
        self.history_message.add(query)
        final_message=[SystemMessage(self.model_prompt).to_dict()]+self.history_message.unpack()
        if(self.json_output):
            response=self.model.chat.completions.create(
                model= self.model_name,
                messages= final_message,
                response_format={'type':self.type},
                #strem=
            )
        else:
            response=self.model.chat.completions.create(
                            model= self.model_name,
                            messages= final_message,
                             
                        )
        self.history_message.add(AIMMessage(response.choices[0].message.content))
        self.data.save(self.history_message.unpack())
        if(self.json_output):
            return json.loads(response.choices[0].message.content)
        return response.choices[0].message.content
class Model_no_history:
    model: OpenAI
    model_prompt:str
    user_id:str
    type:str
    json_output:bool
    model_name:str
    def __init__(self, api_key, base_url,model_name:str,model_prompt:str,user_id:str,json_output=False):
        self.model = OpenAI(
            api_key=api_key,
            base_url= base_url,
        )
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
        if(self.json_output):
            response=self.model.chat.completions.create(
                model= self.model_name,
                messages= final_message,
                response_format={'type':self.type},
                #strem=
            )
        else:
            response=self.model.chat.completions.create(
                            model= self.model_name,
                            messages= final_message,
                                
                        )
        if(self.json_output):       
            return json.loads(response.choices[0].message.content)
        return response.choices[0].message.content