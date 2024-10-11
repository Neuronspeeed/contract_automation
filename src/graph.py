from langgraph.graph import StateGraph, END
from models import ContractState
from nodes import (
    process_documents,
    extract_pii_and_address,
    human_verification,
    missing_information,
    identify_buyer_and_seller,
    construct_contract
)

def create_graph():
    # Create the graph
    graph = StateGraph(ContractState)

    # Add nodes
    graph.add_node("process_documents", process_documents)
    graph.add_node("extract_pii_and_address", extract_pii_and_address)
    graph.add_node("human_verification", human_verification)
    graph.add_node("missing_information", missing_information)
    graph.add_node("identify_buyer_and_seller", identify_buyer_and_seller)
    graph.add_node("construct_contract", construct_contract)

    # Define edges
    graph.set_entry_point("process_documents")
    graph.add_edge("process_documents", "extract_pii_and_address")
    graph.add_edge("extract_pii_and_address", "human_verification")
    graph.add_conditional_edges(
        "human_verification",
        lambda state: "missing_information" if "missing" in state.messages[-1].content.lower() else "identify_buyer_and_seller"
    )
    graph.add_edge("missing_information", "human_verification")
    graph.add_edge("identify_buyer_and_seller", "construct_contract")
    graph.add_edge("construct_contract", END)

    return graph.compile()