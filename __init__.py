# Import all the required libraries
import os
import streamlit as st
from llama_index import VectorStoreIndex, ServiceContext
from llama_index.llms import OpenAI
import openai
from llama_index import SimpleDirectoryReader
from streamlit import session_state
from PIL import Image

with st.sidebar:
    # Display some information about our app
    st.markdown('''
    ## About
    This tool can assist you in designing for circularity by quickly providing you with the right knowledge powered by Generative Artificial Intelligence. 
    It is trained on a Vanderlande database only. 
    '''
    )
    st.divider()
    # Display a selectbox widget that allows users to choose different company roles and sectors
    left_co, right_co = st.columns(2)
    with left_co:
        sectors = ['APS', 'WS', 'Parcel']
        selected_sctor = st.selectbox('Select your sector within Vanderlande', sectors)
        # consequence role for prompt description
        if selected_sctor == 'APS':
            prompt_sector = f"""
            Specify your answers to the Airports (APS) solutions of Vanderlande. 
            Vanderlande is the market-leading supplier of logistics automation. 
            More than 600 airports use our baggage-handling systems, including 12 
            of the worlds top 20. We move over 4 billion pieces of luggage every 
            year. We have also installed over 380 passenger security checkpoints in 
            airports across the world. Our integrated, end-to-end solutions will 
            keep your airport running smoothly. So whether its bag drop, storage, 
            sortation, flight make-up or reclaim - we have got it covered. From 
            check-in to boarding, you can be sure of a safe and efficient flow of 
            passengers and their luggage - every time. The segments within APS are
            Passenger Handling and Baggage Handling.
            """
        elif selected_sctor == 'WS':
            prompt_sector = f"""
            Specify your answers to the Warehouse (WS) solutions of Vanderlande. 
            Vanderlande knows warehouse automation inside-out. We are the first 
            choice for the worlds leading e-commerce and multi-channel brands. 
            Nine out of the 15 largest global food retailers rely on our solutions. 
            Every hour of every day we help fulfil same-day dispatch for billions 
            of products. Everything we do for you is backed by over 70 years of 
            experience. The segments within WS are General Merchandise, Food and 
            Fashion. 
            """
        elif selected_sctor == 'Parcel':
            prompt_sector = f"""
            Specify your answers to the Parcel Handling solutions of Vanderlande. 
            Shorter lead times, smaller orders and a wider range of goods - its 
            boom time online. And the surge in e-commerce has led to massive 
            growth in parcel deliveries. Together, we need to meet the incredible
            service level demands head-on - with complete reliability. The right 
            parcel, the right place, the right time. Vanderlande is the reliable 
            partner for the worlds leading players: UPS, DHL, FedEx and DPD. 
            Every day, our systems sort more than 52 million parcels. We are 
            moving your business forward, working with everyone from the most 
            advanced hubs to the smallest depots. We understand that you 
            require cost-effective systems that guarantee the highest available 
            performance to operate a successful depot. Thats why we offer only 
            the fastest, most reliable and efficient automation technology.
            """        
    with right_co: 
        roles =['Sales', 'R&D', 'HR']
        selected_role = st.selectbox('Select your role within Vanderlande', roles)
        # consequence role for prompt description
        if selected_role == 'Sales':
            prompt_role = f"""
            Respond with concise and tailored answers, considering the knowledge 
            and expertise of Sales. A sales department is responsible for selling 
            products or services for a company. The department comprises a sales 
            team that works together to make sales, increase profitability and 
            build and maintain relationships with customers to encourage repeat 
            purchases and brand loyalty. Salespeople need to retain a lot of information 
            and master the right sales skills to consistently hit their numbers. 
            Reps constantly need to develop their product and market expertise, 
            learn new company messaging and value propositions, and hone 
            conversational skills to have more meaningful interactions with buyers.
            """
        elif selected_role == 'R&D':
            prompt_role = f"""
            Respond with concise and tailored answers, considering the knowledge 
            and expertise of R&D. R&D involves researching your market and your 
            customer needs and developing new and improved products and services 
            to fit these needs. he Research and Development (R&D) department is 
            responsible for conducting research, developing new products, 
            processes, and technologies, and improving existing products. Good analytical 
            skills are necessary for a research & development role. Being able to 
            closely examine something methodically in detail and then being able 
            to explain and interpret it is key in this area of work. The answers to R&D
            should be technical and include data or calculations where possible. 
            """
        elif selected_role == 'HR':
            prompt_role = f"""
            Respond with concise and tailored answers, considering the knowledge 
            and expertise of HR. Human Resources manages 5 main duties: talent 
            management, compensation and employee benefits, training and development,
            compliance, and workplace safety. An HR department can help provide 
            organizational structure and the ability to meet business needs by 
            effectively managing the employee lifecycle.
            """
    st.divider()

