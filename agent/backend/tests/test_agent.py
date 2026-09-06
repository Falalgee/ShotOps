from app.agent import root_agent


def test_root_agent_exists():
    assert root_agent is not None
    assert root_agent.name == "shotops_production_operations_agent"
