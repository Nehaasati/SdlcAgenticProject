import pydantic
from pydantic import BaseModel, Field
from typing import Dict, Literal, Optional


class SDLC(BaseModel):
    """State model for SDLC workflow - All fields properly typed"""
    
    # Required field
    #requirements: str
    
    # Optional artifact fields with proper typing
    User_story: Optional[str] = None
    design_documents: Optional[str] = None
    generated_code: Optional[str] = None
    generated_testcase: Optional[str] = None
    qa_test_results: Optional[str] = None
    
    # Feedback fields with defaults
    Feedback: str = Field(default="no feedback yet")
    user_story_feedback: str = Field(default="No user story feedback yet.")
    design_feedback: str = Field(default="No design feedback yet.")
    code_review: str = Field(default="No code feedback yet.")
    test_case_feedback: str = Field(default="No test case feedback yet.")
    QA_feedback: str = Field(default="No QA feedback yet.")
    
    # Approval status fields
    approval_status: str = Field(default="pending")
    design_approval_status: str = Field(default="pending")
    code_approval_status: str = Field(default="pending")
    testcase_approval_status: str = Field(default="pending")
    QA_approval_status: str = Field(default="pending")

    feedback: str = "No feedback yet."
    test_review_feedback: Literal["approve", "revise"] = "revise"
    qa_test_result: Literal["pass", "fail"] = "fail"
    qa_attempts: int = 0
    design_attempt: int = Field(default=0)
    design_feedback: str = Field(default="No design feedback yet.")
    status: str = Field(default="pending")
    user_stories_feedback: str = Field(default="")
    test_case_feedback: str = "No test case feedback yet."
    finale_code: Optional[str] = Field(default="")
    final_test_cases: Optional[str] = Field(default="")