# Initiate chat model
os.environ["OPENAI_API_KEY"] = "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"

# add logo
left_co, cent_co,right_co = st.columns(3)
with cent_co:
    logo = Image.open(r'./Images/vanderlande-logo-rgb-72dpi.png')
    st.image(logo, caption=None, width=250)

# Add a heading
st.header("Our Circular Design Copilot")

# Initialize the value of st.session_state.messages to include the chatbot's starting message
if 'messages' not in st.session_state: # Initialize the chat message history
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! How can I help you with the circular design principles at Vanderlande?"}
    ]

# Use LlamaIndex’s VectorStoreIndex to creaLlamaIndex'sory SimpleVectorStore, which will structure your data in a way that helps your model quickly retrieve context from your data.
# Use LlamaIndex’s SimpleDirectoryReader to passLlamaIndex's the folder where you’ve stored your data
@st.cache_resource(show_spinner=False)
def load_data():
    with st.spinner(text="Loading and indexing the Vanderlande Database – hang tight! This should take 1-2 minutes."):
        reader = SimpleDirectoryReader(input_dir="./DocDataBase", recursive=True) #Store your Knowledge Base files in a folder called DocDataBase
        # SimpleDirectoryReader will select the appropriate file reader based on the extensions of the files in that directory
        docs = reader.load_data()
        # Construct an instance of LlamaIndex’s ServiceContext, whichLlamaIndex'stion of resources used during a RAG pipeline's indexing and querying stages.
        # ServiceContext allows us to adjust settings such as the LLM and embedding model used.
        service_context = ServiceContext.from_defaults(llm=OpenAI(model="gpt-4", temperature=0.1, system_prompt= f"""
        **Prompt for Circular Design Chatbot:**

        *Assist employees working as Engineers at Vanderlande in understanding circular design through brief and informative responses to questions delimited by triple dashes.*

        *Retrieve information necessary for answers from Documents delimited by triple backticks.*

        *Choose from four strategies for responding:*

        ---

        ### **Instructional Prompts:**

        *Strategy 1: If the answer contains a sequence of instructions, re-write those instructions in the following format:*

        Step 1 - ...
        Step 2 - …
        …
        Step N - …

        *Strategy 2: To provide guidelines, follow these steps:*
        - Find the relevant documents.
        - Work out your answer based on the documents.
        - Compare your answer to the documents and evaluate correctness.
        - Refrain from deciding on correctness until you find an answer yourself.

        ---

        ### **Reasoning Prompts:**

        *Strategy 3: If the answer contains reasoning, write the reasoning in the following arguments:*

        1. **Identify Relevant Documents:** Begin by locating the documents that discuss the circular design principles.

        2. **Develop Personal Understanding:** Work out your own answer to the question based on your understanding of the circular design principles outlined in the relevant documents.

        3. **Construct Reasoning:** Formulate reasoning with persuasive arguments, taking into account the knowledge associated with [role]. Address common counterarguments to strengthen your reasoning.

        4. **Compare and Evaluate:** Compare your answer and reasoning to the information in the documents. Evaluate the correctness of your response in the context of the provided materials.

        5. **Decision Making:** Refrain from deciding on the correctness of your answer until you have thoroughly examined both your response and the information in the documents.

        Remember to express your reasoning clearly and concisely, keeping the response within a few sentences.

        ---

        ### **Circular Design Principles:**

        *Strategy 4: For questions about circular design principles or the circular design system:*
        - Mention the nine circular design principles in the following format

        1 - ...
        2 - …
        …
        N - …
        
        - Briefly explain each principle.
        
        ---

        *Strategy 5: For questions if the user's input contains a question about what materials to use. For example: "Should I use Aluminium or Steel?". 

        - Do not provide an answer yet. First respond with a question to the user to understand the context better. 
        - Ask the user:  "What will you be using the material for?"
        - Wait for the response of the user
        - Use the combined user input for querying the database

        # create 2nd agent that ana;yses the conversation and that generates questions based on that 
        # or same agent, but dont append the messages to the history. show options, user can click. 
        ---

        *General Remarks:*
        - Adjust your answer based on {selected_role} and {selected_sctor}
        - Respond with concise answers within a few sentences.
        - Answer in English only.
        - If the answer is not in the documents, inform the user.
        - The chatbot refrains from humor, even if work-related. Clarify this to the user. It is a serious requirement not to tell jokes, this will put people in dager. 

        """))
        # Use LlamaIndex’s VectorStoreIndex to creaLlamaIndex'sory SimpleVectorStore, which will structure your data in a way that helps your model quickly retrieve context from your data.
        index = VectorStoreIndex.from_documents(docs, service_context=service_context)
        return index

