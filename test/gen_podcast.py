import os, json, random
from pathlib import Path
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
            system_message=f"As the podcast guest: {c_name}, respond to the previous or existing dialogue.",
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

def save_conversation(content, output_dir=Path("outputs/conversations")):
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # Convert the content to a JSON string
    content_json = json.dumps(content, indent=4)
    
    # Generate the filename with the current timestamp
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{timestamp}.json"
    filepath = os.path.join(output_dir, filename)

    # Save the content to the file
    with open(filepath, "w") as file:
        file.write(content_json)

    return filepath

def get_state_transition(initializer, research_coder, executor, informer, host_agent, podcast_agents, script_parser):
    def state_transition(last_speaker, groupchat):
        messages = groupchat.messages

        if last_speaker is initializer:
            # init -> retrieve
            return research_coder
        elif last_speaker is research_coder:
            # retrieve: action 1 -> action 2
            return executor
        elif last_speaker is executor:
            if messages[-1]["content"] == "exitcode: 1":
                # retrieve --(execution failed)--> coder
                return research_coder
            else:
                # retrieve --(execution success)--> informer
                return informer
        elif last_speaker is informer:
            # informer -> host
            return host_agent
        elif last_speaker is host_agent:
            # host -> random character from podcast_agents
            return random.choice(podcast_agents)
        elif last_speaker in podcast_agents:
            # one podcast agent -> another weighted choice from podcast_agents
            return weighted_choice(podcast_agents, last_speaker, weight=0.5, host_chance=1/len(podcast_agents))
        else:
            return script_parser
    return state_transition
    
def main(topic="General Conversation", characters=None, n_rounds=5):    
    llm_config = setup_config()
    initializer, research_coder, executor, informer, host_agent, podcast_agents, script_parser = setup_agents(llm_config, characters)
    speaker_transition = get_state_transition(
        initializer, research_coder, executor, informer, host_agent, podcast_agents, script_parser
    )
    groupchat = autogen.GroupChat(
        agents=[initializer, host_agent] + podcast_agents + [script_parser],
        messages=[],
        max_round=n_rounds,
        speaker_selection_method=speaker_transition
        #"auto"
    )
    
    manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)
    
    characters_str = ",".join(characters)
    chat_result = initializer.initiate_chat(
        manager, message=f"Create a podcast on the topic: '{topic}' among the characters: {characters_str}, as in a real-life conversation. Each dialogue must be inquired from each podcast guest. The dialogue are eventually compiled into a JSON transcript."
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
        characters=[
            "Harry Potter", "Iron Man", "Darth Vader"],
        n_rounds=8
        )
    print(last_message)