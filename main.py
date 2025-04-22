import streamlit as st
from langchain_helper import get_few_shot_db_chain

# Setting the page title and layout
st.set_page_config(page_title="AtliQ T-Shirts Database Q&A", layout="centered")

# Header and subtitle
st.title("AtliQ T-Shirts: Database Q&A 👕")
st.markdown("""
    **Welcome to the AtliQ T-Shirts Q&A system!**  
    You can ask any question related to the inventory and stock of our T-shirts, and the system will fetch the relevant information directly from the database.
    Simply type your question below and get the answer instantly!
""")

# Input for question with a placeholder and some styling
question = st.text_input("Ask a question about our T-shirt stock:", placeholder="e.g., How many white Nike T-shirts are in stock?")

# Display a loading spinner while processing
if question:
    with st.spinner('Fetching the answer...'):
        chain = get_few_shot_db_chain()
        response = chain.invoke(question)
    print(response)
    # Attention-seeking header for the result
    if "-999" in response['result'] or not response['result'].strip():
        st.error(
            "❌ **Unauthorized Action**: You do not have permission to modify the database.")

    else:
        st.markdown(f"### 🎯 **Answer:**")
        st.success(response['result'], icon="✅")  # Success message with a checkmark icon
else:
    # Message prompting users to enter a question
    st.info("🔍 Please enter a question to get started. (e.g., 'How many Adidas T-shirts are available?')", icon="ℹ️")

# Add a 'Help' button for users to get more info on how to use the app
if st.button('Need Help?'):
    st.markdown("""
        #### Here are some example questions you can ask:
        - "How many white Nike T-shirts do we have?"
        - "What is the stock count for black Adidas T-shirts?"
        - "How many red T-shirts are available in size M?"
    """)
