from docx import Document
#doc = Document("test.docx")


class ReadFile:
    text:str
    def __init__(self):
        pass
    def read_by_docx(self,file_path:str):
        self.text=str()
        doc=Document(file_path)
        for p in doc.paragraphs:
            if p.text=='':
                continue
            self.text+=p.text+'\n'
        return self.text
    def read_by_markdown(self,file_path:str):
        self.text=str()
        with open(file_path,'r',encoding='utf-8') as f:
            self.text=f.read()
            return self.text
#rf=ReadFile()
#rf.read_by_docx('喜羊羊_简历.docx')
#print(rf.text)