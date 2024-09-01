import streamlit as st
import pandas as pd
import docx
import io
import asyncio
import ui_config

from text_extraction import extract_text_from_docx, extract_text_from_pdf
from sentiment_analysis import analyze_sentiment, interpret_sentiment
from ai_analysis import analyze_text_async, rewrite_brief
from utils import parse_and_improve
from ui_config import add_footer

# --- UI Configuration ---
ui_config.set_page_config()
ui_config.apply_custom_styles()

# --- Main App ---
st.markdown('<h1 class="title">💡 Briefly</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Crafting Briefs That Inspire Marketing Success</p>', unsafe_allow_html=True)

# --- Trained on Marketing Briefs Text ---
st.markdown(
    '<p class="description">In the world of marketing, a well-crafted brief is the difference between mediocrity and exceptional results. Briefly empowers you to align expectations, unlock creative potential, and drive measurable results.</p>',
    unsafe_allow_html=True,
)

# Add a brief description of how to use the app
st.markdown(
    """
    <div class="description">
        <h2>How It Works</h2>
        <ol style="text-align: left; margin: 0 auto; max-width: 800px;">
            <li><strong>Upload Your Brief:</strong> Upload your marketing brief in DOCX or PDF format.</li>
            <li><strong>AI Analysis:</strong> Our AI analyzes your brief to provide actionable insights.</li>
            <li><strong>Receive Feedback:</strong> Get feedback on clarity of objectives, strategic alignment, target audience definition, competitive analysis, channel strategy, and key performance indicators (KPIs).</li>
            <li><strong>Drive Results:</strong> Use the insights to create more effective and impactful marketing campaigns that drive results.</li>
        </ol>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- File Upload ---
uploaded_file = st.file_uploader(
    "Upload Your Marketing Brief (DOCX or PDF)", type=["docx", "pdf"], accept_multiple_files=False
)

# --- Process Uploaded File ---
if uploaded_file is not None:
    try:
        file_bytes = uploaded_file.read()

        if uploaded_file.name.endswith(".docx"):
            document_text = extract_text_from_docx(file_bytes)
        elif uploaded_file.name.endswith(".pdf"):
            document_text = extract_text_from_pdf(file_bytes)
        else:
            st.error("Unsupported file type. Please upload a DOCX or PDF file.")
            st.stop()  # Stop execution if the file type is invalid

        if document_text is None:
            st.error("Failed to extract text from the uploaded file. Please try again with a different file.")
            st.stop()

        # --- Analyze the Text ---
        with st.spinner("Analyzing your brief..."):
            df_results, overall_score, gap_analysis_results, competitors_mentioned = asyncio.run(analyze_text_async(document_text))

        # Store analysis results in session state
        st.session_state['df_results'] = df_results
        st.session_state['overall_score'] = overall_score
        st.session_state['gap_analysis_results'] = gap_analysis_results
        st.session_state['competitors_mentioned'] = competitors_mentioned
        st.session_state['document_text'] = document_text

        # --- Perform Sentiment Analysis ---
        polarity, subjectivity = analyze_sentiment(document_text)
        polarity_text, subjectivity_text = interpret_sentiment(polarity, subjectivity)

        # Store sentiment analysis in session state
        st.session_state['polarity_text'] = polarity_text
        st.session_state['subjectivity_text'] = subjectivity_text

        # --- Display Results ---
        if df_results is not None:
            st.markdown("---")  # Add a visual separator

            # Overall Score and Feedback
            st.header("Overall Score")
            col1, col2 = st.columns([1, 4])  # Adjust column ratios as needed
            col1.metric("", f"{overall_score}/100")

            with col2:
                if overall_score >= 90:
                    st.success("Excellent! Your marketing brief is very strong.")
                elif overall_score >= 70:
                    st.success("Great job! Your brief is well-structured and informative.")
                elif overall_score >= 50:
                    st.warning("Your brief shows potential, but there's room for improvement.")
                else:
                    st.error("Your brief needs significant work to be effective.")

            # Detailed Breakdown (Exclude Extracted Data Columns, Adjust Column Widths)
            st.markdown("---")
            st.header("Detailed Analysis & Feedback")
            relevant_columns = ['Score', 'Feedback']  # Only include relevant columns
            df_display = df_results[relevant_columns].style.format({"Score": "{:.0f}"}).set_properties(**{'text-align': 'left'})

            # Adjust column widths (example)
            df_display.set_table_styles([
                {'selector': 'th.col_heading', 'props': [('text-align', 'left')]},
                {'selector': 'th.col_heading.level0', 'props': [('max-width', '150px')]}, # Adjust width as needed
                {'selector': 'td', 'props': [('word-wrap', 'break-word')]} # Wrap text to new lines
            ])

            st.dataframe(df_display, use_container_width=True)

            # --- Competitors and Target Location/Market Section ---
            st.markdown("---")
            col1, col2 = st.columns(2)

            with col1:
                st.markdown('<h3 class="competitors-title">🏢 Competitors</h3>', unsafe_allow_html=True)

                if competitors_mentioned:
                    st.markdown("The following competitors were mentioned in your brief:")
                    for competitor in competitors_mentioned:
                        st.markdown(f"- {competitor}")
                else:
                    st.markdown('<p class="error-text">No competitors were mentioned in your brief.</p>', unsafe_allow_html=True)
                    st.markdown("Identifying competitors helps you understand the market landscape and differentiate your offering.")

            with col2:
                st.markdown('<h3 class="competitors-title">🌍 Target Location/Market</h3>', unsafe_allow_html=True)

                target_locations = df_results.loc['Target Audience Definition', 'Target Locations'] if 'Target Audience Definition' in df_results.index else []

                if target_locations:
                    st.markdown("The following target locations/markets were mentioned in your brief:")
                    for location in target_locations:
                        st.markdown(f"- {location}")
                else:
                    st.markdown('<p class="error-text">No target locations/markets were mentioned in your brief.</p>', unsafe_allow_html=True)
                    st.markdown("Specifying target locations/markets helps tailor your strategy to specific regions and audiences.")

            # --- Sentiment and Gap Analysis Section ---
            st.markdown("---")
            col1, col2 = st.columns([1, 1], gap="large")  # Add gap between columns

            with col1:
                st.markdown('<h3 class="sentiment-title">😊 Sentiment Analysis</h3>', unsafe_allow_html=True)
                st.write(polarity_text)
                st.write(subjectivity_text)

            with col2:
                st.markdown('<h3 class="gap-analysis-title">🔍 Gap Analysis</h3>', unsafe_allow_html=True)

                if gap_analysis_results:
                    st.markdown("The following elements appear to be missing from your brief:")
                    for item in gap_analysis_results:
                        st.markdown(f'<li class="gap-analysis-item">{item}</li>', unsafe_allow_html=True)
                else:
                    st.success("✅ No missing elements detected! Your brief looks comprehensive.")

            # Areas for Improvement (using accordions)
            st.markdown("---")
            st.header("Actionable Insights")
            improvement_areas = parse_and_improve(df_results, overall_score)

            for category, details in improvement_areas.items():
                score = df_results.loc[category, 'Score'] # Get the score for the category
                with st.expander(f"**{category} ({score}/100)**"):  # Include score in title
                    st.markdown("""
                    <style>
                        .suggestion-text {
                            font-size: 16px; 
                        }
                    </style>
                    """, unsafe_allow_html=True)

                    # Display short description (taken from the 'Feedback' column)
                    st.markdown(f"<p class='suggestion-text'>{df_results.loc[category, 'Feedback']}</p>", unsafe_allow_html=True)

                    # Display suggestions
                    st.markdown("<p class='suggestion-text'><strong>Suggestions:</strong></p>", unsafe_allow_html=True)
                    for suggestion in details["Suggestions"]:
                        st.write(f"- {suggestion}")

                    # Access and display extracted data 
                    for col in df_results.columns:
                        if col not in ['Score', 'Feedback', 'Suggestions', 'Examples'] and df_results.loc[category, col]: 
                            values = df_results.loc[category, col]
                            st.write(f"**{col.replace('_', ' ').title()}: {', '.join(values) if isinstance(values, list) else values}")

            # --- Improved Brief Section ---
            st.markdown("---")
            st.header("✨ Improved Brief (Premium Feature)")
            st.markdown("This section provides an improved version of your brief based on our analysis. Upgrade to access full features!")

            if st.button("Generate Improved Brief"):
                with st.spinner("Generating improved brief..."):
                    improved_brief, suggestions, from_to_quotes = rewrite_brief(st.session_state['document_text'], st.session_state['df_results'])

                st.success("Your improved brief is ready!")
                
                # Display original and improved briefs side by side
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown('<h3 class="sentiment-title">Original Brief</h3>', unsafe_allow_html=True)
                    st.text_area("Original Brief", value=st.session_state['document_text'], height=300)
                
                with col2:
                    st.markdown('<h3 class="sentiment-title">Improved Brief</h3>', unsafe_allow_html=True)
                    st.text_area("Improved Brief", value=improved_brief, height=300, key="improved_brief")

                # --- Download Button (Word DOCX) ---
                doc = docx.Document()
                doc.add_paragraph(improved_brief)
                doc_bytes = io.BytesIO()
                doc.save(doc_bytes)
                doc_bytes.seek(0)

                st.download_button(
                    label="Download Improved Brief (DOCX)",
                    data=doc_bytes,
                    file_name="improved_brief.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )

                # --- Major Improvements Section ---
                st.markdown("---")
                st.header("📈 Major Improvements")
                st.markdown("""
                    In this section, we highlight major improvements made to your marketing brief. These improvements are based on a detailed analysis and aim to enhance the effectiveness of your brief.
                    Below are some examples of changes made:
                    - **Target Audience Definition:** From "No target demographics specified" to "Included target demographics such as age 25-34, gender: female, location: New York, interests: fitness, wellness."
                    - **Competitive Analysis:** From "No competitors mentioned" to "Added relevant competitors such as Competitor A, Competitor B, Competitor C."
                    - **Key Performance Indicators (KPIs):** From "No KPIs defined" to "Included KPIs such as conversion rate, click-through rate, customer acquisition cost."
                """)
                if from_to_quotes:
                    for category, quotes in from_to_quotes.items():
                        with st.expander(f"**{category}**"):
                            st.markdown(f"**From:** {quotes['from']}")
                            st.markdown(f"**To:** {quotes['to']}")
                else:
                    st.markdown("No additional suggestions were generated.")

        else:
            st.error("Error analyzing the text. Please try again.")

    except Exception as e:
        st.error(f"An error occurred: {e}")

# --- Benefits Section ---
st.markdown("---")
st.header("Why Choose Briefly?")
st.markdown(
    """
    <p class="description">
        Briefly combines the expertise of seasoned marketing professionals with the power of AI to help you craft marketing briefs that drive success. Our platform provides you with the tools and insights needed to ensure your campaigns are effective, targeted, and impactful.
    </p>
    """,
    unsafe_allow_html=True,
)

col1, col2, col3 = st.columns(3) # Create 3 columns

with col1:
    st.markdown(
        """
        <div class="benefit">
            <div class="benefit-container">
                <span class="benefit-icon">🎯</span> 
                <h3>A Foundation for Success</h3>
            </div>
            <p>Briefly provides the framework and expert guidance to craft briefs that inspire confidence and clarity. We help you articulate your vision, define measurable objectives, and ensure everyone is on the same page from day one.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        """
        <div class="benefit">
            <div class="benefit-container">
                <span class="benefit-icon">⚙️</span> 
                <h3>Streamlined Collaboration</h3>
            </div>
            <p>Briefly facilitates seamless communication and collaboration, eliminating ambiguity and reducing time-consuming revisions. It's like having an experienced marketing director guiding your team every step of the way.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        """
        <div class="benefit">
            <div class="benefit-container">
                <span class="benefit-icon">📊</span> 
                <h3>Data-Driven Insights</h3>
            </div>
            <p>Briefly goes beyond gut feelings. Our analysis provides actionable insights, identifies potential gaps, and helps you refine your strategy for maximum impact.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --- Score Explanation Table ---
st.markdown("---")
st.header("Understanding Your Scores")
st.markdown(
    """
    <p class="description">
        The following table explains the criteria used to evaluate your marketing brief. Each criterion is crucial for creating an effective and impactful marketing campaign.
    </p>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="table-container">
        <table class="score-table">
            <thead>
                <tr>
                    <th>Criterion</th>
                    <th>Description</th>
                    <th>Importance</th>
                    <th>Tips for Improvement</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Clarity of Objectives</td>
                    <td>Evaluates how clear and specific the objectives of the marketing brief are.</td>
                    <td>Clear objectives help ensure everyone understands the goals and can work towards them effectively.</td>
                    <td>Define specific, measurable, achievable, relevant, and time-bound (SMART) objectives.</td>
                </tr>
                <tr>
                    <td>Strategic Alignment</td>
                    <td>Checks if the brief aligns with overall business goals and strategies.</td>
                    <td>Ensures the marketing efforts support the broader business objectives.</td>
                    <td>Clearly articulate how the campaign supports the company's overall marketing and business objectives.</td>
                </tr>
                <tr>
                    <td>Target Audience Definition</td>
                    <td>Assesses how well-defined and relevant the target audience is.</td>
                    <td>A well-defined target audience helps tailor the marketing strategy to reach the right people.</td>
                    <td>Specify demographics, psychographics, behaviors, and needs of the target audience.</td>
                </tr>
                <tr>
                    <td>Competitive Analysis</td>
                    <td>Identifies competitors and competitive advantages mentioned in the brief.</td>
                    <td>Understanding competitors helps differentiate your offering and develop effective strategies.</td>
                    <td>Research and identify key competitors, analyze their strengths and weaknesses, and highlight your unique value proposition.</td>
                </tr>
                <tr>
                    <td>Channel Strategy</td>
                    <td>Recommends effective channels for the campaign based on the brief.</td>
                    <td>Choosing the right channels ensures the message reaches the target audience effectively.</td>
                    <td>Develop a comprehensive channel strategy and justify the selection of each channel based on its relevance to the audience.</td>
                </tr>
                <tr>
                    <td>Key Performance Indicators (KPIs)</td>
                    <td>Suggests key performance indicators to track the success of the campaign.</td>
                    <td>KPIs help measure the effectiveness of the campaign and guide data-driven adjustments.</td>
                    <td>Define specific and measurable KPIs related to your objectives, such as website traffic, lead generation, and sales conversions.</td>
                </tr>
            </tbody>
        </table>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- FAQ Section ---
st.markdown("---")
st.header("❓ Frequently Asked Questions (FAQ)")

faq_items = [
    {
        "question": "How does Briefly analyze my marketing brief?",
        "answer": """
        Briefly uses advanced natural language processing (NLP) techniques and machine learning models to analyze your marketing brief. 
        It evaluates various aspects such as clarity of objectives, strategic alignment, target audience definition, competitive analysis, channel strategy, and key performance indicators (KPIs).
        """
    },
    {
        "question": "What metrics are used in the analysis?",
        "answer": """
        The analysis includes several metrics:
        
        | Criterion                  | Description                                                                                      | Importance                                                                                           | Tips for Improvement                                                                                                                                           |
        |----------------------------|--------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------|
        | Clarity of Objectives      | Evaluates how clear and specific the objectives of the marketing brief are.                      | Clear objectives help ensure everyone understands the goals and can work towards them effectively.   | Define specific, measurable, achievable, relevant, and time-bound (SMART) objectives.                                     |
        | Strategic Alignment        | Checks if the brief aligns with overall business goals and strategies.                           | Ensures the marketing efforts support the broader business objectives.                               | Clearly articulate how the campaign supports the company's overall marketing and business objectives.                      |
        | Target Audience Definition | Assesses how well-defined and relevant the target audience is.                                   | A well-defined target audience helps tailor the marketing strategy to reach the right people.        | Specify demographics, psychographics, behaviors, and needs of the target audience.                                         |
        | Competitive Analysis       | Identifies competitors and competitive advantages mentioned in the brief.                        | Understanding competitors helps differentiate your offering and develop effective strategies.        | Research and identify key competitors, analyze their strengths and weaknesses, and highlight your unique value proposition. |
        | Channel Strategy           | Recommends effective channels for the campaign based on the brief.                               | Choosing the right channels ensures the message reaches the target audience effectively.             | Develop a comprehensive channel strategy and justify the selection of each channel based on its relevance to the audience.  |
        | Key Performance Indicators (KPIs) | Suggests key performance indicators to track the success of the campaign.                          | KPIs help measure the effectiveness of the campaign and guide data-driven adjustments.               | Define specific and measurable KPIs related to your objectives, such as website traffic, lead generation, and sales conversions. |
        """
    },
    {
        "question": "Can I see examples of improvements?",
        "answer": """
        Yes, here are some examples:
        - **Target Audience Definition:** From "No target demographics specified" to "Included target demographics such as age 25-34, gender: female, location: New York, interests: fitness, wellness."
        - **Competitive Analysis:** From "No competitors mentioned" to "Added relevant competitors such as Competitor A, Competitor B, Competitor C."
        - **Key Performance Indicators (KPIs):** From "No KPIs defined" to "Included KPIs such as conversion rate, click-through rate, customer acquisition cost."
        """
    },
    {
        "question": "How are the scores calculated?",
        "answer": """
        Scores are calculated based on a combination of factors including clarity, relevance, completeness, and alignment with best practices. 
        Each aspect of the brief is evaluated and given a score out of 100, which contributes to the overall score.
        """
    },
    {
        "question": "What should I do if my brief has a low score?",
        "answer": """
        If your brief has a low score, review the detailed feedback and suggestions provided. Focus on improving areas with the lowest scores first. 
        Use the actionable insights to refine your objectives, better define your target audience, align your strategy with business goals, and specify clear KPIs.
        """
    }
]

for item in faq_items:
    with st.expander(item["question"]):
        st.markdown(item["answer"])

add_footer()