import streamlit as st
import pandas as pd
import google.generativeai as genai
import docx
import PyPDF2
import io
import json
from json_repair import repair_json
from textblob import TextBlob

# --- UI Configuration ---
st.set_page_config(
    page_title="Briefly - Bridging the Gaps in Marketing Collaboration",
    page_icon=":bulb:",
    layout="wide",  # Use the full page width
)

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

# --- Functions ---

# --- Load API Key from Secrets ---
api_key = "AIzaSyCkgn6nlhZR2V3lDag6kmyD-FmGch6dQzM"
genai.configure(api_key=api_key)

def extract_text_from_docx(file_bytes):
    doc = docx.Document(io.BytesIO(file_bytes))
    text = []
    for paragraph in doc.paragraphs:
        text.append(paragraph.text)
    return '\n'.join(text)

def extract_text_from_pdf(file_bytes):
    pdf_reader = PyPDF2.PdfFileReader(io.BytesIO(file_bytes))
    text = ""
    for page_num in range(pdf_reader.numPages):
        page = pdf_reader.getPage(page_num)
        text += page.extract_text()
    return text

def analyze_sentiment(text):
    blob = TextBlob(text)
    sentiment = blob.sentiment
    return sentiment.polarity, sentiment.subjectivity

def interpret_sentiment(polarity, subjectivity):
    if polarity <= -0.5:
        polarity_text = "The brief has a very negative tone, which might not be engaging. A negative tone can demotivate your audience and reduce the effectiveness of your messaging. Consider revising the content to include more positive and inspiring language."
    elif polarity < -0.1:
        polarity_text = "The brief has a somewhat negative tone. While it's important to address challenges, ensure that the overall message remains optimistic and solution-oriented to keep your audience engaged."
    elif polarity <= 0.1:
        polarity_text = "The brief has a neutral tone. This is balanced but may lack emotional impact. Consider adding elements that evoke positive emotions to make your message more compelling."
    elif polarity <= 0.5:
        polarity_text = "The brief has a positive tone, which is generally engaging. Positive language can inspire and motivate your audience, making your campaign more effective."
    else:
        polarity_text = "The brief has a very positive tone, which is highly engaging. A positive tone can significantly boost audience morale and drive better engagement and action."

    if subjectivity <= 0.3:
        subjectivity_text = "The brief is very objective, focusing on facts. While factual information is crucial, consider incorporating some subjective elements like testimonials or personal stories to connect emotionally with your audience."
    elif subjectivity <= 0.5:
        subjectivity_text = "The brief is fairly objective. This balance is good, but adding a bit more personal touch or opinion can make the content more relatable and persuasive."
    elif subjectivity <= 0.7:
        subjectivity_text = "The brief is somewhat subjective, focusing on opinions. While opinions can be powerful, ensure they are backed by facts to maintain credibility and trust."
    else:
        subjectivity_text = "The brief is very subjective, focusing heavily on opinions. High subjectivity can make the content feel biased. Balance it with factual information to strengthen your argument and credibility."

    return polarity_text, subjectivity_text

def generate_prompt(text):
    return f"""
    ## Marketing Brief Analysis Request

    Please analyze the following marketing brief and provide a structured response suitable for Python processing, with scores as numbers out of 100. 
    Extract specific details and insights where possible.

    **Marketing Brief Text:**

    ```
    {text}
    ```

    **Response Format:**

    ```json
    {{
      "overall_score": {{score}},
      "breakdown": {{
        "focus_clarity": {{
          "score": {{score}},
          "feedback": "{{feedback}}",
          "extracted_objectives": ["list of extracted objectives from the text"], 
          "keywords": ["list of relevant keywords"]
        }},
        "strategic_alignment": {{
          "score": {{score}},
          "feedback": "{{feedback}}",
          "alignment_issues": ["list of potential misalignments with business goals (if any)"]
        }},
        "target_audience": {{
          "score": {{score}},
          "feedback": "{{feedback}}",
          "extracted_demographics": ["age", "location", "interests", "other relevant demographics"],
          "target_audience_examples": ["specific examples of the target audience mentioned in the text"]
        }},
        "competitive_landscape": {{
          "score": {{score}},
          "feedback": "{{feedback}}",
          "competitors_mentioned": ["list of competitor brands mentioned"],
          "competitive_advantages": ["list of mentioned or implied competitive advantages"]
        }},
        "channel_strategy": {{
          "score": {{score}},
          "feedback": "{{feedback}}",
          "recommended_channels": ["list of potentially effective channels based on the brief"],
          "channel_justifications": ["reasons for recommending each channel"]
        }},
        "measurement_kpis": {{
          "score": {{score}},
          "feedback": "{{feedback}}",
          "extracted_kpis": ["list of KPIs mentioned in the brief"],
          "kpi_suggestions": ["suggestions for additional relevant KPIs"]
        }}
      }},
      "gap_analysis": [
            "List of missing elements (if any)",
            "Another missing element"
        ]
    }}
    """
    
