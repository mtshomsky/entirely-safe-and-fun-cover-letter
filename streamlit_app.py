import os
from openai import OpenAI
import streamlit as st
import streamlit as st
import pyperclip
import json


# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
MODEL_NAME = "gpt-4o"
#MODEL_NAME = "o3-mini"


def validate_input(text, max_length=75000):
    """Validate input text length and content."""
    if not text or not text.strip():
        return False, "Input cannot be empty"
    if len(text) > max_length:
        return False, f"Input exceeds maximum length of {max_length} characters"
    return True, ""


def generate_cover_letter(
    job_description,
    resume,
    paragraph_count=3,
    tone="professional job seeker wants to convey enthusiasm for the next role and excited to match past experiences with future expectations",
    style="Normal"
):
    """Generate a cover letter using OpenAI API."""
    try:
        api_key = st.session_state.get("openai_api_key") or os.environ.get("OPENAI_API_KEY")
        client = OpenAI(api_key=api_key)

        if style == "T-Style":
            prompt = f"""
            Generate a T-style cover letter based on the following:

            Job Description:
            {job_description}

            Resume:
            {resume}

            Tone:
            {tone}

            Create a cover letter in two parts:
            1. A narrative section with exactly {paragraph_count} paragraphs that:
               - Matches the candidate's experience with job requirements
               - Uses the specified tone: {tone}
               - Shows enthusiasm for the position
               - Highlights relevant skills and experiences

            2. A "Requirements Match" section that:
               - Extracts 4-6 key requirements from the job description
               - Matches each requirement with relevant experience/skills from the resume
               - Formats as a two-column list with requirements on the left and matching qualifications on the right
               - Use exactly 20 spaces between the requirement and the matching qualification

            Format the Requirements Match section as:

            Requirements Match:
            [Requirement 1]                    [Matching Experience/Skill]
            [Requirement 2]                    [Matching Experience/Skill]
            etc.

            Keep the narrative section professional and well-structured with:
            - First paragraph: Introduction and position interest
            - Middle paragraph(s): Relevant experience and skills
            - Last paragraph: Closing statement and call to action
            """
        else:
            prompt = f"""
            Generate a professional cover letter based on the following:

            Job Description:
            {job_description}

            Resume:
            {resume}

            Tone:
            {tone}

            Create a compelling cover letter that:
            1. Matches the candidate's experience with job requirements
            2. Uses the specified tone: {tone}
            3. Contains exactly {paragraph_count} paragraphs
            4. Highlights relevant skills and experiences
            5. Shows enthusiasm for the position

            Important: The response MUST be exactly {paragraph_count} paragraphs long.
            Each paragraph should be well-structured and focused on a specific aspect:
            - First paragraph: Introduction and position interest
            - Middle paragraph(s): Relevant experience and skills
            - Last paragraph: Closing statement and call to action

            Response should be in clear paragraphs suitable for a formal letter.
            """

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{
                "role":
                    "system",
                "content":
                    "You are a professional cover letter writer with expertise in creating compelling job application letters."
            }, {
                "role": "user",
                "content": prompt
            }],
            temperature=0.7,
        )

        return True, response.choices[0].message.content
    except Exception as e:
        return False, f"Error generating cover letter: {str(e)}"


def analyze_resume(resume_text):
    """Analyze resume and provide recommendations using OpenAI API."""
    try:
        api_key = st.session_state.get("openai_api_key") or os.environ.get("OPENAI_API_KEY")
        client = OpenAI(api_key=api_key)

        prompt = f"""
        Analyze the following resume and provide actionable recommendations:

        Resume:
        {resume_text}

        Please provide a JSON response with the following structure:
        {{
            "strengths": [list of 3 key strengths],
            "improvements": [list of 3 specific areas for improvement],
            "ats_optimization": [list of 3 recommendations for ATS optimization],
            "skills_gaps": [list of 2-3 suggested skills to develop]
        }}

        Keep recommendations specific, actionable, and constructive.
        """

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{
                "role":
                    "system",
                "content":
                    "You are an expert resume reviewer with experience in HR and recruitment."
            }, {
                "role": "user",
                "content": prompt
            }],
            temperature=0.7,
            response_format={"type": "json_object"})

        return True, response.choices[0].message.content
    except Exception as e:
        return False, f"Error analyzing resume: {str(e)}"


