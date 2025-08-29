import streamlit as st
from langchain_community.document_loaders import WebBaseLoader

from chains import Chain
from portfolio import Portfolio
from utils import clean_text


def create_streamlit_app(llm, portfolio, clean_text):
    st.title("Cold Email Generator")
    
    # Create a form for better organization
    with st.form("email_form"):
        st.subheader("Job Details")
        url_input = st.text_input("Job Posting URL", 
                                placeholder="https://example.com/job-posting",
                                help="Paste the URL of the job posting you want to apply for")
        
        st.subheader("Your Information")
        
        # Basic Information
        with st.expander("Basic Information", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                your_name = st.text_input("Full Name*", placeholder="John Doe")
                your_email = st.text_input("Email Address*", placeholder="your.email@example.com")
            with col2:
                phone = st.text_input("Phone Number", placeholder="+1 (123) 456-7890")
                location = st.text_input("Location", placeholder="City, Country")
        
        # Professional Experience
        with st.expander("Professional Experience", expanded=True):
            st.subheader("Current/Most Recent Position")
            col1, col2 = st.columns(2)
            with col1:
                job_title = st.text_input("Job Title*", placeholder="e.g., Software Engineer")
                company = st.text_input("Company/Institution*", placeholder="Company/University Name")
            with col2:
                employment_type = st.selectbox("Employment Type", ["Full-time", "Part-time", "Contract", "Freelance", "Internship", "Student"])
                work_mode = st.selectbox("Work Mode", ["On-site", "Hybrid", "Remote"])
            
            st.text_area("Responsibilities & Achievements", 
                       placeholder="- Describe your key responsibilities\n- Highlight your achievements with metrics when possible\n- Mention any leadership roles or special projects",
                       height=100)
        
        # Technical Skills
        with st.expander("Technical Skills", expanded=True):
            st.subheader("Technical Skills & Tools")
            skills = st.text_area("List your technical skills*",
                               placeholder="- Programming Languages: Python, JavaScript, Java\n- Frameworks: React, Node.js, Django\n- Tools & Technologies: Git, Docker, AWS, SQL\n- Any other relevant technical skills",
                               height=100,
                               key="skills")
        
        # Projects
        with st.expander("Projects", expanded=True):
            st.subheader("Relevant Projects")
            projects = st.text_area("Describe 1-3 relevant projects*",
                                 placeholder="Project 1: [Project Name]\n- Technologies used: [List technologies]\n- Your role: [Your contribution]\n- Outcome: [Results/impact]\n\nProject 2: [Project Name]\n- Technologies used: [List technologies]\n- Your role: [Your contribution]\n- Outcome: [Results/impact]",
                                 height=150,
                                 key="projects")
        
        # Additional Information
        with st.expander("Additional Information", expanded=True):
            st.subheader("Education")
            col1, col2 = st.columns(2)
            with col1:
                degree = st.text_input("Degree/Qualification", placeholder="e.g., B.Tech in Computer Science")
            with col2:
                institution = st.text_input("Institution", placeholder="University/School Name")
            
            st.subheader("Certifications (if any)")
            certifications = st.text_area("List any relevant certifications",
                                      placeholder="- [Certification Name], [Issuing Organization], [Year]\n- [Certification Name], [Issuing Organization], [Year]",
                                      height=80,
                                      key="certifications")
            
            st.subheader("Online Presence")
            col1, col2 = st.columns(2)
            with col1:
                linkedin = st.text_input("LinkedIn Profile (optional)", 
                                      placeholder="https://linkedin.com/in/yourprofile",
                                      key="linkedin")
            with col2:
                portfolio = st.text_input("Portfolio/Website (optional)",
                                       placeholder="https://yourportfolio.com",
                                       key="portfolio")
            
            st.subheader("Other Information")
            additional_info = st.text_area("Anything else you'd like to include",
                                       placeholder="- Languages you speak\n- Volunteer experience\n- Hobbies or interests relevant to the role",
                                       height=80,
                                       key="additional_info")
        
        # Email Customization
        st.subheader("Email Customization")
        
        # Email Customization
        st.subheader("Email Customization")
        with st.expander("Customize Your Email", expanded=True):
            instruction = st.text_area("Additional Instructions", 
                                     placeholder="Any specific points you'd like to include in your email?",
                                     height=100,
                                     help="Mention any specific requirements or points you want to highlight in the email.")
        
        submit_button = st.form_submit_button("Generate Cold Email")

    if submit_button and url_input:
        # Validate required fields
        required_fields = [your_name, your_email, job_title, company]
        error_message = None
        
        if not all(required_fields):
            error_message = "Please fill in all required fields (marked with *)."
        
        if error_message:
            st.warning(error_message)
        else:
            try:
                with st.spinner("Analyzing job posting and generating email..."):
                    # Load and process the job posting
                    loader = WebBaseLoader([url_input])
                    data = clean_text(loader.load().pop().page_content)
                    
                    # Initialize and load portfolio if it's not already loaded
                    if isinstance(portfolio, str):
                        portfolio = Portfolio()
                    portfolio.load_portfolio()
                    
                    # Extract job details
                    jobs = llm.extract_jobs(data)
                    
                    # Prepare user profile with unified form data
                    user_profile = {
                        "name": your_name,
                        "email": your_email,
                        "phone": phone,
                        "location": location,
                        "job_title": job_title if job_title != "Student" else "Student" + (f" at {institution}" if institution else ""),
                        "company": company if company != "Student" else (institution if institution else "Student"),
                        "employment_type": employment_type,
                        "work_mode": work_mode,
                        "skills": skills,
                        "projects": projects,
                        "education": f"{degree} from {institution}" if degree or institution else "Currently pursuing education",
                        "certifications": certifications,
                        "additional_info": additional_info,
                        "instruction": instruction,
                        "linkedin": linkedin if 'linkedin' in locals() else "",
                        "portfolio": portfolio if 'portfolio' in locals() else "",
                        "institution": institution
                    }
                    
                    # Generate email for each job found
                    for job in jobs:
                        skills = job.get('skills', [])
                        links = portfolio.query_links(skills)
                        
                        # Generate email with user profile
                        email = llm.write_mail(job=job, links=links, **user_profile)
                        
                        # Display the generated email
                        st.subheader(f"Generated Email for {job.get('role', 'the position')}")
                        st.markdown("---")
                        st.markdown(email)
                        st.markdown("---")
                        
                        # Add a download button for the email
                        st.download_button(
                            label="📥 Download Email",
                            data=email,
                            file_name=f"cold_email_{job.get('role', 'position').lower().replace(' ', '_')}.txt",
                            mime="text/plain"
                        )
                        
            except Exception as e:
                st.error(f"An error occurred while processing your request: {str(e)}")
                st.error("Please check the URL and try again.")
    elif submit_button and not url_input:
        st.warning("Please enter a valid job posting URL.")


if __name__ == "__main__":
    st.set_page_config(
        layout="wide", 
        page_title="Cold Email Generator", 
        page_icon="📧",
        initial_sidebar_state="expanded"
    )
    
    # Add some custom CSS for better styling
    st.markdown("""
    <style>
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        .stTextArea textarea {
            min-height: 100px;
        }
    </style>
    """, unsafe_allow_html=True)
    
    chain = Chain()
    # Initialize portfolio with the correct path
    portfolio = Portfolio(file_path="app/resource/my_portfolio.csv")
    create_streamlit_app(chain, portfolio, clean_text)