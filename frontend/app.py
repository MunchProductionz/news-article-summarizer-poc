from client import get_articles, send_email
import streamlit as st
import pandas as pd

articles = get_articles()

st.title('News Summarizer')

articles_df = pd.DataFrame(articles)
articles_df = [articles_df[col].astype(str) for col in articles_df.columns]
articles_display_df = articles_df[["title", "category", "bullet_points"]].copy()
articles_display_df['include_in_summary'] = False
edited_df = st.data_editor(
    articles_display_df,
    column_config={
        "title": ""
    })

summary_df = edited_df[edited_df["include_in_summary"]]
ids = articles_df.loc[summary_df.index, "id"].tolist()

title = st.text_input("Receiver mail", "")

st.markdown(f"You are interested in {ids}")

if st.button('Send summary', type="primary"):
    send_email(ids, title)