def generate_improved_resume(resume_text, analysis_result):
    """Generate an improved version of the resume based on the analysis."""
    try:
        api_key = st.session_state.get("openai_api_key") or os.environ.get("OPENAI_API_KEY")
        client = OpenAI(api_key=api_key)

        prompt = f"""
        Original Resume:
        {resume_text}

        Analysis Results:
        {analysis_result}

        Please rewrite the resume incorporating the following improvements:
        1. Address the areas of improvement mentioned in the analysis
        2. Optimize for ATS as suggested
        3. Better highlight the key strengths identified
        4. Maintain the same basic structure but enhance the content
        5. Keep the length similar to the original

        The response should be the complete rewritten resume in a clean, professional format.
        Maintain standard resume sections (Summary, Experience, Education, Skills, etc.).
        """

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{
                "role":
                    "system",
                "content":
                    "You are an expert resume writer with experience in optimizing resumes for ATS systems and professional presentation."
            }, {
                "role": "user",
                "content": prompt
            }],
            temperature=0.7,
        )

        return True, response.choices[0].message.content
    except Exception as e:
        return False, f"Error generating improved resume: {str(e)}"


def init_session_state():
    """Initialize session state variables."""
    if 'generated_letter' not in st.session_state:
        st.session_state.generated_letter = ""
    if 'error_message' not in st.session_state:
        st.session_state.error_message = ""
    if 'edited_letter' not in st.session_state:
        st.session_state.edited_letter = ""
    if 'disclaimer_accepted' not in st.session_state:
        st.session_state.disclaimer_accepted = False
    if 'openai_api_key' not in st.session_state:
        st.session_state.openai_api_key = ""


def copy_to_clipboard():
    """Copy generated letter to clipboard."""
    try:
        # Use the edited version if it exists, otherwise use the generated version
        text_to_copy = st.session_state.edited_letter or st.session_state.generated_letter
        pyperclip.copy(text_to_copy)
        st.success("Cover letter copied to clipboard!")
    except Exception as e:
        st.error(f"Failed to copy to clipboard: {str(e)}")


def show_disclaimer():
    """Show the disclaimer modal and prompt for OpenAI API key."""
    import os
    if not st.session_state.disclaimer_accepted or not st.session_state.openai_api_key:
        disclaimer_container = st.empty()
        with disclaimer_container.container():
            st.warning("⚠️ Disclaimer")
            st.markdown("""
            **Important Notice:**

            Use at your own risk. Always carefully review any generated cover letters and resumes before using them. 
            By using this application, you acknowledge and consent to take full ownership and responsibility for any 
            generated materials.
            """)
            # Load API key from environment if available and not already set in session
            env_api_key = os.environ.get("OPENAI_API_KEY", "")
            if not st.session_state.openai_api_key and env_api_key:
                st.session_state.openai_api_key = env_api_key
            # Prompt for OpenAI API key
            st.markdown("""
            **OpenAI API Key Required**

            Please enter your OpenAI API key below. This key is only stored in your session and never sent to any server except OpenAI.
            """)
            api_key = st.text_input(
                "OpenAI API Key",
                type="password",
                value=st.session_state.openai_api_key,
                help="You can get your API key from https://platform.openai.com/account/api-keys"
            )
            if api_key:
                st.session_state.openai_api_key = api_key
            accept = st.button("I Accept")
            if accept and st.session_state.openai_api_key:
                st.session_state.disclaimer_accepted = True
                disclaimer_container.empty()
                return True
            if accept and not st.session_state.openai_api_key:
                st.error("Please enter your OpenAI API key to proceed.")
            return False
    return True


