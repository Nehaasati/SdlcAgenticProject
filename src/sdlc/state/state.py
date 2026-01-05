from pydantic import BaseModel, Field
from typing import Literal, Optional


class SDLC(BaseModel):
    requirements: str = Field(default="")
    
    User_story: Optional[str] = None
    design_documents: Optional[str] = None
    generated_code: Optional[str] = None
    generated_testcase: Optional[str] = None
    qa_test_results: Optional[str] = None
    finale_code: Optional[str] = Field(default="")
    final_test_cases: Optional[str] = Field(default="")
    
    user_story_feedback: str = Field(default="no feedback yet.")
    design_feedback: str = Field(default="No design feedback yet.")
    code_review: str = Field(default="No code feedback yet.")
    test_case_feedback: str = Field(default="No test case feedback yet.")
    QA_feedback: str = Field(default="No QA feedback yet.")
    
    approval_status: str = Field(default="pending")
    design_approval_status: str = Field(default="pending")
    code_approval_status: str = Field(default="pending")
    testcase_approval_status: str = Field(default="pending")
    QA_approval_status: str = Field(default="pending")
    
    qa_attempts: int = Field(default=0)
    design_attempt: int = Field(default=0)
    
    test_review_feedback: Literal["approve", "revise"] = "revise"
    qa_test_result: Literal["pass", "fail"] = "fail"
    status: str = Field(default="pending")