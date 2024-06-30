import os
from pathlib import Path
import random
from datetime import datetime
import autogen
from autogen import AssistantAgent, UserProxyAgent
from termcolor import colored
from autogen.code_utils import content_str

def setup_config():
    config_list_gemini = autogen.config_list_from_json(
        "conf/OAI_CONFIG_LIST.txt",
        filter_dict={"model": ["gemini-pro"]}
    )

    llm_config = {
        "cache_seed": 42,  # change the cache_seed for different trials
        "temperature": 0,
        "config_list": config_list_gemini,
        "timeout": 120,
    }

    return llm_config

def setup_agents(llm_config, characters):
    def termination_msg(x):
        return isinstance(x, dict) and "TERMINATE" == str(x.get("content", ""))[-9:].upper()

    host = autogen.UserProxyAgent(
        name="host",
        is_termination_msg=termination_msg,
        human_input_mode="NEVER",
        code_execution_config=False,
        default_auto_reply="Reply `TERMINATE` if the task is done.",
        description="Host and initiator of the group podcast who mediates the conversation to keep it continuing",
    )

    guest_conf = [
        {"name": "Darth Vader", "description": "Darth Vader is a fictional character in the Star Wars universe who serves at the Galactic Empire as the right-hand man to the Sith and was once known as Anakin Skywalker, the fallen Jedi."},
        {"name": "Joe Rogan", "description": "A comedian and well-known podcast host for his own shows."}
    ]

    guest_agents = [
        autogen.UserProxyAgent(
            name=guest.get('name'),
            is_termination_msg=termination_msg,
            human_input_mode="NEVER",
            code_execution_config=False,
            default_auto_reply="Reply `TERMINATE` if the task is done.",
            description=guest.get("description"),
        )
        for guest in guest_conf
    ]

    initializer = autogen.UserProxyAgent(name="Init", human_input_mode="NEVER")

    coder = autogen.AssistantAgent(
        name="Retrieve_coder",
        llm_config=llm_config,
        human_input_mode="NEVER",
        system_message="""You are the Coder. 
        You write python/shell code to solve the task provided. Wrap the code in a code block that specifies the script type. The user can't modify your code. So do not suggest incomplete code which requires others to modify. Don't use a code block if it's not intended to be executed by the executor.
        Don't include multiple code blocks in one response. Do not ask others to copy and paste the result. Check the execution result returned by the executor.
        If the result indicates there is an error, fix the error and output the code again. Suggest the full code instead of partial code or code changes. If the error can't be fixed or if the task is not solved even after the code is executed successfully, analyze the problem, revisit your assumption, collect additional info you need, and think of a different approach to try. Ensure proper error handling such that an appropriate format of results is returned with the error code.
        """,
    )

    research_coder = autogen.AssistantAgent(
        name="Research_coder",
        llm_config=llm_config,
        human_input_mode="NEVER",
        system_message="""You are the Coder. 
        You write python/shell code only to find and provide resources available on the web for research purposes.
        The user can't modify your code. So do not suggest incomplete code which requires others to modify. Don't use a code block if it's not intended to be executed by the executor.
        Don't include multiple code blocks in one response. Do not ask others to copy and paste the result. Check the execution result returned by the executor.
        If the result indicates there is an error, fix the error and output the code again. Suggest the full code instead of partial code or code changes. If the error can't be fixed or if the task is not solved even after the code is executed successfully, analyze the problem, revisit your assumption, collect additional info you need, and think of a different approach to try. Ensure proper error handling such that an appropriate format of results is returned with the error code.
        """,
    )

    executor = autogen.UserProxyAgent(
        name="Retrieve_executer",
        system_message="Executor. Execute the code written by the Coder and report the result.",
        human_input_mode="NEVER",
        code_execution_config={"last_n_messages": 3, "work_dir": "code", "use_docker": False},
    )

    informer = autogen.AssistantAgent(
        name="information",
        llm_config=llm_config,
        human_input_mode="NEVER",
        system_message="""Provide cornerstone information on the participants in the conversation. Provide the summarized biography of the guests in the conversation, including their most known achievements, personality and relevant news as context.""",
    )

    script_parser = autogen.AssistantAgent(
        name="Json Parser",
        llm_config=llm_config,
        human_input_mode="NEVER",
        system_message="Provide an output in JSON string. Parse the conversation dialogue string under the key 'podcast'. Include a boilerplate summary of the podcast content under 'abstract'.",
    )

    host_agent = autogen.AssistantAgent(
        name="Podcast Host",
        llm_config=llm_config,
        human_input_mode="NEVER",
        system_message="""As a podcast host such as the NPR, you will start and lead the conversation to create entertaining conversations, jokes while investigating the guests' thoughts and perspectives""",
    )

    podcast_agents = [
        autogen.AssistantAgent(
            name=c_name,
            llm_config=llm_config,
            system_message=f"As yourself: {c_name}, respond to the previous or existing dialogue.",
        )
        for c_name in characters
    ]

    return initializer, research_coder, executor, informer, host_agent, podcast_agents, script_parser

def weighted_choice(items, current, weight=0.5, host_chance=None, host=None):
    if host_chance is None:
        host_chance = 1 / len(items)

    non_host_weight = (1 - host_chance)

    weights = [
        weight if item == items[(items.index(current) + 1) % len(items)]
        else (non_host_weight / (len(items) - 2)) if item != host
        else host_chance
        for item in items if item != current
    ]

    choices = [item for item in items if item != current]
    return random.choices(choices, weights=weights)[0]

def save_conversation(content, output_dir=Path("output/conversations")):
    output_dir.mkdir(exist_ok=True, parents=True)
    if type(content) == list:
        content = "\n".join(content)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{timestamp}.txt"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w") as file:
        file.write(content)

    return filepath

def main(topic="General Conversation", characters=None, n_rounds=5):
    if characters is None:
        characters = ["Harry Potter", "Iron Man", "Darth Vader", "Alan Turing", "Albert Einstein", "Djingis Khan"]
    
    llm_config = setup_config()
    initializer, research_coder, executor, informer, host_agent, podcast_agents, script_parser = setup_agents(llm_config, characters)

    groupchat = autogen.GroupChat(
        agents=[initializer, research_coder, executor, informer, host_agent] + podcast_agents + [script_parser],
        messages=[],
        max_round=n_rounds,
        speaker_selection_method="auto"
    )
    
    manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)
    
    characters_str = ",".join(characters)
    chat_result = initializer.initiate_chat(
        manager, message=f"Carry out a podcast on the topic: '{topic}' among the characters: {characters_str}, in a real-life conversation using current and historical news to provide context. A character should only start or respond to the existing conversation."
    )
    
    conv = chat_result.chat_history
    try:
        save_conversation(conv)
    except Exception as e:
        print(e)

    return conv[3:]

if __name__ == "__main__":
    last_message = main(
        topic="Science and Technology", 
        characters=["Alan Turing", "Albert Einstein"],
        n_rounds=5
        )
    print(last_message)