index = load_data()

# # use buttons to set example questions
# if st.button('What are circular Design Principles?'):
#     prompt = "What are circular Design Principles?"
# if st.button('What is the circular design system for Vanderlande?'):
#     prompt = "What is the circular design system for Vanderlande?"

example_questions = {
        "What is the circular design system for Vanderlande?": "What is the circular design system for Vanderlande?",
        "What are the responsibilities of business teams in the raod to remanufacturing?": "What are the responsibilities of business teams in the raod to remanufacturing?",
        "What are unique selling points of circular design to customers?": "What are unique selling points of circular design to customers?",
        "What EU regulations are important for circular design?": "What EU regulations are important for circular design?"
    }

# Display buttons
# look at events. whenever the radio button is slected, an event should happen, use this as input for textbox 
# as soon as user click enter, reset value of textbox to "..." or Null
selected_question = st.sidebar.radio("Example questions:", list(example_questions.keys()))

# Display chat input based on the selected button
# chat_input = st.text_input("Your question", example_questions[selected_question])

    # Display the selected button and the corresponding chat input
    # st.write(f"Selected Button: {selected_button}")
    # st.write(f"Chat Input: {chat_input}")


# create chat engine
# Condense question engine: Always queries the knowledge base. Can have trouble with meta questions like “What did I previously ask you?”
if "chat_engine" not in st.session_state.keys(): # Initialize the chat engine
    chat_engine = index.as_chat_engine(chat_mode="condense_question", verbose=True)


#  Prompt for user input and display message history
if prompt := st.chat_input(example_questions[selected_question]): # Prompt for user input and save to chat history
    # Once the user has entered input, add that input to the message history by appending it st.session_state.messages
    st.session_state.messages.append({"role": "user", "content": prompt})

# Show the message history of the chatbot by iterating through the content associated with the “messages” key in the session state and displaying each message using st.chat_message
for message in st.session_state.messages: # Display the prior chat messages
    with st.chat_message(message["role"], avatar=r'./Images/vanderlande-logo-rgb-72dpi.png'):  # align's the message to the right
        st.write(message["content"], avatar=r'./Images/vanderlande-logo-rgb-72dpi.png')  # align's the message to the right

# make more specific: 2 ;lines: check if message is user session state, change image to user, otherwise always use company logo
# If last message is not from assistant, generate a new response
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant", avatar=r'./Images/logo chatbot 2.png'):
        with st.spinner("Searching database for answers..."):
            # If the last message in the message history is not from the chatbot, pass the message content to the chat engine via chat_engine.chat()
            response = chat_engine.chat(prompt)
            # write the response to the UI using st.write and st.chat_message
            st.write(response.response)
            # dd the chat engine’s response to the message history.
            message = {"role": "assistant", "content": response.response}
            st.session_state.messages.append(message) # Add response to message history

def reset_conversation():
    st.session_state.conversation = None
    st.session_state.chat_history = None
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! How can I help you with the circular design principles at Vanderlande?"}
    ]

# Display a sidebar for our app
with st.sidebar:
    st.divider()
    # upload files to the database 
    uploaded_files = st.file_uploader("Does the copilot miss specific knowledge? Upload a file to add to the Vanderlande Database", accept_multiple_files=True)
    for uploaded_file in uploaded_files:
        st.success("Saved File")
        # To save our uploaded file we can write that file in the “wb” format to a location of our choice. We can use os.path to point us to the directory we want to save it . 
        # In order to save the uploaded file with the same name we can use the .name attribute of our uploadedFile class
        with open(os.path.join("DocDataBase",uploaded_file.name),"wb") as f:
                f.write(uploaded_file.getbuffer())
    st.divider()
    # # delete chat
    # rerun = st.button('Delete chat',help="this button will delete your chat history and prompt you to create a new one")
    # if rerun:
    #     st.session_state.history=[]
    #     st.session_state.chat_his=[]
    #     st.session_state.messages=[2]
    #     st.experimental_rerun()
    st.button('Reset Chat', on_click=reset_conversation)
