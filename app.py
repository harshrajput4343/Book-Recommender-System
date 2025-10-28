import os
import sys
import pickle
import streamlit as st
import numpy as np
from books_recommender.logger.log import logging
from books_recommender.config.configuration import AppConfiguration
from books_recommender.pipeline.training_pipeline import TrainingPipeline
from books_recommender.exception.exception_handler import AppException


# Custom CSS for beautiful UI
def load_custom_css():
    st.markdown("""
    <style>
    /* Main app styling */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
    }
    
    /* Header styling */
    .header-container {
        text-align: center;
        padding: 2rem 0;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        backdrop-filter: blur(10px);
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    .header-title {
        font-size: 3rem;
        font-weight: 800;
        color: white;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        margin-bottom: 0.5rem;
    }
    
    .header-subtitle {
        font-size: 1.2rem;
        color: #f0f0f0;
        font-weight: 300;
    }
    
    /* Button styling */
    .stButton>button {
        width: 100%;
        background: linear-gradient(45deg, #f093fb 0%, #f5576c 100%);
        color: white;
        font-size: 1.1rem;
        font-weight: 600;
        padding: 0.75rem 2rem;
        border: none;
        border-radius: 25px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
    }
    
    /* Select box styling - FIXED TEXT COLOR */
    .stSelectbox {
        margin: 2rem 0;
    }
    
    .stSelectbox > div > div {
        background-color: rgba(255, 255, 255, 0.9);
        border-radius: 10px;
        border: 2px solid #667eea;
    }
    
    /* Fix for selectbox input text color */
    .stSelectbox input {
        color: #000000 !important;
        font-weight: 500;
    }
    
    /* Fix for selectbox selected value */
    .stSelectbox [data-baseweb="select"] > div {
        color: #000000 !important;
    }
    
    /* Fix for selectbox dropdown options */
    .stSelectbox [data-baseweb="select"] span {
        color: #000000 !important;
    }
    
    /* Label text color */
    .stSelectbox label {
        color: white !important;
        font-weight: 600;
        font-size: 1.1rem;
    }
    
    /* Column styling for book recommendations */
    .book-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease;
        text-align: center;
    }
    
    .book-card:hover {
        transform: scale(1.05);
    }
    
    /* Footer styling */
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        text-align: center;
        padding: 1rem 0;
        box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.2);
        z-index: 999;
    }
    
    .footer-content {
        font-size: 1rem;
        font-weight: 500;
    }
    
    .footer a {
        color: #ffd700;
        text-decoration: none;
        font-weight: 700;
        transition: color 0.3s ease;
    }
    
    .footer a:hover {
        color: #ffed4e;
        text-decoration: underline;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Image styling */
    img {
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        transition: transform 0.3s ease;
    }
    
    img:hover {
        transform: scale(1.05);
    }
    
    /* Text styling */
    .stText {
        color: white;
        font-weight: 600;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
    }
    
    /* Book title styling */
    [data-testid="column"] p {
        color: #333333;
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)


# Custom footer
def add_footer():
    footer_html = """
    <div class="footer">
        <div class="footer-content">
            <p>Designed and Developed by <a href="#" target="_blank">Harsh Kumar</a></p>
            <p style="font-size: 0.85rem; margin-top: 0.5rem;">📚 Books Recommender System | © 2025 All Rights Reserved</p>
            <p style="font-size: 0.85rem; margin-top: 0.5rem;"> harshkumarsingh4343@gmail.com  ,   phone no: 6287007845</p>
        </div>
    </div>
    """
    st.markdown(footer_html, unsafe_allow_html=True)


class Recommendation:
    def __init__(self, app_config=AppConfiguration()):
        try:
            self.recommendation_config = app_config.get_recommendation_config()
        except Exception as e:
            raise AppException(e, sys) from e

    def fetch_poster(self, suggestion):
        try:
            book_name = []
            ids_index = []
            poster_url = []
            book_pivot = pickle.load(open(self.recommendation_config.book_pivot_serialized_objects, 'rb'))
            final_rating = pickle.load(open(self.recommendation_config.final_rating_serialized_objects, 'rb'))

            for book_id in suggestion:
                book_name.append(book_pivot.index[book_id])

            for name in book_name[0]:
                ids = np.where(final_rating['title'] == name)[0][0]
                ids_index.append(ids)

            for idx in ids_index:
                url = final_rating.iloc[idx]['image_url']
                poster_url.append(url)

            return poster_url

        except Exception as e:
            raise AppException(e, sys) from e

    def recommend_book(self, book_name):
        try:
            books_list = []
            model = pickle.load(open(self.recommendation_config.trained_model_path, 'rb'))
            book_pivot = pickle.load(open(self.recommendation_config.book_pivot_serialized_objects, 'rb'))
            book_id = np.where(book_pivot.index == book_name)[0][0]
            distance, suggestion = model.kneighbors(book_pivot.iloc[book_id, :].values.reshape(1, -1), n_neighbors=6)

            poster_url = self.fetch_poster(suggestion)

            for i in range(len(suggestion)):
                books = book_pivot.index[suggestion[i]]
                for j in books:
                    books_list.append(j)
            return books_list, poster_url

        except Exception as e:
            raise AppException(e, sys) from e

    def train_engine(self):
        try:
            obj = TrainingPipeline()
            obj.start_training_pipeline()
            st.success("✅ Training Completed Successfully!")
            logging.info(f"Recommended successfully!")
        except Exception as e:
            raise AppException(e, sys) from e

    def recommendations_engine(self, selected_books):
        try:
            recommended_books, poster_url = self.recommend_book(selected_books)
            
            st.markdown("### 📖 Recommended Books for You")
            
            col1, col2, col3, col4, col5 = st.columns(5)
            
            # Display recommendations (skip index 0, show 1-5)
            with col1:
                st.markdown(f"**{recommended_books[1]}**")
                st.image(poster_url[1], width=150)
            
            with col2:
                st.markdown(f"**{recommended_books[2]}**")
                st.image(poster_url[2], width=150)

            with col3:
                st.markdown(f"**{recommended_books[3]}**")
                st.image(poster_url[3], width=150)
            
            with col4:
                st.markdown(f"**{recommended_books[4]}**")
                st.image(poster_url[4], width=150)
            
            with col5:
                st.markdown(f"**{recommended_books[5]}**")
                st.image(poster_url[5], width=150)
                
        except Exception as e:
            st.error(f"❌ Error generating recommendations: {str(e)}")
            raise AppException(e, sys) from e


if __name__ == "__main__":
    # Page configuration
    st.set_page_config(
        page_title="Books Recommender System",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Load custom CSS
    load_custom_css()
    
    # Header
    st.markdown("""
    <div class="header-container">
        <h1 class="header-title">📚 Books Recommender System</h1>
        <p class="header-subtitle">Discover your next favorite book with AI-powered recommendations</p>
    </div>
    """, unsafe_allow_html=True)

    obj = Recommendation()

    # Create two columns for buttons
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button('🚀 Train Recommender System'):
            with st.spinner('Training in progress...'):
                obj.train_engine()

    st.markdown("---")
    
    # Book selection
    st.markdown("### 🔍 Select a Book")
    book_names = pickle.load(open(os.path.join('templates', 'book_names.pkl'), 'rb'))
    selected_books = st.selectbox(
        "Type or select a book from the dropdown",
        book_names,
        key="book_selector"
    )

    # Recommendation button
    if st.button('✨ Show Recommendations'):
        with st.spinner('Finding recommendations...'):
            try:
                obj.recommendations_engine(selected_books)
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.info("Please check if the model is trained and all files are properly loaded.")
    
    # Add custom footer
    add_footer()
