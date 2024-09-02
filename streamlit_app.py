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
st.markdown(
    """
    <div class="background-container">
        <div class="overlay"></div>
        <div class="content">
            <h1 class="title">💡 Briefly.</h1>
            <p class="subtitle">&nbsp&nbspTransform Your Briefs, Transform Your Results.&nbsp&nbsp</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- How It Works Section ---
st.markdown('<h2 class="section-title">How It Works</h2>', unsafe_allow_html=True)
st.markdown(
    """
    <div class="section-description">
  <h3 style="text-align: center;">Unlock Your Marketing Potential with Briefly</h3> 
  <ol style="text-align: left; margin: 0 auto; max-width: 800px;">
    <li><strong>Share Your Brief:</strong> Upload your marketing brief (DOCX or PDF) – it's the first step to unlocking your campaign's full potential.</li>
    <li><strong>Expert Analysis:</strong> Our advanced AI dissects your brief, providing an in-depth analysis to pinpoint strengths and areas for improvement.</li>
    <li><strong>Receive Clear, Actionable Suggestions:</strong> Get targeted feedback on key areas like objectives, target audience, competitive landscape, channel strategy, KPIs, and more. </li>
    <li><strong>Transform Your Brief, Transform Your Results:</strong>  Use Briefly's insights to refine your strategy, create more impactful campaigns, and achieve your marketing goals with confidence.</li>
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
    <p class="section-description">
        Briefly combines the expertise of seasoned marketing professionals with the power of AI to help you craft marketing briefs that drive success. Our platform provides you with the tools and insights needed to ensure your campaigns are effective, targeted, and impactful.
    </p>
    """,
    unsafe_allow_html=True,
)

# Use the new CSS classes in your HTML structure
st.markdown('<div class="benefit-card-container">', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        """
        <div class="benefit-card">
            <div class="benefit-container">
                <span class="benefit-icon">🧠</span> 
                <h3 class="benefit-title">Get Expert Advice</h3>
            </div>
            <p class="benefit-description">Benefit from the collective wisdom of seasoned marketing professionals. Briefly's AI analyzes your brief and provides tailored recommendations based on industry best practices, ensuring your strategy is set up for success.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        """
        <div class="benefit-card">
            <div class="benefit-container">
                <span class="benefit-icon">💪</span> 
                <h3 class="benefit-title">Craft Briefs with Confidence</h3>
            </div>
            <p class="benefit-description">Eliminate the guesswork and uncertainty from brief creation. Briefly's intuitive platform guides you through each step, providing clear suggestions and actionable insights so you can build winning briefs every time.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        """
        <div class="benefit-card">
            <div class="benefit-container">
                <span class="benefit-icon">🚀</span> 
                <h3 class="benefit-title">Create Business Impact</h3>
            </div>
            <p class="benefit-description">Don't just launch campaigns—drive measurable results. Briefly helps you define clear objectives, track key metrics, and optimize your strategies to maximize your marketing ROI and achieve your business goals.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
st.markdown('</div>', unsafe_allow_html=True) # Close the benefit-card-container

# --- Understanding Your Scores Section ---
st.markdown("---")
st.header("What We Focus On To Score Your Briefs")
st.markdown(
    "Our expert analysis powered by AI evaluates your marketing brief across key areas to pinpoint strengths and highlight opportunities for improvement.  Click on each category below to learn more:"
)

# Category Explanations (Tabs)
categories = {
    "🎯 Clarity of Objectives": {
        "What We Look For": "Clearly defined, measurable, and achievable marketing objectives that align with your overall business goals.",
        "Why It Matters": "Clear objectives ensure everyone understands the goals and can work towards them effectively.",
        "Tips to Improve": " - Use the SMART framework (Specific, Measurable, Achievable, Relevant, Time-bound).<br> - Clearly link objectives to business outcomes.<br> - Ensure alignment across your marketing team."
    },
    "🤝 Strategic Alignment": {
        "What We Look For": "Clear links between your marketing campaign and your overall business objectives and strategies.",
        "Why It Matters": "Ensures your marketing efforts directly contribute to achieving your company's wider goals.",
        "Tips to Improve": " - Explicitly state how the campaign supports key business goals.<br> - Align marketing metrics with business KPIs.<br> - Communicate the campaign's strategic importance to stakeholders."
    },
    "👥 Target Audience Definition": {
        "What We Look For": "A well-defined target audience with specific demographics, psychographics, behaviors, and needs.",
        "Why It Matters": "Understanding your audience is crucial for crafting targeted messaging and choosing the right channels.",
        "Tips to Improve": " - Create detailed buyer personas.<br> - Conduct market research to understand your audience's needs and pain points.<br> - Use data to segment your audience for more targeted campaigns."
    },
    "⚔️ Competitive Analysis": {
        "What We Look For": "Thorough research on your competitors, highlighting their strengths, weaknesses, and your brand's unique value proposition.",
        "Why It Matters": "A strong competitive analysis helps you differentiate your offering and develop more effective strategies.",
        "Tips to Improve": " - Identify your top competitors.<br> - Analyze their marketing strategies, target audience, and messaging.<br> - Clearly articulate your competitive advantages."
    },
    "🗺️ Channel Strategy": {
        "What We Look For": "A strategic approach to channel selection, ensuring you reach your target audience in the most effective way.",
        "Why It Matters": "The right channels amplify your message and maximize your campaign's reach.",
        "Tips to Improve": " - Consider your target audience's preferred channels.<br> - Research the strengths and limitations of different channels.<br> - Use a mix of online and offline channels for a holistic approach."
    },
    "🔑 Key Performance Indicators (KPIs)": {
        "What We Look For": "Specific, measurable, and relevant KPIs that align with your objectives and allow you to track campaign performance.",
        "Why It Matters": "KPIs provide insights into what's working and what's not, enabling data-driven optimization.",
        "Tips to Improve": " - Choose KPIs that directly relate to your objectives.<br> - Set realistic and measurable targets for each KPI.<br> - Regularly track and analyze your KPIs to make data-driven adjustments."
    },
}

# CSS Styling 
st.markdown(
    """
    <style>
        /* Style for tab titles */
        button[data-baseweb="tab"] { 
            font-size: 18px !important; /* Adjust font size as needed */
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Create tabs
tabs = st.tabs(list(categories.keys()))

# Display content for each tab
for i, (category, details) in enumerate(categories.items()):
    with tabs[i]:
        st.markdown(f"**What We Look For:** {details['What We Look For']}")
        st.markdown(f"**Why It Matters:** {details['Why It Matters']}")
        st.markdown(f"**Tips to Improve:** {details['Tips to Improve']}", unsafe_allow_html=True)


# --- FAQ Section ---
st.markdown("---")
st.header("Frequently Asked Questions (FAQ)")

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