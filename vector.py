from sentence_transformers import SentenceTransformer
import numpy as np
from numpy.typing import NDArray
from .Data import Data
from .Model import Model_no_history,AsyncModel_no_history
from .ReadFile import ReadFile
from pathlib import Path

'''
    np.dot(a, b)          # 点乘
    np.linalg.norm(a)     # a 的模长
    np.linalg.norm(b)     # b 的模长
'''
def cosine_similarity(a: NDArray, b: NDArray) -> float:
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return np.dot(a, b) / (norm_a * norm_b)
    #return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
class TextVector:
    vector: NDArray
    text:str
    _model=None
    def __init__(self,text:str):
        if TextVector._model is None:
            TextVector._model = SentenceTransformer("BAAI/bge-small-zh-v1.5")
        self.vector=TextVector._model.encode(text)
        self.text=text
    def to_dict(self):
        return {
            'vector':self.vector.tolist(),
            'text':self.text
        }
    
class KnowledgeVector:
    knowledge_vector_list:list[dict] 
    data:Data
    #data_file_name:str=None
    data_file_path:Path
    def __init__(self,data_file_path:Path):
        self.knowledge_vector_list=[]
        self.data_file_path= data_file_path
        #self.data_file_path=data_file_name+'.json'
        self.data=Data(self.data_file_path)
        self.knowledge_vector_list=self.data.load()
        #print('初始化知识库')
    def create_by_text(self):
        pass
    def create_by_markdown(self):
            pass
    def create_by_docx(self,read_file_path,api_key:str,base_url:str,model_name:str):
        split_promote='''
        
# 文本语义拆分任务提示词模板

## 任务描述
你是专业文本语义分割处理器，负责对输入长文本进行语义分块，用于知识库向量化预处理。

## 强制执行规则
1. **分割规则**：依据语义自然切分，禁止在完整句子中间强行截断，保证单块内容语义完整独立。
2. **字数约束**：每个文本片段汉字数量控制在 **200～300字**。
3. **内容约束**：禁止修改、增删原文文字，只做文本切割。
4. **输出格式约束**
    - 只输出纯净JSON，不要任何开场白、解释文字、注释；
    - 禁止使用 ```json 代码块包裹结果；
    - 最外层是一维数组，数组内每一项为字符串。

## 标准输出示例
```json
["第一段分割文本内容","第二段分割文本内容","第三段分割文本内容"]
'''
        #print('调用分段大模型')
        model=Model_no_history(api_key, base_url,model_name,split_promote,"split_model",json_output=True)
        #print('调用完成')
        rf=ReadFile()
        rf.read_by_docx(read_file_path)
        text=rf.text
        res=model.invoke(text)
         
        for content in res:
            vector=TextVector(content)
            self.add(vector)
        #print(res)
    async def async_create_by_docx(self,read_file_path,api_key:str,base_url:str,model_name:str):
            split_promote='''
            
    # 文本语义拆分任务提示词模板
    
    ## 任务描述
    你是专业文本语义分割处理器，负责对输入长文本进行语义分块，用于知识库向量化预处理。
    
    ## 强制执行规则
    1. **分割规则**：依据语义自然切分，禁止在完整句子中间强行截断，保证单块内容语义完整独立。
    2. **字数约束**：每个文本片段汉字数量控制在 **200～300字**。
    3. **内容约束**：禁止修改、增删原文文字，只做文本切割。
    4. **输出格式约束**
        - 只输出纯净JSON，不要任何开场白、解释文字、注释；
        - 禁止使用 ```json 代码块包裹结果；
        - 最外层是一维数组，数组内每一项为字符串。
    
    ## 标准输出示例
    ```json
    ["第一段分割文本内容","第二段分割文本内容","第三段分割文本内容"]
    '''
            #print('调用分段大模型')
            model=AsyncModel_no_history(api_key, base_url,model_name,split_promote,"split_model",json_output=True)
            #print('调用完成')
            rf=ReadFile()
            rf.read_by_docx(read_file_path)
            text=rf.text
            res=await model.invoke(text)  
            for content in res:
                vector=TextVector(content)
                self.add(vector)
    def add(self,vector:TextVector):
        self.knowledge_vector_list.append(vector.to_dict())
        self.data.save(self.knowledge_vector_list)
    def search(self,vector:NDArray,top_k:int=1):
        similarities=[]
        #error:vector is not a numpy array
        for v in self.knowledge_vector_list:
            similarities.append({'TextVector':v,'similarity':cosine_similarity(vector,np.array(v['vector']))})
        similarities.sort(reverse=True,key=lambda x:x['similarity'])
        ret_list=[]
        for ret in similarities[:top_k]:
            ret_list.append(ret['TextVector'])
        return ret_list

if __name__ == '__main__':
    # temp=KnowledgeVector('知识库测试.1')
    # temp.create_by_docx('喜羊羊_简历.docx')
    pass




