"""
Management command to populate SEO-optimized tags for the blog.
Run with: python manage.py populate_seo_tags
"""
from django.core.management.base import BaseCommand
from blog.models import Tag


class Command(BaseCommand):
    help = 'Populates the database with SEO-optimized tags for educational AI content'

    def handle(self, *args, **options):
        # SEO-optimized tags based on 2025 trends for AI education, student learning, and tutoring
        seo_tags = [
            # AI & Technology (High Search Volume)
            "artificial intelligence",
            "AI education",
            "AI for students",
            "machine learning basics",
            "AI chatbot",
            "study AI assistant",
            "AI tutor",
            "generative AI",
            "ChatGPT for students",
            "AI study tools",
            
            # Education & Learning (Evergreen Keywords)
            "online learning",
            "study tips",
            "exam preparation",
            "academic success",
            "student productivity",
            "effective studying",
            "learning techniques",
            "study methods",
            "educational technology",
            "e-learning",
            
            # Student-Specific (Target Audience)
            "university students",
            "college tips",
            "student life",
            "undergraduate",
            "graduate students",
            "student resources",
            "academic help",
            "homework help",
            "assignment assistance",
            "course materials",
            
            # Study & Productivity
            "note-taking",
            "study schedule",
            "time management",
            "focus techniques",
            "productivity hacks",
            "exam success",
            "test preparation",
            "memorization techniques",
            "active learning",
            "study motivation",
            
            # Technology & Tools
            "educational apps",
            "study apps",
            "learning platforms",
            "digital learning",
            "online tutoring",
            "virtual study",
            "smart studying",
            "EdTech",
            "learning software",
            "study automation",
            
            # Subject Areas (Broad Appeal)
            "STEM education",
            "science learning",
            "math help",
            "engineering students",
            "computer science",
            "programming tutorial",
            "data science",
            "research methods",
            "academic writing",
            "critical thinking",
            
            # Nigeria-Specific (Local SEO)
            "Nigerian students",
            "university in Nigeria",
            "JAMB preparation",
            "WAEC study tips",
            "Nigerian education",
            "Naija students",
            "study in Nigeria",
            
            # Trending Topics (2025)
            "personalized learning",
            "adaptive learning",
            "AI personalization",
            "future of education",
            "smart education",
            "learning analytics",
            "education innovation",
            "digital transformation",
            "hybrid learning",
            "micro-learning",
            
            # Action-Oriented (High Intent)
            "how to study better",
            "pass exams",
            "improve grades",
            "learn faster",
            "study smarter",
            "ace your exams",
            "get better grades",
            "master any subject",
            "academic excellence",
            "top student tips",
            
            # Long-Tail Keywords (Less Competition)
            "AI powered study assistant",
            "custom AI chatbot for notes",
            "personalized study bot",
            "lecture notes to chatbot",
            "AI from course materials",
            "automated study helper",
            "intelligent study companion",
            "custom learning AI",
            "course-specific AI tutor",
            "AI study partner",
        ]
        
        created_count = 0
        skipped_count = 0
        
        for tag_name in seo_tags:
            tag, created = Tag.objects.get_or_create(name=tag_name)
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Created tag: "{tag_name}"'))
            else:
                skipped_count += 1
                self.stdout.write(self.style.WARNING(f'- Skipped (exists): "{tag_name}"'))
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ DONE! Created {created_count} new tags, skipped {skipped_count} existing tags.'))
        self.stdout.write(self.style.SUCCESS(f'📊 Total tags in database: {Tag.objects.count()}'))
        self.stdout.write(self.style.SUCCESS('\n💡 TIP: When creating blog posts, select 5-10 relevant tags for best SEO!'))