def analyze_text(text):
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    prompt = generate_prompt(text)

    try:
        response = model.generate_content(prompt)
        response_text = response.text

        # --- Clean up the response ---
        response_text = clean_response(response_text)

        # --- Repair potentially malformed JSON ---
        try:
            response_text = repair_json(response_text)
        except Exception as e:
            print(f"Warning: json_repair could not fix the JSON: {e}")

        # Directly try to parse as JSON
        response_data = json.loads(response_text)

        # Extract data for DataFrame (corrected structure)
        data = {}

        for category, details in response_data['breakdown'].items():
            category_title = category.replace('_', ' ').title()
            
            # Store all details for the category in a dictionary
            data[category_title] = {
                'Score': int(details['score']),
                'Feedback': details['feedback'],
                'Extracted Objectives': details.get('extracted_objectives', []),
                'Keywords': details.get('keywords', []),
                'Alignment Issues': details.get('alignment_issues', []),
                'Extracted Demographics': details.get('extracted_demographics', []),
                'Target Audience Examples': details.get('target_audience_examples', []),
                'Competitors Mentioned': details.get('competitors_mentioned', []),
                'Competitive Advantages': details.get('competitive_advantages', []),
                'Recommended Channels': details.get('recommended_channels', []),
                'Channel Justifications': details.get('channel_justifications', []),
                'Extracted KPIs': details.get('extracted_kpis', []),
                'KPI Suggestions': details.get('kpi_suggestions', []),
                'Target Locations': details.get('target_locations', [])  # Add target locations extraction
            } 

        df_results = pd.DataFrame.from_dict(data, orient='index')
        overall_score = int(response_data['overall_score'])

        # Extract gap analysis results
        gap_analysis_results = response_data.get('gap_analysis', [])

        # Extract competitors mentioned
        competitors_mentioned = data['Competitive Landscape']['Competitors Mentioned']

        return df_results, overall_score, gap_analysis_results, competitors_mentioned 
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        print(f"Raw response: {response.text}")
        return None, None, None, []
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    prompt = generate_prompt(text)

    try:
        response = model.generate_content(prompt)
        response_text = response.text

        # --- Clean up the response ---
        response_text = clean_response(response_text)

        # --- Repair potentially malformed JSON ---
        try:
            response_text = repair_json(response_text)
        except Exception as e:
            print(f"Warning: json_repair could not fix the JSON: {e}")

        # Directly try to parse as JSON
        response_data = json.loads(response_text)

        # Extract data for DataFrame (corrected structure)
        data = {}

        for category, details in response_data['breakdown'].items():
            category_title = category.replace('_', ' ').title()
            
            # Store all details for the category in a dictionary
            data[category_title] = {
                'Score': int(details['score']),
                'Feedback': details['feedback'],
                'Extracted Objectives': details.get('extracted_objectives', []),
                'Keywords': details.get('keywords', []),
                'Alignment Issues': details.get('alignment_issues', []),
                'Extracted Demographics': details.get('extracted_demographics', []),
                'Target Audience Examples': details.get('target_audience_examples', []),
                'Competitors Mentioned': details.get('competitors_mentioned', []),
                'Competitive Advantages': details.get('competitive_advantages', []),
                'Recommended Channels': details.get('recommended_channels', []),
                'Channel Justifications': details.get('channel_justifications', []),
                'Extracted KPIs': details.get('extracted_kpis', []),
                'KPI Suggestions': details.get('kpi_suggestions', []),
                'Target Locations': details.get('target_locations', [])  # Add target locations extraction
            } 

        df_results = pd.DataFrame.from_dict(data, orient='index')
        overall_score = int(response_data['overall_score'])

        # Extract gap analysis results
        gap_analysis_results = response_data.get('gap_analysis', [])

        # Extract competitors mentioned
        competitors_mentioned = response_data['breakdown']['competitive_landscape']['competitors_mentioned']

        return df_results, overall_score, gap_analysis_results, competitors_mentioned 
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        print(f"Raw response: {response.text}")
        return None, None, None, []

