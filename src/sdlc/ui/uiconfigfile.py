class Config:
    def __init__(self):
        self.page_title = "AI-Driven SDLC"
        self.page_description = "SDLC automation system"
        self.llm_options = ["Groq"]
        self.groq_model_options = [
            "mixtral-8x7b-32768",
            "llama-3.3-70b-versatile",
            "llama-3.3-70b-versatile",
            "whisper-large-v3-turbo"
        ]
        self.default_groq_model = "whisper-large-v3-turbo"
    
    def get_page_title(self):
        return self.page_title
    
    def get_page_description(self):
        return self.page_description
    
    def get_llm_options(self):
        return self.llm_options
    
    def get_groq_model_options(self):
        return self.groq_model_options
    
    def get_default_groq_model(self):
        return self.default_groq_model