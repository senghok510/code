from langchain_openai import ChatOpenAI

from dotenv import load_dotenv


load_dotenv()


class Model:
    def __init__(self,model_name):
        self.model = model_name
    
    def load_model(self):
        
        model = ChatOpenAI(model= self.model)
        return model
    
    
    
    
    


