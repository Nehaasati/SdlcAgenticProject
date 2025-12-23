from pydantic import BaseModel, Field
from src.sdlc.state.state import State
import importlib
import subprocess
import webbrowser
import sys
import streamlit as st
from langchain_core.messages import HumanMessage, SystemMessage
from src.sdlc.state.state import SDLC
from src.sdlc.LLMS.groq_llm import GroqLLM
from typing import Literal
from langgraph.graph import START,END,StateGraph
max_iterations = 3

class code(BaseModel):
    """Code output"""
    prefix: str = Field(description="Description of the problem and approach")
    imports: str = Field(description="Code block import statements")
    code: str = Field(description="Code block not including import statements")
    # description = "Schema for code solutions to questions about LCEL." 

class SDLCNode:
    def __init__(self,model):
        self.llm = model
        self.code_gen_chain = model.with_structured_output(code, include_raw=False)
        
    def Initial_requirements(self,state:SDLC)->SDLC:
        """user provide intial input collect project requiremntfrom user_input"""
        if not state.requirements:
          state.requirements=input("enter project requirements:")
          return state.model_copy(update={"requirements": state.requirements})


    def User_story(self,state:SDLC)->SDLC:
      """write detail user story according given input and feedback"""
    
      base_prompt = [
        "Generate a detailed user story with:",
        "1. User Story (As a [role], I want [feature], so that [benefit])",
        "2. Acceptance Criteria (numbered list)",
        "3. Error Handling Scenarios (must include):",
        "   - System errors",
        "   - User input errors",
        "   - Network/resource errors",
        "4. Definition of Done",
        f"\nRequirements: {state.requirements}"
        ]
      if state.user_story_feedback!="no  feedback yet.":
        feedback = state.user_story_feedback
        if "reject:" in feedback:
            feedback = feedback.replace("reject:", "").strip()
            print(f"Processing Feedback: {feedback}")
            
            base_prompt.extend([
                "\nPrevious Story:",
                state.User_story,
                "\nFeedback to address:",
                feedback,
                "\nRevision Guidelines:",
                "1. Address the feedback completely",
                "2. Maintain existing good elements",
                "3. Include specific error scenarios",
                "4. Ensure measurable acceptance criteria"
            ])


        messages= [

        SystemMessage(content="\n".join([
         
         "you are expert agile coach for writing user story",
         "focus on creating compehnsive with error handling,",
         "each rivision should improve upon privious one"

        ])),
       HumanMessage(content="\n".join(base_prompt))
        ]
        try:
          revised_story = GroqLLM.invoke(messages).content
        #print("\nGenerated User Story:\n")
          print(revised_story)
          print(f"✅ User Story Generated ({len(revised_story)} chars)")
          print(f"Preview: {revised_story[:150]}...")
        # Update state with new story
          return state.model_copy(update={
          "User_story": revised_story,
          "approval_status": "pending"
           })

        except Exception as e:
         print(f"Error in story generation: {e}")
         return state.model_copy(update={
            "feedback": f"Error in story generation: {str(e)}"
         })
    
    def product_owner_review(self,state: SDLC) -> SDLC:
      """Handle product owner review of user story"""
      print("PRODUCT OWNER REVIEW - USER STORY")
      print(f"User Story exists: {bool(state.User_story)}")
      print(f"User Story length: {len(state.User_story) if state.User_story else 0}")
    
      print("\nCurrent User Story:")
      print(state.User_story)
      if not state.User_story:
         print("ERROR: No user story to review!")
         return state
    
      print(f"\nUser Story Preview:\n{state.User_story[:200]}...")
    
      while True:
        feedback = input("\nDo you approve this user story? (yes/no): ").strip().lower()
        
        if feedback in ("yes", "ya", "y"):
             print(" User story approved!")
             return state.model_copy(update={
                    "approval_status": "approved",
                    "user_story_feedback": "No user story feedback yet."
                    })

        
        elif feedback in ("no", "not", "n"):
            user_feedback = input("\nProvide feedback for revision: ").strip()
            if user_feedback:
                print(f" Feedback recorded: {user_feedback}")
                return state.model_copy(update={
                    "approval_status": "rejected",
                    "user_story_feedback": user_feedback
                })
            else:
                print("  Please provide feedback to improve the user story.")
        else:
            print(" Invalid input. Please enter 'yes' or 'no'.")


    def design_document(self,state:SDLC)->SDLC:
     """create designe document according to user story and feedback"""
     
     print("NODE: create_design_document")
    
     print(f"User Story exists: {bool(state.User_story)}")
     print(f"Design Feedback: {state.design_feedback}")
     if not state.User_story:
        print("User stories missing. Cannot generate design document.")
        return state

    # Base prompt
     base_content = [
        "# Design Document Template",
        "",
        "Create a detailed design document for these user stories:",
        str(state.User_story),
        "",
        "## Sections to Include:",
        "1. System Architecture Overview",
        "2. Component Design",
        "3. Data Models & Database Schema",
        "4. API Specifications (endpoints, request/response)",
        "5. Security & Authentication",
        "6. Technology Stack",
        "",
        "",
        "## Important Rules",
        "- Do not include any testing sections",
        "- Do not include error handling unless explicitly requested",
        "- Use markdown formatting",
        "",

     ]
     if state.design_feedback != "No design feedback yet.":
        print(f" Incorporating feedback: {state.design_feedback}")
        base_content.extend([
            "",
            "## Previous Design:",
            str(state.design_documents) if str(state.design_documents) else "None",
            "",
            "## Feedback to Address:",
            str(state.design_feedback)
        ])

   
     messages = [
        SystemMessage(content="\n".join([
            "You are a software architect creating clear, structured design documents.",
            "Focus on practical, implementable designs.",
            "Use markdown formatting for better readability.",
            "Strictly follow the requested sections only.",
            "Remove any sections mentioned in feedback."
        ])),
        HumanMessage(content="\n".join(base_content))
     ]
    

     try:
        # Generate design document
        design_doc = GroqLLM.invoke(messages).content
        print("Design Document Generated!")
        print(design_doc)

        # Store the updated design document
        return state.model_copy(update={
            "design_documents": design_doc,
            "design_approval_status": "pending"
            
        })

     except Exception as e:
        print(f"\nError generating design document: {str(e)}")
        return state


     #step 5: create a design review
    def design_review(self,state: SDLC )-> SDLC:
       """Review design documents and approve or reject them."""
       print("\nCurrent Design Document:")
       if not state.design_documents:
          print(" No design document to review!")
          return state
       print(state.design_documents[:300] + "...")
       while True:
        design_feedback = input("\DO you Approve this design document (yes or no):").strip()
        if design_feedback in ("yes","ya"):
            print("Design document approve")
            return state.model_copy(update={
                "design_approval_status":"approved",
                "design_feedback":" yes!"
              
            })
        elif design_feedback in ("not", "no", "n"):
               design_feedback = input("\nProvide feedback: ").strip()
               if design_feedback:
                   print(f" Design feedback recorded: {design_feedback}")
                   return state.model_copy(update={
                       "design_approval_status": "rejected",
                       "design_feedback": design_feedback
                   })
               else:
                   print("⚠️ Please provide feedback.")
       else:
               print("❌ Invalid input. Please enter 'yes' or 'no'.")

    def generate_code(self,state: SDLC) -> SDLC:  
       """Generate code based on design document"""
    
       print("\n" + "="*60)
       print("NODE: generate_code")
       print("="*60)
       print(f"Design doc exists: {bool(state.design_documents)}")
    
       if not state.design_documents:
         print(" Design document missing. Cannot generate code.")
         return state
    
    
       base_prompt = [
         "Generate production-ready code based on this design document:",
         state.design_documents,
         "",
         "## Requirements:",
         "1. Write clean and well-structured code",
         "2. Include proper error handling",
         "3. Add comprehensive comments",
         "4. Follow best practices and design patterns",
         "5. Include input validation",
         "6. Add logging where appropriate",
         "7. Make code modular and testable",
         "",
         "## Code Structure:",
         "- Main application logic",
         "- Helper functions/classes",
         "- Configuration management",
         "- Error handling utilities",
         "",
         "Generate complete, runnable code with all necessary imports and setup."
        ]
       if state.code_approval_status!= "No code feedback yet.":
         print(f" Incorporating feedback: {state.code_review}")
         base_prompt.extend([ 
             "",
             "## Previous Code:",
             state.generated_code if state.generated_code else "None",
             "",
             "## Feedback to Address:",
             state.code_review,
             "",
             "Revise the code to address all feedback points."
            ])

         messages = [
             SystemMessage(content="\n".join([
             "You are an expert software developer writing production-ready code.",
             "Focus on code quality, maintainability, and best practices.",
             "Include proper error handling and validation.",
             "Write code that is well-commented and easy to understand.",
             "Follow SOLID principles and design patterns where appropriate."
           ])),
         HumanMessage(content="\n".join(base_prompt))  
         ]
    
         try:
          generated_code = GroqLLM.invoke(messages).content
          print(" CODE GENERATED!")
          print(generated_code[:200] + "...")
        
          return state.model_copy(update={
            "generated_code": generated_code,  
            "code_approval_status": "pending"
         })

         except Exception as e:
          print(f"Error generating code: {str(e)}")
          return state
    def code_review(self,state: SDLC) -> SDLC:
        """Review generated code and collect feedback"""
        print("\n NODE: code_review - STARTING") 
        if not state.generated_code:  
          print(" No code to review!")
          return state 
        print(f"Design approval status: {state.design_approval_status}") 
        print("SENIOR DEVELOPER REVIEW - CODE")
        print(state.generated_code[:300] + "...")
        print("\nGenerated Code:")
        print(state.generated_code)
    
    
        while True:
         code_feedback = input("\nDo you approve this code? (yes/no): ").strip().lower()
        
         if code_feedback in ("yes", "ya", "y"):
             print(" Code approved! Ready for deployment!")
             return state.model_copy(update={
                 "code_approval_status": "approved",
                 "code_feedback": "No code feedback yet."
             })
        
         elif code_feedback in ("no", "not", "n"):
             code_feedback = input("\nProvide feedback for code revision: ").strip()
             if code_feedback:
                 print(f"✗ Code feedback recorded: {code_feedback}")
                 return state.model_copy(update={
                     "code_approval_status": "rejected",
                     "code_feedback": code_feedback
                 })
             else:
                 print("  Please provide feedback to improve the code.")
         else:
             print(" Invalid input. Please enter 'yes' or 'no'.")


    def genrated_test_case(self,state: SDLC) -> SDLC:
       """Generate comprehensive test cases for the code"""
       print("\n" + "="*60)
       print(" STEP 8: Test Case Generation")
       print("="*60)
    
       #  FIX: Check for generated_CODE, not generated_testcase
       if not state.generated_code:
         print("❌ ERROR: No code available to generate tests for!")
         return state
    
       print(f"✓ Code exists ({len(state.generated_code)} characters)")
    
       base_prompt = [
         "Generate comprehensive, executable test cases for this code:",
         "",
         "```",
         state.generated_code,
         "```",
         "",
         "**Test Requirements:**",
         "1. Use pytest or unittest framework",
         "2. Test all main functionality",
          "3. Include positive test cases",
         "4. Include negative/edge test cases",
         "5. Test error handling",
         "6. Use clear, descriptive test names",
         "7. Include setup and teardown if needed",
         "8. Add assertions for all expected outcomes",
         "",
         "**Format:**",
         "- Complete, runnable test file",
         "- Proper imports",
         "- Test class organization",
         "- Individual test methods"
        ]
    
        # Add revision context if feedback exists
       if state.test_case_feedback != "No test case feedback yet.":
         print(f"Incorporating feedback: {state.test_case_feedback[:100]}...")
         base_prompt.extend([
             "",
             "**Previous Test Cases:**",
             state.generated_testcase or "None",
             "",
             "**Feedback to Address:**",
             state.test_case_feedback,
             "",
             "**Instructions:** Add missing tests and fix issues mentioned in feedback."
          ])
    
         messages = [
           SystemMessage(content="\n".join([
             "You are a senior QA engineer specializing in test automation.",
             "Write thorough, maintainable test suites.",
             "Cover all functionality including edge cases.",
             "Follow testing best practices."
           ])),
         HumanMessage(content="\n".join(base_prompt))
         ]

         try:
          test_cases = GroqLLM.invoke(messages).content
          print(f"Test cases generated ({len(test_cases)} characters)")
          print(f" Preview:\n{test_cases[:400]}...\n")
        
          return state.model_copy(update={
              "generated_testcase": test_cases,
              "testcase_approval_status": "pending"
          })
    
         except Exception as e:
          print(f" Error generating test cases: {e}")
          return state

    def review_testcase(self,state:SDLC)->SDLC:
       """Ai reviwe the genrated test caseand decide to approve or rejected"""
       print("testcase review")
       if not state.generated_testcase:
         print("no test case for review")
         return state
       print(state.generated_testcase)
       while True:

        test_case_feedback = input("\n do you approve this test case(yes\no)")

        if test_case_feedback in ("yes", "ya", "y"):
              print(" Code approved! Ready for deployment!")
              return state.model_copy(update={
                  "testcase_approval_status": "approved",
                 "test_case_feedback": "No code feedback yet."
              })
        
        elif test_case_feedback in ("no", "not", "n"):
              test_case_feedback = input("\nProvide feedback for code revision: ").strip()
              if test_case_feedback:
                  print(f"✗ Code feedback recorded: {test_case_feedback}")
                  return state.model_copy(update={
                      "testcase_approval_status": "rejected",
                      "test_case_feedback": test_case_feedback
                 })
              else:
                  print("  Please provide feedback to improve the code.")
        else:
              print(" Invalid input. Please enter 'yes' or 'no'.")

    def qa_testing(self,state: SDLC) -> SDLC:
       """AI executes test cases and validates code quality"""
       print("\n" + "="*70)
       print("PHASE 6: QA TESTING & VALIDATION")
       print("="*70)
    
       if not state.generated_code or not state.generated_testcase:
          print(" Missing code or test cases. Skipping QA testing.")
          return state.model_copy(update={
             "qa_test_results": "SKIPPED: Missing prerequisites",
             "QA_approval_status": "pending"
          })
    
       print("✓ Executing comprehensive QA testing...")
    
       prompt_content = f"""You are a senior QA engineer. Execute the following test cases on the provided code and provide a detailed test execution report.

       Generated Code:
       ```
       {state.generated_code}
        ```

       Test Cases to Execute:
        ```
       {state.generated_testcase}
        ```

     Original Requirements:
     {state.requirements}

     User Story:
     {state.User_story}
     """
    
       if state.QA_feedback and state.QA_feedback != "No QA feedback yet.":
         print(" Re-validating previous QA issues...")
         prompt_content += f"""

         Previous QA Feedback (Verify These Are Fixed):
         {state.QA_feedback}

          CRITICAL: Check if previously identified issues are resolved.
          """
    
         prompt_content += """

         Testing Instructions:

         1. Code Analysis:
         - Review code logic against requirements
         - Check for potential bugs
         - Validate error handling
         - Assess code quality

         2. Test Execution Simulation:
          - Determine if each test would PASS or FAIL
          - Identify specific failure reasons
          - Check edge cases
          - Validate error scenarios

         3. Quality Assessment:
         - Code completeness
         - Security vulnerabilities
         - Performance concerns
         - Best practices compliance

         Report Format:

         Decision: [pass/fail]

         Test Execution Summary:
         - Total Tests: [number]
         - Passed: [number]
         - Failed: [number]
         - Coverage: [percentage estimate]

          Test Results:

         Passed Tests:
          - test_name_1: Brief reason why it passes
           - test_name_2: Brief reason why it passes

          Failed Tests (if any):
         - test_name_3: Specific failure reason and what's wrong in code
         - test_name_4: Specific failure reason and what's wrong in code

         Code Quality Issues:
         Critical:
         - [Issue with line reference]

         Medium:
         - [Issue with line reference]

         Minor:
        - [Issue with line reference]

         Security Concerns:
         - [Security issue 1]
         - [Security issue 2]

         Performance Observations:
         - [Performance concern 1]
         - [Performance concern 2]

         Recommendations:
         1. [Specific recommendation]
         2. [Specific recommendation]

         ### Overall Assessment:
         [2-3 sentences summarizing code quality and test results]

         **Decision Criteria:**
         - Choose "pass" ONLY if:
          * ALL tests pass
         * No critical issues
         * Code meets requirements
         * Security is acceptable
         - Choose "fail" if ANY:
         * Test fails
         * Critical bug exists
         * Security vulnerability found
           * Requirements not met
           """
    
         messages = [
          SystemMessage(content="""You are a meticulous senior QA engineer with expertise in:
         - Test execution and validation
         - Code quality assessment
         - Security analysis
         - Performance evaluation

         Be thorough, critical, and provide actionable feedback."""),
         HumanMessage(content=prompt_content)
         ]
    
         try:
            qa_results = GroqLLM.invoke(messages).content
        
            print("\n" + "="*70)
            print("QA TEST RESULTS")
            print("="*70)
            print(qa_results)
            print("="*70)
        
            # Parse decision
            decision = "fail"  # Default to fail for safety
            for line in qa_results.split('\n'):
             if 'Decision:' in line or 'decision:' in line:
               if 'pass' in line.lower():
                   decision = "pass"
                   print("\n QA TESTING PASSED!")
             else:
                    decision = "fail"
                    print("\nQA TESTING FAILED - Issues found!")
             break
        
            approval_status = "approved" if decision == "pass" else "rejected"
            qa_feedback = qa_results if decision == "fail" else "All tests passed successfully"
        
            return state.model_copy(update={
            "qa_test_results": qa_results,
            "QA_approval_status": approval_status,
            "QA_feedback": qa_feedback
             })
         except Exception as e:
       
          print(f"\n Error during QA testing: {str(e)}")
         return state.model_copy(update={
                 "qa_test_results": f"ERROR: {str(e)}",
                 "QA_approval_status": "pending",
                 "QA_feedback": f"QA testing error: {str(e)}"
             })   
    def user_story_routing(self,state: SDLC) -> Literal["User_story", "design_document"]:
        if state.approval_status == "approved":
          return "design_document"
        return "User_story"


    def design_routing(self,state: SDLC) -> Literal["design_document", "generate_code"]:
       if state.design_approval_status == "approved":
         return "generate_code"
       return "design_document"


    def code_routing(self,state: SDLC) -> Literal["generate_code", "genrated_test_case"]:
      """Route after code review - FIXED"""
      print(f"\n ROUTING: code_routing")
      print(f"   Code Approval: {state.code_approval_status}")
    
      if state.code_approval_status == "approved":
          print("Going to: genrated_test_case")
          return "genrated_test_case"  
      else:
          print(" Going to: generate_code")
          return "generate_code"


    def test_case_routing(self,state: SDLC) -> Literal["genrated_test_case", "qa_testing"]:
      """Route after test case review """
      print(f"\n ROUTING: test_case_routing")
      print(f"   Test Case Approval: {state.testcase_approval_status}")
    
      if state.testcase_approval_status == "approved":
          print("   Going to: qa_testing")
          return "qa_testing"  
      else:
          print("   Going to: genrated_test_case")
          return "genrated_test_case"
    def qa_test_route(self,state: SDLC) -> Literal["END", "generate_code"]:
       """ Routes based on QA test results: Pass -> Save Files & END, Fail -> Fix Code."""
       print(f"\nROUTING: QAtest_case_routing")
       print(f"QA Test Case Approval: {state.QA_approval_status}")
       if state.QA_approval_status == "approved":
          return END
       return "generate_code"
           
