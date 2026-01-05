import streamlit as st
import uuid
from src.sdlc.ui.streamlitui.load_ui import LoadStreamlitUI
from src.sdlc.LLMS.groq_llm import GroqLLM
from src.sdlc.graph.graph_builder import GraphBuilder
from src.sdlc.state.state import SDLC


def load_sdlc_app():
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = str(uuid.uuid4())
    if "workflow_started" not in st.session_state:
        st.session_state.workflow_started = False
    if "requirements" not in st.session_state:
        st.session_state.requirements = ""
    
    ui = LoadStreamlitUI()
    user_input = ui.load_streamlit_ui()

    if not user_input:
        st.error("Error: Failed to load user input.")
        return

    st.markdown("---")
    st.subheader("🔄 SDLC Workflow Automation")
    
    if not st.session_state.workflow_started:
        st.info("Enter your project requirements below")
        user_message = st.chat_input("📝 Enter requirements:")
        
        if user_message:
            st.session_state.requirements = user_message
            st.session_state.workflow_started = True
            st.rerun()
    
    else:
        with st.expander("📋 Requirements", expanded=False):
            st.write(st.session_state.requirements)
        
        try:
            obj_llm_config = GroqLLM(user_controls_input=user_input)
            model = obj_llm_config.get_llm_model()
            
            if not model:
                st.error("LLM initialization failed")
                return

            graph_builder = GraphBuilder(model)
            graph = graph_builder.setup_graph()
            
            config = {"configurable": {"thread_id": st.session_state.thread_id}}
            
            try:
                state = graph.get_state(config)
                
                if not state.values or not state.values.get('requirements'):
                    st.info("Initializing...")
                    initial_state = SDLC(requirements=st.session_state.requirements)
                    graph.update_state(config, initial_state.model_dump())
                    st.success("Initialized!")
                
                st.markdown("### 🎯 Status")
                current_state = graph.get_state(config)
                
                if current_state.next:
                    next_node = current_state.next[0]
                    st.warning(f"⏸️ Paused at: {next_node}")
                    st.info("💡 Check TERMINAL for prompts!")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Continue", type="primary"):
                            with st.spinner("Processing..."):
                                try:
                                    for event in graph.stream(None, config, stream_mode="values"):
                                        pass
                                    st.success("Done!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {e}")
                    
                    with col2:
                        if st.button("New Project"):
                            st.session_state.workflow_started = False
                            st.session_state.thread_id = str(uuid.uuid4())
                            st.session_state.requirements = ""
                            st.rerun()
                
                elif current_state.values.get('qa_test_results'):
                    st.success("🎉 Completed!")
                    
                    st.markdown("### 📦 Artifacts")
                    
                    tab1, tab2, tab3, tab4, tab5 = st.tabs([
                        "User Story", "Design", "Code", "Tests", "QA"
                    ])
                    
                    with tab1:
                        if current_state.values.get('User_story'):
                            st.markdown(current_state.values['User_story'])
                            st.download_button("Download", current_state.values['User_story'], "user_story.md")
                    
                    with tab2:
                        if current_state.values.get('design_documents'):
                            st.markdown(current_state.values['design_documents'])
                            st.download_button("Download", current_state.values['design_documents'], "design.md")
                    
                    with tab3:
                        if current_state.values.get('generated_code'):
                            st.code(current_state.values['generated_code'], language="python")
                            st.download_button("Download", current_state.values['generated_code'], "code.py")
                    
                    with tab4:
                        if current_state.values.get('generated_testcase'):
                            st.code(current_state.values['generated_testcase'], language="python")
                            st.download_button("Download", current_state.values['generated_testcase'], "tests.py")
                    
                    with tab5:
                        if current_state.values.get('qa_test_results'):
                            st.markdown(current_state.values['qa_test_results'])
                            st.download_button("Download", current_state.values['qa_test_results'], "qa.md")
                    
                    if st.button("New Project", type="primary"):
                        st.session_state.workflow_started = False
                        st.session_state.thread_id = str(uuid.uuid4())
                        st.session_state.requirements = ""
                        st.rerun()
                
                else:
                    st.info("Ready to start!")
                    
                    if st.button("▶️ Start Workflow", type="primary"):
                        with st.spinner("Starting..."):
                            try:
                                for event in graph.stream(None, config, stream_mode="values"):
                                    pass
                                st.success("Started!")
                                st.info("Check TERMINAL!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")
            
            except Exception as e:
                st.error(f"State error: {e}")
                if st.button("Reset"):
                    st.session_state.workflow_started = False
                    st.session_state.thread_id = str(uuid.uuid4())
                    st.rerun()

        except ValueError as e:
            st.error(f"Config error: {e}")
            st.info("Add API key in sidebar")
        
        except Exception as e:
            st.error(f"Error: {e}")
            if st.button("Refresh"):
                st.session_state.workflow_started = False
                st.session_state.thread_id = str(uuid.uuid4())
                st.rerun()