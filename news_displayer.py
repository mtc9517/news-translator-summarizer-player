import streamlit as st
import os

# Using object notation
choice_selectbox = st.sidebar.selectbox(
    "What kind of news would you like to view ?",
    ("Positive", "Negative", "Neutral"), index = 0)

# Get the list of all files and directories
download_dir = "./downloads_all/"
dir_list = os.listdir(download_dir)

dir_full_list = []
for x in dir_list:
    if 'full' in x:
        dir_full_list.append(x)

look_for = ""
if choice_selectbox == 'Negative':
    look_for = "negative"
if choice_selectbox == 'Positive':
    look_for = "positive"
if choice_selectbox == 'Neutral':
    look_for = "neutral"

for complete_text_file_name in dir_full_list:
    if look_for in complete_text_file_name:
        st.info("Full article")
        with open(download_dir + complete_text_file_name) as f:
            contents = f.read()
            st.markdown(contents)
            f.close()

        st.info("Summarized article")
        with open(download_dir + complete_text_file_name.replace("full", "summary")) as f:
            contents = f.read()
            st.markdown(contents)
            f.close()
