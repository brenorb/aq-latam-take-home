"""Question generation logic using templates."""
import random
from models.job import Job


class QuestionGenerator:
    """
    Generates role-grounded interview questions using templates.
    
    Questions are generated based on job title, department, and requirements.
    Uses a template-based approach for Phase 3 (simple, no external dependencies).
    """
    
    TEMPLATES = [
        "Why are you interested in this {job_title} position in {department}?",
        "Tell me about your experience with {first_requirement}.",
        "Describe a project where you demonstrated skills relevant to {job_title}.",
        "What challenges have you faced in {department}, and how did you overcome them?",
        "How do you stay current with {requirement} technologies?",
        "What experience do you have with {requirement}?",
        "Can you walk me through your approach to {first_requirement}?",
        "What motivates you to work in {department}?",
    ]
    
    def generate_initial_question(self, job: Job) -> str:
        """
        Generate the first question for an interview.
        
        Args:
            job: The job instance to generate question for
            
        Returns:
            Role-grounded interview question string
        """
        return self.generate_next_question(job, [], question_number=1)
    
    def generate_next_question(
        self,
        job: Job,
        conversation_history: list[dict],
        question_number: int
    ) -> str:
        """
        Generate the next question based on question number.
        
        Args:
            job: The job instance to generate question for
            conversation_history: List of previous Q/A pairs (not used in template approach)
            question_number: Current question number (1-indexed)
            
        Returns:
            Role-grounded interview question string
        """
        # Select template based on question number (cycle through templates)
        template_index = (question_number - 1) % len(self.TEMPLATES)
        template = self.TEMPLATES[template_index]
        
        # Extract job-specific values
        job_title = job.title
        department = job.department
        requirements = job.requirements
        first_requirement = requirements[0] if requirements else "this role"
        # Select a requirement (prefer first, but can use random for variety)
        if len(requirements) == 0:
            requirement = "this role"
        elif len(requirements) == 1:
            requirement = first_requirement
        else:
            requirement = random.choice(requirements)
        
        # Replace placeholders
        question = template.format(
            job_title=job_title,
            department=department,
            first_requirement=first_requirement,
            requirement=requirement
        )
        
        return question

