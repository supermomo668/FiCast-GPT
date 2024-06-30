from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain

import os, dotenv, yaml

from langchain.chains.conversation.memory import ConversationBufferMemory, ConversationSummaryBufferMemory

from . import DEFAULT_CONF

# load the environment variables
dotenv.load_dotenv()
# first initialize the large language model
DEFAULT_MODEL = os.environ.get("MODEL", "gpt-4")

class podcaster:
    def __init__(self, conv_conf=DEFAULT_CONF, conv="DEFAULT"):
        llm = ChatOpenAI(
            temperature=1e-2,
            openai_api_key=os.environ.get("OPENAI_API_KEY"),
            model_name=DEFAULT_MODEL,
        )
        memory = ConversationSummaryBufferMemory(llm=llm, max_token_limit=2000)
        # memory=ConversationBufferMemory(
        # ai_prefix="AI Assistant", human_prefix="Human"
        # )
        # now initialize the conversation chain
        self.conversation_buf = ConversationChain(
                llm=llm,
                memory=memory,
        )
        self.conversation_buf.prompt.template = conv_conf.get("PROMPTS")["AGENT"][conv]
        pass

    def converse(self, dialogue):
        return self.conversation_buf(dialogue)


if __name__ == "__main__":
    podcast_expert = podcaster(
        conv_conf, conv="PODCAST_GUEST")
    print(
        "Default conversation template:",
        type(podcast_expert.conversation_buf.prompt.template),
        podcast_expert.conversation_buf.prompt.template,
        sep="\n",
    )
