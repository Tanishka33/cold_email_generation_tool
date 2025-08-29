import os
from app.chains import Chain
from app.portfolio import Portfolio

def test_email_generation():
    # Initialize the chain and portfolio
    chain = Chain()
    portfolio = Portfolio(file_path="app/resource/my_portfolio.csv")
    portfolio.load_portfolio()
    
    # Sample job data (mocked from the provided URL)
    job = {
        'role': 'Data Analyst Intern',
        'experience': '0-1 years',
        'skills': ['Python', 'SQL', 'Data Analysis', 'Machine Learning'],
        'description': '''We are looking for a Data Analyst Intern to join our team. 
        The ideal candidate should have strong analytical skills and experience with Python and SQL.'''
    }
    
    # User profile
    user_profile = {
        'name': 'Tanushka Borade',
        'email': 'tanushka.b@example.com',
        'phone': '+91-9876543210',
        'job_title': 'Student',
        'company': 'B.Tech CSE, 2026 (Expected)',
        'employment_type': 'Internship',
        'work_mode': 'Hybrid',
        'skills': '\n- Python\n- SQL\n- Data Analysis\n- Machine Learning',
        'projects': 'Built a potato leaf disease detection model using computer vision',
        'education': 'B.Tech in Computer Science and Engineering (Expected 2026)',
        'certifications': 'None',
        'additional_info': 'Published article on AI in healthcare',
        'instruction': 'Please highlight my academic projects and internship experience',
        'location': 'Mumbai, India',
        'institution': 'University of Mumbai'
    }
    
    # Generate email
    try:
        email = chain.write_mail(
            job=job,
            links=[],
            **user_profile
        )
        
        print("\n" + "="*80)
        print("GENERATED EMAIL:")
        print("="*80)
        print(email)
        print("="*80 + "\n")
        
        # Save to file for review
        with open('generated_email.txt', 'w', encoding='utf-8') as f:
            f.write(email)
            
        print("Email has been saved to 'generated_email.txt'")
        
    except Exception as e:
        print(f"Error generating email: {str(e)}")
        raise

if __name__ == "__main__":
    test_email_generation()
