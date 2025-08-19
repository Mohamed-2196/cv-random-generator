from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
import random
import json
import uuid
import io
from datetime import datetime, timedelta
from faker import Faker
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors

app = FastAPI(title="CV Generator API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CVGenerator:
    def __init__(self):
        self.fake = Faker()
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
        
    def setup_custom_styles(self):
        """Setup custom paragraph styles for the CV"""
        self.styles.add(ParagraphStyle(
            name='CVTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1,  # Center alignment
            textColor=colors.darkblue
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.darkblue,
            borderWidth=1,
            borderColor=colors.darkblue,
            borderPadding=5
        ))
        
        self.styles.add(ParagraphStyle(
            name='ContactInfo',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=1,  # Center alignment
            spaceAfter=20
        ))
        
    def generate_personal_info(self):
        """Generate random personal information"""
        return {
            'name': self.fake.name(),
            'email': self.fake.email(),
            'phone': self.fake.phone_number(),
            'address': f"{self.fake.street_address()}, {self.fake.city()}, {self.fake.state()} {self.fake.zipcode()}",
            'linkedin': f"linkedin.com/in/{self.fake.user_name()}",
            'summary': self.fake.text(max_nb_chars=300)
        }

    def generate_work_experience(self):
        """Generate random work experience"""
        positions = [
            'Software Engineer', 'Data Analyst', 'Product Manager', 'Marketing Specialist',
            'Sales Representative', 'HR Coordinator', 'Financial Analyst', 'Project Manager',
            'Operations Manager', 'Customer Success Manager', 'DevOps Engineer', 'UX Designer',
            'Business Analyst', 'Quality Assurance Engineer', 'Content Writer'
        ]
        
        companies = [
            'TechCorp Inc.', 'Global Solutions Ltd.', 'Innovation Labs', 'Digital Dynamics',
            'Future Systems', 'Smart Technologies', 'NextGen Solutions', 'Alpha Enterprises',
            'Beta Industries', 'Gamma Corporation', 'Delta Systems', 'Epsilon Group'
        ]
        
        experiences = []
        current_date = datetime.now()
        
        for i in range(random.randint(2, 5)):
            end_date = current_date - timedelta(days=random.randint(30, 365) * i)
            start_date = end_date - timedelta(days=random.randint(365, 1095))
            
            experience = {
                'position': random.choice(positions),
                'company': random.choice(companies),
                'start_date': start_date.strftime('%m/%Y'),
                'end_date': end_date.strftime('%m/%Y') if i > 0 else 'Present',
                'responsibilities': [
                    self.fake.sentence() for _ in range(random.randint(2, 4))
                ]
            }
            experiences.append(experience)
            
        return experiences

    def generate_education(self):
        """Generate random education background"""
        degrees = [
            'Bachelor of Science in Computer Science',
            'Bachelor of Arts in Business Administration',
            'Master of Business Administration',
            'Bachelor of Engineering',
            'Master of Science in Data Science',
            'Bachelor of Arts in Marketing',
            'Master of Science in Information Technology',
            'Bachelor of Science in Finance'
        ]
        
        universities = [
            'State University', 'Tech Institute', 'Business College', 'Engineering University',
            'Metropolitan University', 'City College', 'National Institute', 'Regional University'
        ]
        
        education = []
        for _ in range(random.randint(1, 3)):
            grad_year = random.randint(2010, 2023)
            edu = {
                'degree': random.choice(degrees),
                'institution': random.choice(universities),
                'year': str(grad_year),
                'gpa': round(random.uniform(3.0, 4.0), 2) if random.choice([True, False]) else None
            }
            education.append(edu)
            
        return education

    def generate_skills(self):
        """Generate random skills"""
        technical_skills = [
            'Python', 'Java', 'JavaScript', 'SQL', 'React', 'Node.js', 'AWS', 'Docker',
            'Kubernetes', 'Git', 'Linux', 'MongoDB', 'PostgreSQL', 'Redis', 'Elasticsearch'
        ]
        
        soft_skills = [
            'Leadership', 'Communication', 'Problem Solving', 'Team Collaboration',
            'Project Management', 'Time Management', 'Critical Thinking', 'Adaptability'
        ]
        
        return {
            'technical': random.sample(technical_skills, random.randint(5, 10)),
            'soft': random.sample(soft_skills, random.randint(3, 6))
        }

    def generate_certifications(self):
        """Generate random certifications"""
        certs = [
            'AWS Certified Solutions Architect',
            'Google Cloud Professional',
            'Microsoft Azure Fundamentals',
            'Certified Project Management Professional (PMP)',
            'Scrum Master Certification',
            'Six Sigma Green Belt',
            'CompTIA Security+',
            'Cisco Certified Network Associate (CCNA)'
        ]
        
        return random.sample(certs, random.randint(0, 3))

    def create_pdf(self, cv_data):
        """Create PDF from CV data and return as bytes"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter,
                              rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=18)
        
        story = []
        
        # Name and title
        story.append(Paragraph(cv_data['personal']['name'], self.styles['CVTitle']))
        
        # Contact information
        contact_info = f"""
        {cv_data['personal']['email']} | {cv_data['personal']['phone']}<br/>
        {cv_data['personal']['address']}<br/>
        {cv_data['personal']['linkedin']}
        """
        story.append(Paragraph(contact_info, self.styles['ContactInfo']))
        
        # Professional Summary
        story.append(Paragraph("PROFESSIONAL SUMMARY", self.styles['SectionHeader']))
        story.append(Paragraph(cv_data['personal']['summary'], self.styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Work Experience
        story.append(Paragraph("WORK EXPERIENCE", self.styles['SectionHeader']))
        for exp in cv_data['experience']:
            # Position and company
            exp_header = f"<b>{exp['position']}</b> - {exp['company']} ({exp['start_date']} - {exp['end_date']})"
            story.append(Paragraph(exp_header, self.styles['Normal']))
            
            # Responsibilities
            for resp in exp['responsibilities']:
                story.append(Paragraph(f"• {resp}", self.styles['Normal']))
            story.append(Spacer(1, 8))
        
        # Education
        story.append(Paragraph("EDUCATION", self.styles['SectionHeader']))
        for edu in cv_data['education']:
            edu_text = f"<b>{edu['degree']}</b><br/>{edu['institution']}, {edu['year']}"
            if edu['gpa']:
                edu_text += f" (GPA: {edu['gpa']})"
            story.append(Paragraph(edu_text, self.styles['Normal']))
            story.append(Spacer(1, 8))
        
        # Skills
        story.append(Paragraph("SKILLS", self.styles['SectionHeader']))
        story.append(Paragraph(f"<b>Technical:</b> {', '.join(cv_data['skills']['technical'])}", self.styles['Normal']))
        story.append(Paragraph(f"<b>Soft Skills:</b> {', '.join(cv_data['skills']['soft'])}", self.styles['Normal']))
        story.append(Spacer(1, 8))
        
        # Certifications
        if cv_data['certifications']:
            story.append(Paragraph("CERTIFICATIONS", self.styles['SectionHeader']))
            for cert in cv_data['certifications']:
                story.append(Paragraph(f"• {cert}", self.styles['Normal']))
        
        doc.build(story)
        buffer.seek(0)
        return buffer

cv_generator = CVGenerator()

class CVResponse(BaseModel):
    personal: dict
    experience: List[dict]
    education: List[dict]
    skills: dict
    certifications: List[str]

@app.get("/")
async def root():
    return {"message": "CV Generator API"}

@app.get("/generate-cv", response_model=CVResponse)
async def generate_random_cv():
    """Generate a random CV with realistic data using Faker"""
    
    cv_data = {
        'personal': cv_generator.generate_personal_info(),
        'experience': cv_generator.generate_work_experience(),
        'education': cv_generator.generate_education(),
        'skills': cv_generator.generate_skills(),
        'certifications': cv_generator.generate_certifications()
    }
    
    return CVResponse(**cv_data)

@app.get("/generate-multiple-cvs/{count}")
async def generate_multiple_cvs(count: int):
    """Generate multiple random CVs"""
    if count > 20:
        raise HTTPException(status_code=400, detail="Maximum 10 CVs can be generated at once")
    
    cvs = []
    for _ in range(count):
        cv_data = {
            'personal': cv_generator.generate_personal_info(),
            'experience': cv_generator.generate_work_experience(),
            'education': cv_generator.generate_education(),
            'skills': cv_generator.generate_skills(),
            'certifications': cv_generator.generate_certifications()
        }
        cvs.append(cv_data)
    
    return {"cvs": cvs, "count": len(cvs)}

@app.get("/download-cv-pdf")
async def download_single_cv_pdf():
    """Generate and download a single CV as PDF"""
    cv_data = {
        'personal': cv_generator.generate_personal_info(),
        'experience': cv_generator.generate_work_experience(),
        'education': cv_generator.generate_education(),
        'skills': cv_generator.generate_skills(),
        'certifications': cv_generator.generate_certifications()
    }
    
    pdf_buffer = cv_generator.create_pdf(cv_data)
    
    # Generate filename
    name = cv_data['personal']['name'].replace(' ', '_').replace(',', '')
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"CV_{name}_{timestamp}.pdf"
    
    return StreamingResponse(
        io.BytesIO(pdf_buffer.read()),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@app.get("/download-multiple-cvs-zip/{count}")
async def download_multiple_cvs_zip(count: int):
    """Generate and download multiple CVs as a ZIP file"""
    if count > 20:
        raise HTTPException(status_code=400, detail="Maximum 20 CVs can be generated at once")
    
    import zipfile
    
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for i in range(count):
            cv_data = {
                'personal': cv_generator.generate_personal_info(),
                'experience': cv_generator.generate_work_experience(),
                'education': cv_generator.generate_education(),
                'skills': cv_generator.generate_skills(),
                'certifications': cv_generator.generate_certifications()
            }
            
            pdf_buffer = cv_generator.create_pdf(cv_data)
            
            # Generate filename
            name = cv_data['personal']['name'].replace(' ', '_').replace(',', '')
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"CV_{name}_{timestamp}_{i+1:03d}.pdf"
            
            zip_file.writestr(filename, pdf_buffer.read())
    
    zip_buffer.seek(0)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"CVs_Batch_{timestamp}_{count}_files.zip"
    
    return StreamingResponse(
        io.BytesIO(zip_buffer.read()),
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={zip_filename}"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
