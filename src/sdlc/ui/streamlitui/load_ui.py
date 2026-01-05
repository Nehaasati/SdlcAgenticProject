import streamlit as st
import os
from src.sdlc.ui.uiconfigfile import Config


class LoadStreamlitUI:
    def __init__(self):
        self.config = Config()
        self.user_controls = {}

    def load_streamlit_ui(self):
        st.set_page_config(
            page_title=self.config.get_page_title(), 
            layout="wide"
        )
        
        st.header(self.config.get_page_title())
        st.markdown(self.config.get_page_description())
        
        if 'timeframe' not in st.session_state:
            st.session_state.timeframe = ''
        if 'IsFetchButtonClicked' not in st.session_state:
            st.session_state.IsFetchButtonClicked = False
        if 'IsSDLC' not in st.session_state:
            st.session_state.IsSDLC = False
        
        with st.sidebar:
            st.title("⚙️ Configuration")
            
            llm_options = self.config.get_llm_options()
            self.user_controls["selected_llm"] = st.selectbox("LLM", llm_options)

            if self.user_controls["selected_llm"] == 'Groq':
                st.markdown("### Groq Config")
                
                model_options = self.config.get_groq_model_options()
                selected_model = st.selectbox("Model", model_options, index=0)
                self.user_controls["selected_groq_model"] = selected_model.strip().rstrip(',')
                
                st.markdown("---")
                st.markdown("### API Key")
                
                env_api_key = os.getenv("GROQ_API_KEY", "")
                
                if env_api_key:
                    st.success("✅ Key found")
                    self.user_controls["GROQ_API_KEY"] = env_api_key
                else:
                    api_key_input = st.text_input(
                        "API Key",
                        type="password",
                        placeholder="gsk_..."
                    )
                    
                    if api_key_input:
                        self.user_controls["GROQ_API_KEY"] = api_key_input.strip()
                    else:
                        self.user_controls["GROQ_API_KEY"] = ""
                
                if self.user_controls.get("GROQ_API_KEY"):
                    key = self.user_controls["GROQ_API_KEY"]
                    if not key.startswith('gsk_'):
                        st.error("Key should start with 'gsk_'")
                    elif len(key) < 40:
                        st.warning("Key too short")
                    else:
                        st.success("✅ Key OK")
                else:
                    st.warning("Enter API key")
                    st.info("Get key: https://console.groq.com/keys")
        
        return self.user_controls