import streamlit as st
import pandas as pd
import google.generativeai as genai
import docx
import PyPDF2
import io
import json
from json_repair import repair_json

# --- UI Configuration ---
st.set_page_config(
    page_title="Briefly - Marketing Brief Analyzer",
    page_icon=":bulb:",
    layout="wide",  # Use the full page width
)

# --- Custom CSS for Styling ---
st.markdown(
    """
    <style>
        .title {
            text-align: center;
            font-size: 48px;
            font-weight: bold;
            color: #007bff; /* Electric Blue */ 
            margin-bottom: 10px;
        }

        .subtitle {
            text-align: center;
            font-size: 20px;
            color: #616161; 
            margin-bottom: 30px; 
        }

        .benefit {
            text-align: center; /* Center content in benefits */
            padding: 30px 20px; /* Increased padding */
            border-radius: 12px; /* Softer corners */
            background-color: #f8f9fa; /* Light neutral background */
            box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);
            margin-bottom: 30px; /* Add margin between benefits */
            transition: transform 0.2s ease; /* Add a hover effect */
        }

        .benefit:hover {
            transform: translateY(-5px); /* Lift on hover */
        }

        .benefit h3 {
            color: #007bff; /* Electric Blue */
            margin-bottom: 10px; /* Add space below heading */
        }

        .trained-text {
            text-align: center;
            font-size: 18px;
            color: #616161;
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
            color: #ffa500; /* Vibrant Orange */
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
        }

        .metric-value {
            font-size: 36px;
            font-weight: bold;
            color: #007bff; /* Electric Blue */
        }

        .metric-label {
            font-size: 18px;
            color: #616161;
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

def generate_prompt(text):
    return f"""
    ## Marketing Brief Analysis Request

    Please analyze the following marketing brief across key dimensions.
    Provide a structured response suitable for Python processing, with scores as numbers out of 100.

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
          "feedback": "{{feedback}}"
        }},
        "strategic_alignment": {{
          "score": {{score}},
          "feedback": "{{feedback}}"
        }},
        "target_audience": {{
          "score": {{score}},
          "feedback": "{{feedback}}"
        }},
        "competitive_landscape": {{
          "score": {{score}},
          "feedback": "{{feedback}}"
        }},
        "channel_strategy": {{
          "score": {{score}},
          "feedback": "{{feedback}}"
        }},
        "measurement_kpis": {{
          "score": {{score}},
          "feedback": "{{feedback}}"
        }}
      }}
    }}
    ```
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

        # Extract data for DataFrame
        data = {
            'Category': [],
            'Score': [],
            'Feedback': []
        }
        for category, details in response_data['breakdown'].items():
            data['Category'].append(category.replace('_', ' ').title())
            data['Score'].append(int(details['score']))  # Convert score to integer
            data['Feedback'].append(details['feedback'])

        df_results = pd.DataFrame(data)
        df_results.set_index('Category', inplace=True)

        # Get overall score from response_data
        overall_score = int(response_data['overall_score'])

        return df_results, overall_score  # Return overall
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        print(f"Raw response: {response.text}")
        return None

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
        score = row['Score']
        feedback = row['Feedback']

        if score < 60:  # Adjust the threshold as needed
            improvement_areas[category] = {
                "Suggestions": [
                    f"Improve the clarity and focus of the text in '{category}'.",
                    "Provide specific examples and measurable objectives.",
                    "Ensure alignment with the target audience's needs and preferences."
                ],
                "Examples": [
                    "For 'Focus & Clarity': Instead of vague objectives like 'make lots of sales', specify 'increase sales by 20% over the next quarter'.",
                    "For 'Target Audience Understanding': Instead of 'everyone', define 'target audience as urban millennials interested in sustainable products'."
                ]
            }
        else:
            improvement_areas[category] = {
                "Suggestions": [
                    f"Great job on '{category}'. Continue to maintain the level of detail and clarity.",
                    "Keep refining and updating based on ongoing feedback and results."
                ],
                "Examples": [
                    "For 'Channel Strategy & Tactics': Continue leveraging data-driven insights to optimize channel selection.",
                    "For 'Measurement & KPIs': Ensure KPIs are regularly tracked and adjusted as needed."
                ]
            }

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
    for category, details in df_results.iterrows():
        prompt += f"**{category.title()}:** {details['Feedback']}\n"

    prompt += """
    Please rewrite the brief, addressing the feedback provided and making it as strong as possible. 
    Maintain the original core message and objectives.
    """

    model = genai.GenerativeModel(model_name="gemini-1.5-flash")  # Or your preferred Gemini model
    response = model.generate_content(prompt)
    return response.text

# --- Main App ---
st.markdown('<h1 class="title">💡 Briefly</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Elevate Your Marketing Briefs with AI-Powered Insights</p>', unsafe_allow_html=True)

# --- Trained on Marketing Briefs Text ---
st.markdown(
    '<p class="trained-text">Briefly is trained on a massive dataset of high-performing marketing briefs to help you craft winning strategies.</p>',
    unsafe_allow_html=True,
)

# --- Benefits Section (using st.columns) ---
col1, col2, col3 = st.columns(3) # Create 3 columns

with col1:
    st.markdown(
        """
        <div class="benefit">
            <div class="benefit-container">
                <span class="benefit-icon">🎯</span> 
                <h3>Target the Right Audience</h3>
            </div>
            <p>Pinpoint your ideal customer and craft messaging that resonates.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        """
        <div class="benefit">
            <div class="benefit-container">
                <span class="benefit-icon">💡</span> 
                <h3>Crystallize Your Message</h3>
            </div>
            <p>Ensure your brief's objectives are clear, concise, and impactful.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        """
        <div class="benefit">
            <div class="benefit-container">
                <span class="benefit-icon">🚀</span> 
                <h3>Maximize Campaign Impact</h3>
            </div>
            <p>Get data-driven insights to optimize your strategies and drive results.</p>
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
            df_results, overall_score = analyze_text(document_text)

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

            # --- Rewrite Button ---
            st.markdown("<br>", unsafe_allow_html=True) # Add some spacing
            if st.button("✨ Improve My Brief"):
                with st.spinner("Rewriting your brief..."):
                    rewritten_brief = rewrite_brief(document_text, df_results)

                st.success("Your improved brief is ready!")
                st.text_area("Improved Brief", value=rewritten_brief, height=300)

                # --- Download Button (Word DOCX) ---
                doc = docx.Document()
                doc.add_paragraph(rewritten_brief)
                doc_bytes = io.BytesIO()
                doc.save(doc_bytes)
                doc_bytes.seek(0)

                st.download_button(
                    label="Download Improved Brief (DOCX)",
                    data=doc_bytes,
                    file_name="improved_brief.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )

            # Detailed Breakdown
            st.markdown("---")
            st.header("Detailed Analysis & Feedback")
            st.dataframe(df_results.style.format({"Score": "{:.0f}"}).set_properties(**{'text-align': 'left'}), use_container_width=True) # Left align text
            # Areas for Improvement (using accordions)
            st.markdown("---")
            st.header("Actionable Insights")
            improvement_areas = parse_and_improve(df_results, overall_score)
            for category, details in improvement_areas.items():
                with st.expander(f"**{category}**"):  
                    st.markdown("""
                    <style>
                        .suggestion-text {
                            font-size: 16px; /* Adjust font size as needed */
                        }
                    </style>
                    """, unsafe_allow_html=True)
                    st.markdown("<p class='suggestion-text'><strong>Suggestions:</strong></p>", unsafe_allow_html=True)
                    for suggestion in details["Suggestions"]:
                        st.write(f"- {suggestion}")
                    st.markdown("<p class='suggestion-text'><strong>Examples:</strong></p>", unsafe_allow_html=True)
                    for example in details["Examples"]:
                        st.write(f"- {example}")

        else:
            st.error("Error analyzing the text. Please try again.")

    except Exception as e:
        st.error(f"An error occurred: {e}")


