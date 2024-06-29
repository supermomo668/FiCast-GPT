import autogen
from autogen import AssistantAgent, UserProxyAgent
from typing import List, Dict

def termination_msg(x):
    return isinstance(x, dict) and "TERMINATE" == str(x.get("content", ""))[-9:].upper()

def create_agents(config):
    llm_config = {
        "cache_seed": config.llm_config.cache_seed,
        "temperature": config.llm_config.temperature,
        "config_list": autogen.config_list_from_json(
            config.llm_config.config_list_path,
            filter_dict={"model": ["gemini-pro"]},
        ),
        "timeout": config.llm_config.timeout,
    }
    
    host = UserProxyAgent(
        name="host",
        is_termination_msg=lambda x: isinstance(x, dict) and "TERMINATE" == str(x.get("content", ""))[-9:].upper(),
        human_input_mode="NEVER",
        code_execution_config=False,
        default_auto_reply="Reply `TERMINATE` if the task is done.",
        description="Host and initiator of the group podcast who mediates the conversation to keep it continuing",
    )


    initializer = UserProxyAgent(name="Init")
    
    coder = AssistantAgent(
        name="Retrieve_coder",
        llm_config=llm_config,
        system_message="""You are the Coder...""",
    )

    reseach_coder = AssistantAgent(
        name="Retrieve_coder",
        llm_config=llm_config,
        system_message="""You are the Coder...""",
    )

    executor = UserProxyAgent(
        name="Retrieve_executer",
        system_message="Executor. Execute the code written by the Coder and report the result.",
        human_input_mode="NEVER",
        code_execution_config={
            "last_n_messages": 3,
            "work_dir": "code",
            "use_docker": False,
        },
    )

    informer = AssistantAgent(
        name="information",
        llm_config=llm_config,
        system_message="""Provide cornerstone information...""",
    )

    script_parser = AssistantAgent(
        name="Json Parser",
        llm_config=llm_config,
        system_message="Reply in JSON...",
    )

    podcast_agents = [
        AssistantAgent(
            name=char,
            llm_config=llm_config,
            system_message=f"As yourself: {char}, respond to the previous or existing dialogue.",
            human_input_mode="NEVER",
            code_execution_config=False,
            # default_auto_reply="Reply `TERMINATE` if the task is done.",
        ) for char in config.characters
    ]

    return [initializer, reseach_coder, executor, informer] + podcast_agents + [script_parser]
