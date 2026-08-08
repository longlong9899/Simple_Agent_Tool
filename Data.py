import json
from filelock import FileLock
from pathlib import Path
class Data:
    #file_name:str
    file_path:Path
    def __init__(self,file_path:Path):
        #self.file_name=file_name
        self.file_path= file_path
        lock=FileLock(self.file_path.with_suffix('.lock'))
        try:
            with lock:
                with open(self.file_path,'x',encoding='utf-8') as f:
                    pass
        except FileExistsError:
            pass
             
       
           
    def save(self,data_list:list):
        #print(data_list)
        lock=FileLock(self.file_path.with_suffix('.lock'))
        with lock:
            with open(self.file_path,'w',encoding='utf-8',) as f:
                text=json.dump(data_list,f,indent=2,ensure_ascii=False)
            #f.write(text)
            #print(data_list)
            return True
         
    def load(self):
        lock=FileLock(self.file_path.with_suffix('.lock'))
        try:
            with lock:
              with open(self.file_path,'r',encoding='utf-8') as f:
                    text=f.read()
                    return json.loads(text)
        except FileNotFoundError:
           # print("文件读取失败")
            return []
             
    
