import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from dotenv import load_dotenv

load_dotenv()

class Chain:
    def __init__(self):
        self.llm = ChatGroq(
            temperature=0, 
            groq_api_key=os.getenv("GROQ_API_KEY"), 
            model_name="llama-3.3-70b-versatile"
        )

    def extract_jobs(self, cleaned_text):
        prompt_extract = PromptTemplate.from_template(
            """
            ### SCRAPED TEXT FROM WEBSITE:
            {page_data}
            ### INSTRUCTION:
            The scraped text is from the career's page of a website.
            Your job is to extract the job postings and return them in JSON format containing the following keys: 
            `role`, `experience`, `skills` and `description`.
            Only return the valid JSON.
            ### VALID JSON (NO PREAMBLE):
            """
        )
        chain_extract = prompt_extract | self.llm
        res = chain_extract.invoke(input={"page_data": cleaned_text})
        try:
            json_parser = JsonOutputParser()
            res = json_parser.parse(res.content)
        except OutputParserException:
            raise OutputParserException("Context too big. Unable to parse jobs.")
        return res if isinstance(res, list) else [res]

    def write_mail(self, job, links, name, email, instruction, **kwargs):
        # Prepare the job description
        job_description = f"""
        Role: {job.get('role', 'Not specified')}
        Experience: {job.get('experience', 'Not specified')}
        Required Skills: {', '.join(job.get('skills', ['Not specified']))}
        
        Job Description:
        {job.get('description', 'No description available')}
        """

        # Build the signature dynamically to avoid f-string issues
        signature_parts = [f"Best regards,\n{name}"]
        
        job_title = kwargs.get("job_title", "")
        if job_title and job_title != 'Not specified':
            signature_parts.append(job_title)
            
        company = kwargs.get('company', '')
        institution = kwargs.get('institution', '')
        
        if company and company != 'Not specified':
            signature_parts.append(company)
        elif institution and institution != 'Not specified':
            signature_parts.append(institution)
            
        contact_info = []
        if email and email != 'Not specified':
            contact_info.append(f"Email: {email}")
            
        phone_num = kwargs.get('phone', '')
        if phone_num and phone_num != 'Not specified':
            contact_info.append(f"Phone: {phone_num}")
            
        location = kwargs.get('location', '')
        if location and location != 'Not specified':
            contact_info.append(f"Location: {location}")
            
        linkedin = kwargs.get('linkedin', '')
        if linkedin and linkedin != 'Not specified':
            contact_info.append(f"LinkedIn: {linkedin}")
            
        portfolio = kwargs.get('portfolio', '')
        if portfolio and portfolio != 'Not specified':
            contact_info.append(f"Portfolio: {portfolio}")
            
        signature = '\n'.join(signature_parts + [''] + contact_info)
        
        # Unified prompt template for all applicants
        prompt_template = f"""
        ### JOB DESCRIPTION:
        {{job_description}}

        ### APPLICANT PROFILE:
        - Name: {name}
        - Current Position: {{job_title}}
        - Company: {{company}}
        - Email: {email}
        - Phone: {phone_num}
        - Location: {location}
        - Employment Type: {{employment_type}}
        - Work Mode: {{work_mode}}
        - Skills: {{skills}}
        - Education: {{education}}
        - Certifications: {{certifications}}
        - Projects: {{projects}}
        - Additional Information: {{additional_info}}
        
        ### INSTRUCTIONS:
        Create a professional and personalized cold email that highlights the applicant's qualifications and matches them with the job requirements.
        
        IMPORTANT GUIDELINES:
        1. Use ALL the information provided in the APPLICANT PROFILE section.
        2. Structure the email with clear paragraphs and proper formatting.
        3. For students: Emphasize education, projects, and relevant coursework.
        4. For professionals: Highlight relevant work experience and achievements.
        5. Include specific examples from the applicant's projects and skills.
        6. Keep the tone professional yet engaging.
        7. Maintain a length of 200-300 words.
        8. Use the exact information provided - no placeholders or made-up details.
        
        ### EMAIL STRUCTURE:
        Subject: Application for {{job_title}} Position - {name}
        
        Dear [Hiring Manager's Name or "Hiring Team"],
        
        [Opening Paragraph]
        - Introduce yourself with your full name
        - Mention the specific position you're applying for
        - State your current status (e.g., "As a [current role/student] at [institution/company]")
        - Express your enthusiasm for the opportunity
        
        [Body Paragraphs - 1-2 paragraphs]
        - Explain why you're interested in this specific position/company
        - Highlight 2-3 key skills/experiences that make you a strong candidate
        - Reference specific projects or achievements that demonstrate your qualifications
        - Mention any relevant education or certifications
        - Connect your background to the job requirements
        
        [Closing Paragraph]
        - Reiterate your interest in the position
        - Express your eagerness to discuss your application further
        - Thank them for their time and consideration
        
        {signature}
        """
        
        # Prepare all variables in one dictionary
        all_vars = {
            # From job
            "job_description": job_description,
            "job_title": job.get('role', 'the position'),
            "link_list": '\n'.join([f"- {link}" for link in links]) if links else "No relevant portfolio links found.",
            
            # From form
            "name": name,
            "email": email,
            "phone": phone_num,
            "location": location,
            "company": company,
            "institution": institution,
            "employment_type": kwargs.get("employment_type", "Not specified"),
            "work_mode": kwargs.get("work_mode", "Not specified"),
            "skills": kwargs.get("skills", "Not specified"),
            "projects": kwargs.get("projects", "No projects specified"),
            "education": kwargs.get("education", "Not specified"),
            "certifications": kwargs.get("certifications", "None"),
            "additional_info": kwargs.get("additional_info", "None"),
            "instruction": instruction
        }
        
        
        # Format the prompt with all variables
        prompt = prompt_template.format(**all_vars)
        
        # Generate the email
        chain = PromptTemplate(
            input_variables=[],
            template=prompt
        ) | self.llm
        
        try:
            response = chain.invoke({})
            email_content = response.content.strip()
            
            # Clean up the generated content
            email_content = email_content.replace('Best regards,', '').strip()
            email_content = email_content.replace('Sincerely,', '').strip()
            
            # Get job title and company from the job details or use defaults
            position = kwargs.get('job_title', job.get('role', 'Professional'))
            company_name = kwargs.get('company', '')
            
            # Create a clean signature
            signature = f"""

Best regards,
{name}
{position}{' at ' + company_name if company_name else ''}
Phone: {kwargs.get('phone', '')}
Email: {email}
"""
            # Only add the signature if it's not already in the email
            if 'best regards' not in email_content.lower() and 'sincerely' not in email_content.lower():
                return email_content + signature
            return email_content
            
        except Exception as e:
            return f"Error generating email: {str(e)}"


if __name__ == "__main__":
    print(os.getenv("GROQ_API_KEY"))
