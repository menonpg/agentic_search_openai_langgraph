# import streamlit as st
# from dotenv import load_dotenv
# from graph import run_graph

# load_dotenv()

# def main():
#     st.title("AI-Powered Search and Insights (GPT-4o)")

#     user_input = st.text_area("Enter your query", height=100)

#     if st.button("Search and Analyze"):
#         with st.spinner("Searching and analyzing..."):
#             result = run_graph(user_input)
#             st.subheader("Results")
#             st.markdown(result)

# if __name__ == "__main__":
#     main()

import streamlit as st
from dotenv import load_dotenv
from graph import run_graph

load_dotenv()

def main():
    st.title("AI-Powered Search and Insights")

    user_input = st.text_area("Enter your query", height=100)

    if st.button("Search and Analyze"):
        with st.spinner("Searching and analyzing..."):
            result = run_graph(user_input)
            st.subheader("Results")
            st.markdown(result, unsafe_allow_html=True)

if __name__ == "__main__":
    main()