def main():
    st.set_page_config(page_title="AI Cover Letter Generator",
                       page_icon="📝",
                       layout="wide")

    init_session_state()

    # Show disclaimer and only proceed if accepted
    if not show_disclaimer():
        return

    st.title("📝 AI Cover Letter Generator")
    st.markdown("""
    MIT License, use at your own risk.  
    This site doesn't collect your data, but it connects to OpenAI's API and I really don't know what they do with it from there.
    Generate a professional cover letter tailored to your resume and the job description.
    Just paste in the details below and let AI do the work!
    """)

    # Input forms
    with st.form("input_form"):
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Job Description")
            job_description = st.text_area(
                "Paste the job description here",
                height=300,
                help="Copy and paste the complete job description",
                max_chars=75000)
            st.caption(f"Character count: {len(job_description)}/75000")

        with col2:
            st.subheader("Your Resume")
            resume = st.text_area("Paste your resume text here",
                                  height=300,
                                  help="Copy and paste your resume content",
                                  max_chars=75000)
            st.caption(f"Character count: {len(resume)}/75000")

        # Add the style selector
        st.subheader("Cover Letter Style")
        style = st.selectbox(
            "Choose the cover letter format",
            options=["Normal", "T-Style"],
            help="Normal: Traditional paragraph format\nT-Style: Includes a section matching job requirements with your skills"
        )

        # Add the tone configuration
        st.subheader("Cover Letter Tone")
        tone = st.text_area(
            "Describe the tone for your cover letter",
            value=
            "professional job seeker wants to convey enthusiasm for the next role and excited to match past experiences with future expectations",
            help=
            "Customize the tone of your cover letter. For example: 'confident and passionate about technology' or 'experienced professional emphasizing leadership skills'",
            height=100)

        # Add the paragraph count slider
        st.subheader("Cover Letter Length")
        paragraph_count = st.slider(
            "Number of paragraphs",
            min_value=1,
            max_value=10,
            value=3,
            help=
            "Adjust the length of your cover letter by selecting the number of paragraphs"
        )

        submit_button = st.form_submit_button("Generate Cover Letter")

    # Handle form submission
    if submit_button:
        # Validate inputs
        is_valid_job, job_error = validate_input(job_description)
        is_valid_resume, resume_error = validate_input(resume)

        if not is_valid_job:
            st.error(f"Job Description: {job_error}")
        elif not is_valid_resume:
            st.error(f"Resume: {resume_error}")
        else:
            with st.spinner("Generating your cover letter... Please wait"):
                success, result = generate_cover_letter(
                    job_description, resume, paragraph_count, tone, style)

                if success:
                    st.session_state.generated_letter = result
                    st.session_state.error_message = ""
                else:
                    st.session_state.error_message = result
                    st.session_state.generated_letter = ""

    # Display results
    if st.session_state.error_message:
        st.error(st.session_state.error_message)

    if st.session_state.generated_letter:
        st.subheader("Generated Cover Letter")
        # Replace st.write with st.text_area for editing capability
        edited_text = st.text_area("Edit your cover letter here:",
                                   value=st.session_state.generated_letter,
                                   height=400,
                                   key="cover_letter_editor")
        # Store the edited text in session state
        st.session_state.edited_letter = edited_text

        if st.button("Copy to Clipboard"):
            copy_to_clipboard()

        st.markdown("---")

        # Add Resume Analysis Section
        st.subheader("AI Resume Analysis")
        st.write("Limitations: Understand that the analysis is best-efforts and may not reflect an actual ATS or opinionated HR perspective.")

        if st.button("Analyze Resume"):
            with st.spinner("Analyzing your resume... Please wait"):
                success, result = analyze_resume(resume)
                if success:
                    try:
                        analysis = json.loads(result)

                        # Display Strengths
                        st.write("### 💪 Key Strengths")
                        for strength in analysis["strengths"]:
                            st.write(f"- {strength}")

                        # Display Areas for Improvement
                        st.write("### 🎯 Areas for Improvement")
                        for improvement in analysis["improvements"]:
                            st.write(f"- {improvement}")

                        # Display ATS Optimization Tips
                        st.write("### 🤖 ATS Optimization Tips")
                        for tip in analysis["ats_optimization"]:
                            st.write(f"- {tip}")

                        # Display Skills Development Suggestions
                        st.write("### 📚 Recommended Skills to Develop")
                        for skill in analysis["skills_gaps"]:
                            st.write(f"- {skill}")

                        # Generate and display improved resume
                        st.markdown("---")
                        st.write("### ✨ AI-Improved Resume")
                        st.subheader("This feature is experimental and does not always result in a better or accurate resume; use with extreme caution.")

                        with st.spinner(
                                "Generating improved resume version..."):
                            success_improved, improved_resume = generate_improved_resume(
                                resume, result)
                            if success_improved:
                                # Create tabs for original and improved versions
                                original_tab, improved_tab = st.tabs(
                                    ["Original Resume", "Improved Resume"])

                                with original_tab:
                                    st.text_area("Original Resume",
                                                 value=resume,
                                                 height=400,
                                                 disabled=True)

                                with improved_tab:
                                    improved_resume_edited = st.text_area(
                                        "Improved Resume (Editable)",
                                        value=improved_resume,
                                        height=400,
                                        help=
                                        "This is an AI-generated improvement of your resume. Feel free to edit and adjust as needed."
                                    )
                            else:
                                st.error(improved_resume)

                    except json.JSONDecodeError:
                        st.error("Error parsing resume analysis results")
                else:
                    st.error(result)

        st.markdown("---")
        st.markdown("""
        ### Remember:
        - Review and personalize the generated letter before sending
        - Ensure all company-specific details are accurate
        - Proofread for any potential improvements
        - Adjust formatting as needed for your submission
        """)


if __name__ == "__main__":
    main()        