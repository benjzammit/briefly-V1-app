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
                color: #ffffff; /* White text for contrast */
                margin-bottom: 10px;
            }

            .subtitle {
                text-align: center;
                font-size: 24px;
                color: #ffffff; /* White text for contrast */
                margin-bottom: 30px; 
            }

            .background-container {
                position: relative;
                width: 100%;
                height: auto;
                background-image: url('https://www.wpp.com/en/-/media/project/wpp/images/wpp-iq/2023/creativepowerhousemain.jpg');
                background-size: cover;
                background-position: center;
                padding: 60px 20px;
                box-sizing: border-box;
            }

            .overlay {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0, 0, 0, 0.1); /* Semi-transparent overlay */
                z-index: 1;
            }

            .content {
                position: relative;
                z-index: 2;
            }

            .section-title {
                text-align: center;
                font-size: 36px;
                font-weight: bold;
                color: #2962FF; /* Briefly Blue */
                margin-top: 40px;
                margin-bottom: 20px;
            }

            .section-subtitle {
                text-align: center;
                font-size: 20px;
                color: #616161; /* Summit Gray */
                margin-bottom: 30px;
            }

            .section-description {
                text-align: center;
                font-size: 18px;
                color: #616161; /* Summit Gray */
                line-height: 1.6;
                margin-bottom: 40px;
            }

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

            /* Benefit Card Styles */
            .benefit-card-container {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
                gap: 20px; 
            }

            .benefit-card {
                background-color: #fff;
                border-radius: 8px;
                padding: 30px;
                box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.1);
                text-align: left; 
                display: flex; 
                flex-direction: column; 
            }

            .benefit-card .benefit-description {
                flex-grow: 1; 
            }

            .benefit-container { 
                display: flex;
                align-items: center; 
                margin-bottom: 15px; 
            }

            .benefit-icon {
                font-size: 28px; 
                margin-right: 10px; 
            }

            .benefit-title {
                color: #2962FF;
                font-size: 24px;
                margin-bottom: 0; 
            }

            .benefit-description {
                color: #616161;
                font-size: 16px;
                line-height: 1.5;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )