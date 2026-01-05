SoftwareAgentic - AI-Powered SDLC Automation
An intelligent Software Development Life Cycle automation system that leverages LangGraph and Groq to streamline the entire development workflow from requirements to deployment.

<img width="207" height="955" alt="image" src="https://github.com/user-attachments/assets/b4fbb381-30ab-4778-9257-ac9e5bc6b029" />


🎯 Overview
SoftwareAgentic automates the complete SDLC process using AI agents, transforming project requirements into production-ready code with automated reviews, testing, and quality assurance. The system orchestrates multiple AI agents through a structured workflow, ensuring comprehensive coverage of all development phases.
✨ Key Features

Automated User Story Generation: Converts requirements into detailed user stories with acceptance criteria
Intelligent Design Documentation: Creates comprehensive architecture and design documents
Code Generation: Produces production-ready, well-structured code with error handling
Test Case Automation: Generates comprehensive test suites covering edge cases
AI-Powered QA: Automated quality assurance and validation
Human-in-the-Loop: Interactive review checkpoints at each phase
State Persistence: Redis-backed state management for workflow continuity

🏗️ Architecture
Project Structure
SoftwareAgentic/
├── src/
│   ├── sdlc/
│   │   ├── graph/          # LangGraph workflow definitions
│   │   ├── nodes/          # Custom workflow nodes
│   │   ├── state/          # State management
│   │   ├── LLMS/           # LLM configurations
│   │   └── ui/             # Streamlit interface
├── cache/                  # Redis cache implementation
└── .env                    # Environment configuration
🛠️ Tech Stack
Backend

Python: Core application logic
LangGraph: Agentic AI workflow orchestration
FastAPI: RESTful API endpoints
Redis: State and checkpoint caching
LangSmith: Graph debugging and monitoring
Groq: High-performance LLM inference

Frontend

Streamlit: Interactive web interface
SwiftUI: Native iOS/macOS client (optional)

AI Models

Mixtral-8x7B: Primary language model (Groq)
Llama 3.3 70B: Alternative high-quality model

🚀 Quick Start
Prerequisites
bashPython 3.9+
Redis server
Groq API key
Installation

Clone the repository:

bashgit clone https://github.com/yourusername/SoftwareAgentic.git
cd SoftwareAgentic

Install dependencies:

bashpip install -r requirements.txt

Configure environment:

bashcp .env.example .env
# Add your GROQ_API_KEY

Start Redis:

bashredis-server

Run the application:

bashstreamlit run app.py
📖 Usage

Enter Requirements: Describe your project in natural language
Review User Story: Approve or provide feedback in terminal
Review Design: Validate architecture and design decisions
Review Code: Inspect generated code quality
Review Tests: Verify test coverage and scenarios
QA Validation: Automated quality assurance runs
Download Artifacts: Export all generated documents and code

🔄 Workflow
The system follows a structured workflow with validation at each stage:
Requirements → User Story → Design Document → Code Generation → 
Test Cases → QA Testing → Production-Ready Output
Each phase includes human review checkpoints, allowing iterative refinement based on feedback.
🎨 Features in Detail
State Management: Redis-backed persistence ensures workflow continuity across sessions, enabling pause/resume functionality.
Multi-Model Support: Flexible LLM backend supporting Mixtral, Llama, and other Groq models with configurable parameters.
Interactive Reviews: All feedback is collected via terminal prompts, providing granular control over each development phase.
Artifact Management: Download generated user stories, designs, code, and tests as individual files for integration into existing workflow






output:
<img width="1892" height="962" alt="Screenshot 2026-01-05 140901" src="https://github.com/user-attachments/assets/741cc28c-ff6f-44eb-8e20-8d3a66d996cf" />
<img width="1898" height="909" alt="Screenshot 2026-01-05 140806" src="https://github.com/user-attachments/assets/fc0635e4-8167-43c4-bcf7-136bd9806409" />