def clean_response(response_text):
    """Cleans up the response text before JSON parsing."""
    # 1. Remove leading/trailing whitespace:
    response_text = response_text.strip()

    # 2. Remove backticks (if present):
    response_text = response_text.replace("```json", "")
    response_text = response_text.replace("```", "")

    # 3. Remove potential BOM (Byte Order Mark) characters:
    response_text = response_text.encode("utf-8", "ignore").decode("utf-8")

    return response_text

def parse_and_improve(df, overall_score):
    improvement_areas = {}

    for category, row in df.iterrows():
        improvement_areas[category] = {
            "Suggestions": [],
            "Examples": []
        }

        if category == 'Focus & Clarity':
            if row['Extracted Objectives']:
                improvement_areas[category]["Suggestions"].append(
                    f"Consider refining the following objectives to ensure they are clear, measurable, and ambitious: {', '.join(row['Extracted Objectives'])}"
                )
            else:
                improvement_areas[category]["Suggestions"].append(
                    "Clearly define specific, measurable, achievable, relevant, and time-bound (SMART) objectives for the campaign."
                )

            if row['Keywords']:
                improvement_areas[category]["Suggestions"].append(
                    f"Ensure these keywords are strategically and consistently incorporated throughout the marketing materials to enhance visibility, searchability, and reach: {', '.join(row['Keywords'])}"
                )

        elif category == 'Strategic Alignment':
            if row['Alignment Issues']:
                improvement_areas[category]["Suggestions"].append(
                    f"Carefully review and address the following potential misalignments with overall business goals to ensure the campaign effectively contributes to key strategic priorities: {', '.join(row['Alignment Issues'])}"
                )
            else:
                improvement_areas[category]["Suggestions"].append(
                    "Clearly articulate how the campaign directly aligns with and supports the company's overall marketing and business objectives. Provide specific examples to demonstrate the connection."
                )

        elif category == 'Target Audience':
            if row['Extracted Demographics'] or row['Target Audience Examples']:
                if row['Extracted Demographics']:
                    demographics_str = ', '.join(row['Extracted Demographics'])
                    improvement_areas[category]["Suggestions"].append(
                        f"Refine targeting by providing more specific information about the desired audience. Consider these extracted demographics: {demographics_str}"
                    )
                if row['Target Audience Examples']:
                    examples_str = ', '.join(row['Target Audience Examples'])
                    improvement_areas[category]["Suggestions"].append(
                        f"While '{examples_str}' provides a starting point, explore and define the target audience more comprehensively. Include demographics, psychographics, behaviors, and needs."
                    )
            else:
                improvement_areas[category]["Suggestions"].append(
                    "Define a specific target audience by considering demographics, psychographics, behaviors, and needs. Avoid overly broad descriptions."
                )

        elif category == 'Competitive Landscape':
            if row['Competitors Mentioned']:
                improvement_areas[category]["Suggestions"].append(
                    f"Conduct a thorough analysis of these competitors to identify opportunities for differentiation and develop effective competitive strategies: {', '.join(row['Competitors Mentioned'])}"
                )
            else:
                improvement_areas[category]["Suggestions"].append(
                    "Research and identify key competitors. Analyze their strengths, weaknesses, target audience, and marketing strategies. Use this information to differentiate your offering and highlight its unique value proposition."
                )

            if row['Competitive Advantages']:
                improvement_areas[category]["Suggestions"].append(
                    f"Clearly and compellingly highlight these competitive advantages in your messaging and positioning to stand out in the market: {', '.join(row['Competitive Advantages'])}"
                )
            else:
                improvement_areas[category]["Suggestions"].append(
                        "Identify and clearly articulate your competitive advantages. What makes your product/service stand out from the competition? Highlight these advantages in your messaging."
                    )

        elif category == 'Channel Strategy':
            if row['Recommended Channels']:
                improvement_areas[category]["Suggestions"].append(
                    f"Evaluate the suitability of these channels for your target audience and campaign objectives: {', '.join(row['Recommended Channels'])}"
                )
            else:
                improvement_areas[category]["Suggestions"].append(
                    "Develop a comprehensive channel strategy that outlines the specific channels to be used (e.g., social media, email, paid advertising, content marketing). Justify the selection of each channel based on its relevance to the target audience and campaign goals."
                )

            # Instead of just listing justifications, integrate them into the channel suggestions
            if row['Channel Justifications']:
                for i, justification in enumerate(row['Channel Justifications']):
                    if i < len(row['Recommended Channels']):
                        channel = row['Recommended Channels'][i]
                        improvement_areas[category]["Suggestions"].append(f" - **{channel}:** {justification}")

        elif category == 'Measurement & KPIs':
            if row['Extracted KPIs']:
                improvement_areas[category]["Suggestions"].append(
                    f"Establish a system for consistently tracking and measuring these KPIs to evaluate campaign performance and make data-driven adjustments: {', '.join(row['Extracted KPIs'])}"
                )
            else:
                improvement_areas[category]["Suggestions"].append(
                    "Define specific and measurable KPIs to track the success of your campaign. Consider metrics related to your objectives, such as website traffic, lead generation, sales conversions, brand awareness, or customer satisfaction."
                )

            if row['KPI Suggestions']:
                improvement_areas[category]["Suggestions"].extend(
                    [f"- Consider tracking {suggestion} to gain additional insights into campaign effectiveness." for suggestion in row['KPI Suggestions']]
                )

    return improvement_areas
    
