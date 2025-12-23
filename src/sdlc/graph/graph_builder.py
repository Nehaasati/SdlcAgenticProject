from langgraph.graph import StateGraph, START,END, MessagesState
from langgraph.prebuilt import tools_condition,ToolNode
from langchain_core.prompts import ChatPromptTemplate
from src.sdlc.state.state import State
from src.sdlc.nodes.node import SDLCNode
from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()


class GraphBuilder:
    def __init__(self, model):
        self.model = model
        self.graph_builder = StateGraph(State)

    def sdlc_graph(self):
        self.node = SDLCNode(self.model)

        self.graph_builder.add_node("User Stories",self.node.User_story)
        self.graph_builder.add_node("Product Owner Review",self.node.product_owner_review)
        
        self.graph_builder.add_node("design_document",self.node.design_document)
        self.graph_builder.add_node("design_review",self.node.design_review)
        self.graph_builder.add_node("generate_code", self.node.generate_code)
        self.graph_builder.add_node("code_review", self.node.code_review)
        self.graph_builder.add_node("genrated_test_case",self.node.genrated_test_case)
        self.graph_builder.add_node("review_testcase",self.node.review_testcase)
        self.graph_builder.add_node("qa_testing",self.node.qa_testing)

     # Edges
        self.graph_builder.add_edge(START, "requirements")
        self.graph_builder.add_edge("requirements", "User_story")
        self.graph_builder.add_edge("User_story", "product_owner_review")

        self.graph_builder.add_conditional_edges(
        "product_owner_review",
         self.node.user_story_routing,
        {
          "design_document": "design_document",
          "User_story": "User_story",
         },
        )

        self.graph_builder.add_edge("design_document", "design_review")

        self.graph_builder.add_conditional_edges(
        "design_review",
          self.node.design_routing,
        {
          "generate_code": "generate_code",
          "design_document": "design_document",
         },
         )

        self.graph_builder.add_edge("generate_code", "code_review")

        self.graph_builder.add_conditional_edges(
        "code_review",
        self.node.code_routing,
         {
          "generate_code": "generate_code",
          "genrated_test_case": "genrated_test_case",
         },
        )

        self.graph_builder.add_edge("genrated_test_case", "review_testcase")

        self.graph_builder.add_conditional_edges(
        "review_testcase",
        self.node.test_case_routing,
        {
          "genrated_test_case": "genrated_test_case",
          "qa_testing": "qa_testing",
        },
        )

        self.graph_builder.add_conditional_edges(
        "qa_testing",
        self.node.qa_test_route,
        {
          END: END,
          "generate_code": "generate_code",
         },
        )
    def setup_graph(self):
     self.sdlc_graph()
     #memory = MemorySaver()
     return self.graph_builder.compile(checkpointer=memory, interrupt_before =[ "product_owner_review",
          "design_review",
          "code_review",
          "review_testcase",
          ])

        
       
        
