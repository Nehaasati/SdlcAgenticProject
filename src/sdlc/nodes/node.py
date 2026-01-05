from langchain_core.messages import HumanMessage, SystemMessage
from src.sdlc.state.state import SDLC
from typing import Literal
from langgraph.graph import END
from pydantic import BaseModel, Field


class code(BaseModel):
    prefix: str = Field(description="Description of the problem and approach")
    imports: str = Field(description="Code block import statements")
    code: str = Field(description="Code block not including import statements")


class SDLCNode:
    def __init__(self, model):
        self.llm = model
        self.code_gen_chain = model.with_structured_output(code, include_raw=False)

    def User_story(self, state: SDLC) -> SDLC:
        print("\n" + "="*60)
        print("USER STORY GENERATION")
        print("="*60)
        
        base_prompt = [
            "Generate a detailed user story with:",
            "1. User Story (As a [role], I want [feature], so that [benefit])",
            "2. Acceptance Criteria (numbered list)",
            "3. Error Handling Scenarios",
            "4. Definition of Done",
            f"\nRequirements: {state.requirements}"
        ]
        
        if state.user_story_feedback != "no feedback yet.":
            feedback = state.user_story_feedback
            print(f"Applying feedback: {feedback}")
            base_prompt.extend([
                "\nPrevious Story:", state.User_story,
                "\nFeedback:", feedback
            ])

        messages = [
            SystemMessage(content="You are an expert agile coach writing user stories."),
            HumanMessage(content="\n".join(base_prompt))
        ]
        
        try:
            print("Calling LLM...")
            revised_story = self.llm.invoke(messages).content
            print(f"✅ User Story Generated ({len(revised_story)} chars)")
            
            return state.model_copy(update={
                "User_story": revised_story,
                "approval_status": "pending"
            })
        
        except Exception as e:
            print(f"❌ ERROR in story generation: {e}")
            error_msg = str(e)
            
            if "401" in error_msg:
                print("\n⚠️ SOLUTION: Your API key is INVALID")
                print("1. Go to: https://console.groq.com/keys")
                print("2. Delete old keys")
                print("3. Create NEW key")
                print("4. Copy FULL key")
                print("5. Paste in sidebar")
                print("6. Refresh browser (Ctrl+Shift+R)")
            elif "404" in error_msg:
                print("\n⚠️ SOLUTION: Model not found")
                print("Select 'mixtral-8x7b-32768' in sidebar")
            
            return state.model_copy(update={
                "user_story_feedback": f"Error: {str(e)}"
            })

    def product_owner_review(self, state: SDLC) -> SDLC:
        print("\n" + "="*60)
        print("PRODUCT OWNER REVIEW - USER STORY")
        print("="*60)
        print(f"User Story exists: {bool(state.User_story)}")
        print(f"User Story length: {len(state.User_story) if state.User_story else 0}")
        
        if not state.User_story:
            print("\n❌ ERROR: No user story to review!")
            print("\n⚠️ This means the API call FAILED.")
            print("Check the error message above for details.")
            return state
        
        print("\nCurrent User Story:")
        print(state.User_story)
        
        while True:
            feedback = input("\nDo you approve this user story? (yes/no): ").strip().lower()
            
            if feedback in ("yes", "ya", "y"):
                print("✅ User story approved!")
                return state.model_copy(update={
                    "approval_status": "approved",
                    "user_story_feedback": "No user story feedback yet."
                })
            
            elif feedback in ("no", "not", "n"):
                user_feedback = input("\nProvide feedback: ").strip()
                if user_feedback:
                    print(f"📝 Feedback recorded: {user_feedback}")
                    return state.model_copy(update={
                        "approval_status": "rejected",
                        "user_story_feedback": user_feedback
                    })
                else:
                    print("⚠️ Please provide feedback")
            else:
                print("❌ Invalid input. Type 'yes' or 'no'")

    def design_document(self, state: SDLC) -> SDLC:
        print("\n" + "="*60)
        print("DESIGN DOCUMENT GENERATION")
        print("="*60)
        
        if not state.User_story:
            print("❌ No user story. Cannot generate design.")
            return state

        base_content = [
            "Create a detailed design document:",
            str(state.User_story),
            "\n## Include:",
            "1. System Architecture",
            "2. Component Design",
            "3. Data Models",
            "4. API Specs",
            "5. Technology Stack"
        ]
        
        if state.design_feedback != "No design feedback yet.":
            base_content.extend([
                "\nPrevious Design:", str(state.design_documents),
                "\nFeedback:", str(state.design_feedback)
            ])

        messages = [
            SystemMessage(content="You are a software architect."),
            HumanMessage(content="\n".join(base_content))
        ]
        
        try:
            design_doc = self.llm.invoke(messages).content
            print(f"✅ Design Generated ({len(design_doc)} chars)")
            return state.model_copy(update={
                "design_documents": design_doc,
                "design_approval_status": "pending"
            })
        except Exception as e:
            print(f"❌ Error: {e}")
            return state

    def design_review(self, state: SDLC) -> SDLC:
        print("\n" + "="*60)
        print("DESIGN REVIEW")
        print("="*60)
        
        if not state.design_documents:
            print("❌ No design to review!")
            return state
        
        print(state.design_documents[:300] + "...")
        
        while True:
            feedback = input("\nApprove design? (yes/no): ").strip().lower()
            
            if feedback in ("yes", "ya", "y"):
                print("✅ Design approved!")
                return state.model_copy(update={
                    "design_approval_status": "approved",
                    "design_feedback": "yes!"
                })
            
            elif feedback in ("no", "not", "n"):
                user_feedback = input("\nFeedback: ").strip()
                if user_feedback:
                    return state.model_copy(update={
                        "design_approval_status": "rejected",
                        "design_feedback": user_feedback
                    })
            else:
                print("❌ Type 'yes' or 'no'")

    def generate_code(self, state: SDLC) -> SDLC:
        print("\n" + "="*60)
        print("CODE GENERATION")
        print("="*60)
        
        if not state.design_documents:
            print("❌ No design. Cannot generate code.")
            return state
        
        base_prompt = [
            "Generate production-ready code:",
            state.design_documents,
            "\nRequirements:",
            "- Clean, well-structured",
            "- Error handling",
            "- Comments",
            "- Complete and runnable"
        ]
        
        if state.code_review != "No code feedback yet.":
            base_prompt.extend([
                "\nPrevious Code:", state.generated_code or "None",
                "\nFeedback:", state.code_review
            ])

        messages = [
            SystemMessage(content="You are an expert developer."),
            HumanMessage(content="\n".join(base_prompt))
        ]
        
        try:
            code = self.llm.invoke(messages).content
            print(f"✅ Code Generated ({len(code)} chars)")
            return state.model_copy(update={
                "generated_code": code,
                "code_approval_status": "pending"
            })
        except Exception as e:
            print(f"❌ Error: {e}")
            return state

    def code_review(self, state: SDLC) -> SDLC:
        print("\n" + "="*60)
        print("CODE REVIEW")
        print("="*60)
        
        if not state.generated_code:
            print("❌ No code to review!")
            return state
        
        print(state.generated_code[:300] + "...")
        
        while True:
            feedback = input("\nApprove code? (yes/no): ").strip().lower()
            
            if feedback in ("yes", "ya", "y"):
                print("✅ Code approved!")
                return state.model_copy(update={
                    "code_approval_status": "approved",
                    "code_review": "No code feedback yet."
                })
            
            elif feedback in ("no", "not", "n"):
                user_feedback = input("\nFeedback: ").strip()
                if user_feedback:
                    return state.model_copy(update={
                        "code_approval_status": "rejected",
                        "code_review": user_feedback
                    })
            else:
                print("❌ Type 'yes' or 'no'")

    def genrated_test_case(self, state: SDLC) -> SDLC:
        print("\n" + "="*60)
        print("TEST GENERATION")
        print("="*60)
        
        if not state.generated_code:
            print("❌ No code. Cannot generate tests.")
            return state
        
        base_prompt = [
            "Generate test cases:",
            "```",
            state.generated_code,
            "```",
            "\nUse pytest. Include:",
            "- Positive tests",
            "- Negative tests",
            "- Edge cases"
        ]
        
        if state.test_case_feedback != "No test case feedback yet.":
            base_prompt.extend([
                "\nPrevious Tests:", state.generated_testcase or "None",
                "\nFeedback:", state.test_case_feedback
            ])

        messages = [
            SystemMessage(content="You are a QA engineer."),
            HumanMessage(content="\n".join(base_prompt))
        ]
        
        try:
            tests = self.llm.invoke(messages).content
            print(f"✅ Tests Generated ({len(tests)} chars)")
            return state.model_copy(update={
                "generated_testcase": tests,
                "testcase_approval_status": "pending"
            })
        except Exception as e:
            print(f"❌ Error: {e}")
            return state

    def review_testcase(self, state: SDLC) -> SDLC:
        print("\n" + "="*60)
        print("TEST REVIEW")
        print("="*60)
        
        if not state.generated_testcase:
            print("❌ No tests to review!")
            return state
        
        print(state.generated_testcase[:300] + "...")
        
        while True:
            feedback = input("\nApprove tests? (yes/no): ").strip().lower()
            
            if feedback in ("yes", "ya", "y"):
                print("✅ Tests approved!")
                return state.model_copy(update={
                    "testcase_approval_status": "approved",
                    "test_case_feedback": "No code feedback yet."
                })
            
            elif feedback in ("no", "not", "n"):
                user_feedback = input("\nFeedback: ").strip()
                if user_feedback:
                    return state.model_copy(update={
                        "testcase_approval_status": "rejected",
                        "test_case_feedback": user_feedback
                    })
            else:
                print("❌ Type 'yes' or 'no'")

    def qa_testing(self, state: SDLC) -> SDLC:
        print("\n" + "="*60)
        print("QA TESTING")
        print("="*60)
        
        if not state.generated_code or not state.generated_testcase:
            print("❌ Missing code or tests")
            return state.model_copy(update={
                "qa_test_results": "SKIPPED",
                "QA_approval_status": "pending"
            })
        
        prompt = f"""Execute tests and provide report:

Code:
{state.generated_code}

Tests:
{state.generated_testcase}

Requirements:
{state.requirements}

Provide:
Decision: [pass/fail]
Summary: Total/Passed/Failed
Issues: [list any critical issues]
"""
        
        messages = [
            SystemMessage(content="You are a senior QA engineer."),
            HumanMessage(content=prompt)
        ]
        
        try:
            qa_results = self.llm.invoke(messages).content
            print("\n" + qa_results)
            
            decision = "fail"
            if "pass" in qa_results.lower()[:200]:
                decision = "pass"
                print("\n✅ QA PASSED!")
            else:
                print("\n❌ QA FAILED!")
            
            approval = "approved" if decision == "pass" else "rejected"
            
            return state.model_copy(update={
                "qa_test_results": qa_results,
                "QA_approval_status": approval,
                "QA_feedback": qa_results if decision == "fail" else "Passed"
            })
        except Exception as e:
            print(f"❌ Error: {e}")
            return state.model_copy(update={
                "qa_test_results": f"ERROR: {e}",
                "QA_approval_status": "pending"
            })

    def user_story_routing(self, state: SDLC) -> Literal["User_story", "design_document"]:
        return "design_document" if state.approval_status == "approved" else "User_story"

    def design_routing(self, state: SDLC) -> Literal["design_document", "generate_code"]:
        return "generate_code" if state.design_approval_status == "approved" else "design_document"

    def code_routing(self, state: SDLC) -> Literal["generate_code", "genrated_test_case"]:
        return "genrated_test_case" if state.code_approval_status == "approved" else "generate_code"

    def test_case_routing(self, state: SDLC) -> Literal["genrated_test_case", "qa_testing"]:
        return "qa_testing" if state.testcase_approval_status == "approved" else "genrated_test_case"

    def qa_test_route(self, state: SDLC) -> Literal["END", "generate_code"]:
        return END if state.QA_approval_status == "approved" else "generate_code"