def rewrite_brief(original_text, df_results):
    """Generates an improved marketing brief using Google Gemini."""

    # Construct a prompt incorporating feedback from the analysis
    prompt = f"""
    ## Marketing Brief Rewriter

    Here's an original marketing brief:
    ```
    {original_text}
    ```

    Based on an analysis, here are some areas for improvement:
    """
    suggestions = {}
    from_to_quotes = {}

    for category, details in df_results.iterrows():
        prompt += f"**{category.title()}:** {details['Feedback']}\n"
        
        # Generate suggestions based on missing elements
        if category == 'Competitive Landscape' and not details['Competitors Mentioned']:
            competitors = ["Competitor A", "Competitor B", "Competitor C"]
            suggestions[category] = f"Consider adding relevant competitors such as {', '.join(competitors)} to better understand the competitive landscape."
            from_to_quotes[category] = {
                "from": "No competitors mentioned.",
                "to": f"Added relevant competitors such as {', '.join(competitors)}."
            }
            prompt += f"Add relevant competitors such as {', '.join(competitors)}.\n"
        elif category == 'Target Audience' and not details['Extracted Demographics']:
            demographics = ["age 25-34", "gender: female", "location: New York", "interests: fitness, wellness"]
            suggestions[category] = f"Specify target demographics such as {', '.join(demographics)} to tailor your strategy effectively."
            from_to_quotes[category] = {
                "from": "No target demographics specified.",
                "to": f"Included target demographics such as {', '.join(demographics)}."
            }
            prompt += f"Include target demographics such as {', '.join(demographics)}.\n"
        elif category == 'Channel Strategy' and not details['Recommended Channels']:
            channels = ["social media", "email marketing", "paid advertising"]
            suggestions[category] = f"Include recommended channels such as {', '.join(channels)} to reach your audience more effectively."
            from_to_quotes[category] = {
                "from": "No recommended channels mentioned.",
                "to": f"Recommended channels such as {', '.join(channels)}."
            }
            prompt += f"Recommend channels such as {', '.join(channels)}.\n"
        elif category == 'Measurement Kpis' and not details['Extracted KPIs']:
            kpis = ["conversion rate", "click-through rate", "customer acquisition cost"]
            suggestions[category] = f"Define specific KPIs such as {', '.join(kpis)} to measure the success of your campaign."
            from_to_quotes[category] = {
                "from": "No KPIs defined.",
                "to": f"Included KPIs such as {', '.join(kpis)}."
            }
            prompt += f"Include KPIs such as {', '.join(kpis)}.\n"
        else:
            # For other categories or if already specified, include general improvements
            from_to_quotes[category] = {
                "from": details['Feedback'],
                "to": f"Enhanced {category.lower()} based on feedback."
            }

    prompt += """
    Please rewrite the brief, addressing the feedback provided and making it as strong as possible. 
    Maintain the original core message and objectives. Use crisp and clear language, and ensure the brief is detailed, actionable, and relevant.
    """

    model = genai.GenerativeModel(model_name="gemini-1.5-flash")  # Or your preferred Gemini model
    response = model.generate_content(prompt)
    
    # Debugging output
    print("Generated Prompt:", prompt)
    print("Suggestions:", suggestions)
    print("From-To Quotes:", from_to_quotes)

    return response.text, suggestions, from_to_quotes

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
            <li><strong>Receive Feedback:</strong> Get feedback on focus clarity, strategic alignment, target audience, competitive landscape, channel strategy, and measurement KPIs.</li>
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

        # --- Analyze the Text ---
        with st.spinner("Analyzing your brief..."):
            df_results, overall_score, gap_analysis_results, competitors_mentioned = analyze_text(document_text) 

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

                target_locations = df_results.loc['Target Audience', 'Target Locations'] if 'Target Audience' in df_results.index else []

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
                    - **Target Audience:** From "No target demographics specified" to "Included target demographics such as age 25-34, gender: female, location: New York, interests: fitness, wellness."
                    - **Competitive Landscape:** From "No competitors mentioned" to "Added relevant competitors such as Competitor A, Competitor B, Competitor C."
                    - **Measurement KPIs:** From "No KPIs defined" to "Included KPIs such as conversion rate, click-through rate, customer acquisition cost."
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

