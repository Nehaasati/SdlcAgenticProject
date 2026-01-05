import os
import streamlit as st
from langchain_groq import ChatGroq


class GroqLLM:
    def __init__(self, user_controls_input):
        self.user_controls_input = user_controls_input

    def get_llm_model(self):
        try:
            groq_api_key = self.user_controls_input.get('GROQ_API_KEY', '')
            
            if not groq_api_key:
                groq_api_key = os.environ.get("GROQ_API_KEY", '')
            
            if not groq_api_key:
                st.error("API Key missing!")
                raise ValueError("API key required")
            
            if not groq_api_key.startswith('gsk_'):
                st.error("Invalid API Key format!")
                raise ValueError("Invalid API key")
            
            if len(groq_api_key) < 40:
                st.error("API Key too short!")
                raise ValueError("API key incomplete")
            
            selected_groq_model = self.user_controls_input.get('selected_groq_model', 'mixtral-8x7b-32768')
            
            llm = ChatGroq(
                api_key=groq_api_key,
                model=selected_groq_model,
                temperature=0.7,
                max_tokens=4096
            )
            
            try:
                llm.invoke("Test")
                st.success("✅ Connected to Groq!")
            except Exception as test_error:
                if "401" in str(test_error):
                    st.error("❌ Invalid API Key!")
                    st.info("Get new key: https://console.groq.com/keys")
                    raise ValueError("Invalid API Key")
                else:
                    raise
            
            return llm

        except ValueError:
            raise
        
        except Exception as e:
            st.error(f"Error: {str(e)}")
            if "401" in str(e):
                st.info("Get key: https://console.groq.com/keys")
            elif "404" in str(e):
                st.info("Try: mixtral-8x7b-32768")
            raise ValueError(f"LLM error: {str(e)}")