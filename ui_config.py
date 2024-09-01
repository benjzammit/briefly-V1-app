import streamlit as st

def set_page_config():
    st.set_page_config(
        page_title="Briefly - Bridging the Gaps in Marketing Collaboration",
        page_icon=":bulb:",
        layout="wide",  # Use the full page width
    )

def add_footer():
    st.markdown(
        """
        <style>
            .footer {
                position: fixed;
                left: 0;
                bottom: 0;
                width: 100%;
                background-color: #f8f9fa;
                color: #616161;
                text-align: center;
                padding: 10px 0;
                font-size: 14px;
            }
            .footer a {
                color: #2962FF;
                text-decoration: none;
            }
            .footer a:hover {
                text-decoration: underline;
            }
            .footer-icon {
                vertical-align: middle;
                margin-right: 5px;
            }
        </style>
        <div class="footer">
            Built by Benjamin Zammit - Strategy and Implementation Manager at InDomo, a WPP Company.
            <br>
            <a href="https://www.linkedin.com/in/benjamin-zammit/" target="_blank">
                <img src="https://cdn-icons-png.flaticon.com/512/174/174857.png" alt="LinkedIn" class="footer-icon" width="16" height="16">
                Connect with me on LinkedIn
            </a>
        </div>
        """,
        unsafe_allow_html=True,
    )

def apply_custom_styles():
    st.markdown(
        """
        <style>
            /* General Styling */
            body {
                font-family: 'Roboto', sans-serif;
                background-color: #f8f9fa;
            }

            .title {
                text-align: center;
                font-size: 48px;
                font-weight: bold;
                color: #2962FF; /* Briefly Blue */ 
                margin-bottom: 10px;
            }

            .subtitle {
                text-align: center;
                font-size: 24px;
                color: #616161; /* Summit Gray */ 
                margin-bottom: 30px; 
            }

            .description {
                text-align: center;
                font-size: 18px;
                color: #616161; /* Summit Gray */
                line-height: 1.6;
                margin-bottom: 40px;
            }

            .how-it-works {
                padding-top: 40px;
                padding-bottom: 40px;
            }

            .how-it-works h2 {
                text-align: left;
                margin-bottom: 20px;
            }

            .how-it-works ol {
                text-align: left;
                margin: 0 auto;
                max-width: 800px;
                padding-left: 20px;
            }

            .how-it-works li {
                margin-bottom: 15px;
            }

            .benefit {
                text-align: center; /* Center content in benefits */
                padding: 30px 20px; /* Increased padding */
                border-radius: 12px; /* Softer corners */
                background-color: #ffffff; /* White background */
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); /* Subtle shadow */
                margin-bottom: 30px; /* Add margin between benefits */
                transition: transform 0.2s ease, box-shadow 0.2s ease; /* Add a hover effect */
            }

            .benefit:hover {
                transform: translateY(-5px); /* Lift on hover */
                box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2); /* Enhance shadow on hover */
            }

            .benefit h3 {
                color: #2962FF; /* Briefly Blue */
                margin-bottom: 10px; /* Add space below heading */
            }

            .trained-text {
                text-align: center;
                font-size: 18px;
                color: #616161; /* Summit Gray */
                margin-bottom: 30px;
            }

            .benefit-container {
                display: flex;
                flex-direction: column; /* Stack icon and text vertically */
                align-items: center; 
            }

            .benefit-icon {
                font-size: 48px; /* Larger icon */
                margin-bottom: 15px; /* Add space below icon */
                color: #FFA500; /* Spark Orange */
            }

            .suggestion-text {
                font-size: 16px; 
                font-weight: bold;
            }

            /* Style for metric box */
            .metric-container {
                border: 2px solid #f0f0f0;
                border-radius: 10px;
                padding: 20px;
                text-align: center;
                background-color: #ffffff; /* White background */
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); /* Subtle shadow */
            }

            .metric-value {
                font-size: 36px;
                font-weight: bold;
                color: #2962FF; /* Briefly Blue */
            }

            .metric-label {
                font-size: 18px;
                color: #616161; /* Summit Gray */
            }

            /* Accordion styling */
            .st-expander {
                background-color: #ffffff; /* White background */
                border-radius: 10px; /* Rounded corners */
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); /* Subtle shadow */
                margin-bottom: 20px; /* Space between accordions */
            }

            /* Button styling */
            .stButton>button {
                background-color: #2962FF; /* Briefly Blue */
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px 20px;
                font-size: 16px;
                cursor: pointer;
                transition: background-color 0.2s ease, transform 0.2s ease;
            }

            .stButton>button:hover {
                background-color: #0056b3; /* Darker blue on hover */
                transform: translateY(-2px); /* Slight lift on hover */
            }

            /* Gap Analysis and Competitors Section */
            .gap-analysis-title, .competitors-title, .sentiment-title {
                font-size: 24px;
                font-weight: bold;
                color: #2962FF; /* Briefly Blue */
                margin-bottom: 10px;
            }

            .gap-analysis-item {
                font-size: 16px;
                color: #616161; /* Summit Gray */
            }

            .highlight {
                background-color: #dff0d8; /* Light green background */
                border-left: 5px solid #3c763d; /* Dark green border */
                padding: 10px;
                margin-bottom: 10px;
            }

            .error-text {
                color: red;
                font-weight: bold;
            }

            /* Padding for columns */
            .stColumn {
                padding-left: 20px;
                padding-right: 20px;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )