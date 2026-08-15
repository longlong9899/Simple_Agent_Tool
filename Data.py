import json
from filelock import FileLock
from pathlib import Path
import os
import logging
logger=logging.getLogger('Simple_Agent_Tool.Data')
    
class Data:
    #file_name:str
    file_path:Path
    def __init__(self,file_path:Path):
        #self.file_name=file_name
        self.file_path= file_path
        lock=FileLock(self.file_path.with_suffix('.lock'))
        logger.info(f"初始化数据文件{self.file_path}")
        try:
            with lock:
                if not self.file_path.exists():
                    self.file_path.parent.mkdir(parents=True,exist_ok=True)
                    temp_path=self.file_path.with_suffix('.tmp')
                    with open(temp_path,'w',encoding='utf-8') as f:
                        logger.info(f"开始写入临时文件{temp_path}")
                        json.dump({},f,indent=2,ensure_ascii=False)
                        f.flush()
                        os.fsync(f.fileno())
                    os.replace(temp_path,self.file_path)
                    logger.info(f"临时文件{temp_path}替换到{self.file_path}完成")
                else:
                    logger.info(f"数据文件{self.file_path}原先存在，无需初始化")
                logger.info(f"数据文件{self.file_path}初始化完成")
        except Exception as e:
            logger.error(f"数据文件{self.file_path}初始化失败：{e}")
            raise 
            
           
    def save(self,data_dict:dict):
        #print(data_list)
        lock=FileLock(self.file_path.with_suffix('.lock'))
        with lock:
            logger.info(f"开始保存数据文件{self.file_path}")
            temp_path=self.file_path.with_suffix('.tmp')
            with open(temp_path,'w',encoding='utf-8',) as f:
                logger.info(f"开始写入临时文件{temp_path}")
                json.dump(data_dict,f,indent=2,ensure_ascii=False)
                f.flush()
                os.fsync(f.fileno())
                logger.info(f"临时文件{temp_path}写入完成")
            logger.info(f"开始替换临时文件{temp_path}到{self.file_path}")
            os.replace(temp_path,self.file_path)
            logger.info(f"临时文件{temp_path}替换到{self.file_path}完成")
            #f.write(text)
            #print(data_list)
            logger.info(f"数据文件{self.file_path}保存完成")
            return True
         
    def load(self):
        lock=FileLock(self.file_path.with_suffix('.lock'))
        try:
            with lock:
                with open(self.file_path,'r',encoding='utf-8') as f:
                    logger.info(f"开始读取数据文件{self.file_path}")
                    text=f.read()
                    logger.info(f"数据文件{self.file_path}读取完成")
                    return json.loads(text)
        except Exception as e:
           # print("文件读取失败")
             logger.error(f"数据文件{self.file_path}无法读取")
             raise 
             
    