# --- FAQ Section ---
st.markdown("---")
st.header("❓ Frequently Asked Questions (FAQ)")

faq_items = [
    {
        "question": "How does Briefly analyze my marketing brief?",
        "answer": """
        Briefly uses advanced natural language processing (NLP) techniques and machine learning models to analyze your marketing brief. 
        It evaluates various aspects such as focus clarity, strategic alignment, target audience, competitive landscape, channel strategy, and measurement KPIs.
        """
    },
    {
        "question": "What metrics are used in the analysis?",
        "answer": """
        The analysis includes several metrics:
        - **Focus Clarity:** Evaluates how clear and concise the objectives are.
        - **Strategic Alignment:** Checks if the brief aligns with overall business goals.
        - **Target Audience:** Assesses the specificity and relevance of the target audience.
        - **Competitive Landscape:** Identifies competitors and competitive advantages.
        - **Channel Strategy:** Recommends effective channels for the campaign.
        - **Measurement KPIs:** Suggests key performance indicators to track success.
        """
    },
    {
        "question": "Can I see examples of improvements?",
        "answer": """
        Yes, here are some examples:
        - **Target Audience:** From "No target demographics specified" to "Included target demographics such as age 25-34, gender: female, location: New York, interests: fitness, wellness."
        - **Competitive Landscape:** From "No competitors mentioned" to "Added relevant competitors such as Competitor A, Competitor B, Competitor C."
        - **Measurement KPIs:** From "No KPIs defined" to "Included KPIs such as conversion rate, click-through rate, customer acquisition cost."
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