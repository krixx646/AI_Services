"""
Management command to add more AI and tech SEO keywords (2025 trending).
Run with: python manage.py populate_ai_tech_keywords
"""
from django.core.management.base import BaseCommand
from blog.models import Tag, Category


class Command(BaseCommand):
    help = 'Populates AI and tech trending keywords for 2025 SEO optimization'

    def handle(self, *args, **options):
        # Additional AI & Tech Tags (Based on 2025 trends)
        ai_tech_tags = [
            # Core AI Technologies (High Search Volume 2025)
            "artificial intelligence",  # Already exists but verify
            "machine learning",
            "deep learning",
            "neural networks",
            "large language models",
            "LLMs",
            "GPT models",
            "Claude AI",
            "Gemini AI",
            "OpenAI",
            
            # AI Applications (Trending 2025)
            "natural language processing",
            "NLP",
            "computer vision",
            "AI image generation",
            "text to image AI",
            "AI video generation",
            "AI automation",
            "AI agents",
            "autonomous AI",
            "multimodal AI",
            
            # AI Tools & Platforms (Hot Keywords)
            "ChatGPT",
            "Claude",
            "Gemini",
            "Copilot AI",
            "AI writing tools",
            "AI coding assistant",
            "AI research tools",
            "AI productivity tools",
            "AI learning platforms",
            "AI study assistant",  # Already exists
            
            # AI in Education (Your Niche!)
            "AI in education",
            "AI tutoring",
            "AI for learning",
            "educational AI",
            "AI homework helper",
            "AI exam prep",
            "AI flashcards",
            "AI note-taking",
            "AI study planner",
            "adaptive AI learning",
            
            # AI Ethics & Responsibility (Trending)
            "AI ethics",
            "responsible AI",
            "AI bias",
            "AI transparency",
            "AI safety",
            "AI regulations",
            "AI governance",
            "ethical AI",
            "trustworthy AI",
            "AI fairness",
            
            # AI in Industries (Business Keywords)
            "AI in healthcare",
            "AI in finance",
            "AI in marketing",
            "AI in education",  # Duplicate check
            "AI in business",
            "AI in customer service",
            "AI in HR",
            "AI in legal",
            "AI in research",
            "AI in journalism",
            
            # Emerging AI Trends 2025
            "generative AI",  # Already exists
            "AGI",
            "artificial general intelligence",
            "prompt engineering",
            "AI fine-tuning",
            "RAG (Retrieval Augmented Generation)",
            "vector databases",
            "AI embeddings",
            "zero-shot learning",
            "few-shot learning",
            
            # AI SEO & Content
            "AI SEO",
            "AI content creation",
            "AI copywriting",
            "AI content optimization",
            "AI keyword research",
            "AI meta descriptions",
            "AI blog writing",
            "AI article generator",
            "SEO AI tools",
            "AI SEO strategy",
            
            # Tech & Development
            "Python for AI",
            "TensorFlow",
            "PyTorch",
            "Hugging Face",
            "AI APIs",
            "OpenAI API",
            "AI development",
            "AI programming",
            "AI frameworks",
            "AI libraries",
            
            # Student-Focused AI
            "AI for students",  # Already exists
            "student AI tools",
            "AI study buddy",
            "AI learning assistant",
            "AI homework AI",
            "AI essay helper",
            "AI research assistant",
            "AI citation generator",
            "AI summarizer",
            "AI paraphraser",
            
            # Conversational AI
            "AI chatbot",  # Already exists
            "chatbot technology",
            "conversational AI",
            "voice AI",
            "AI virtual assistant",
            "AI customer support",
            "chatbot development",
            "AI messaging",
            "AI dialogue systems",
            "context-aware AI",
            
            # AI Startups & Business
            "AI startups",
            "AI entrepreneurship",
            "AI business model",
            "AI monetization",
            "AI SaaS",
            "AI market trends",
            "AI investment",
            "AI unicorns",
            "AI innovation",
            "AI disruption",
            
            # AI Trends & Future
            "AI trends 2025",
            "future of AI",
            "AI predictions",
            "AI advancements",
            "next-gen AI",
            "AI breakthroughs",
            "AI evolution",
            "AI transformation",
            "AI revolution",
            "emerging AI",
        ]
        
        # Categories for better organization
        categories = [
            # Main Categories
            "AI & Technology",
            "Education & Learning",
            "Study Tips",
            "Exam Preparation",
            "Student Resources",
            "Productivity",
            "Nigerian Education",
            "University Life",
            "Career Development",
            "Tech Tutorials",
            
            # Specific AI Categories
            "Machine Learning",
            "Natural Language Processing",
            "AI Tools & Platforms",
            "AI Ethics",
            "AI in Education",
            "Generative AI",
            "AI Trends",
            "AI for Students",
            "Chatbot Technology",
            "AI Development",
            
            # Educational Categories
            "JAMB Preparation",
            "WAEC Study Tips",
            "University Entrance",
            "Academic Excellence",
            "Study Strategies",
            "Time Management",
            "Note-Taking",
            "Research Methods",
            "Online Learning",
            "EdTech",
        ]
        
        # Create/Update Tags
        created_tags = 0
        skipped_tags = 0
        
        self.stdout.write(self.style.SUCCESS('\n🤖 CREATING AI & TECH SEO KEYWORDS...\n'))
        
        for tag_name in ai_tech_tags:
            tag, created = Tag.objects.get_or_create(name=tag_name)
            if created:
                created_tags += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Created tag: "{tag_name}"'))
            else:
                skipped_tags += 1
                self.stdout.write(self.style.WARNING(f'- Skipped (exists): "{tag_name}"'))
        
        # Create Categories
        self.stdout.write(self.style.SUCCESS('\n\n📂 CREATING CATEGORIES...\n'))
        
        created_cats = 0
        skipped_cats = 0
        
        for cat_name in categories:
            cat, created = Category.objects.get_or_create(name=cat_name)
            if created:
                created_cats += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Created category: "{cat_name}"'))
            else:
                skipped_cats += 1
                self.stdout.write(self.style.WARNING(f'- Skipped (exists): "{cat_name}"'))
        
        # Summary
        self.stdout.write(self.style.SUCCESS(f'\n\n✅ DONE!'))
        self.stdout.write(self.style.SUCCESS(f'\n📊 TAGS: Created {created_tags} new, skipped {skipped_tags} existing'))
        self.stdout.write(self.style.SUCCESS(f'📂 CATEGORIES: Created {created_cats} new, skipped {skipped_cats} existing'))
        self.stdout.write(self.style.SUCCESS(f'\n📈 Total tags in database: {Tag.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'📁 Total categories in database: {Category.objects.count()}'))
        self.stdout.write(self.style.SUCCESS('\n💡 TIP: Use these trending 2025 keywords for maximum SEO impact!'))

