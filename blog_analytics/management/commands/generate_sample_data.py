"""
Django management command to generate sample data for testing analytics APIs.
"""
import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker

from blog_analytics.models import Country, User, Blog, BlogView


class Command(BaseCommand):
    help = 'Generate sample data for analytics testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--countries',
            type=int,
            default=10,
            help='Number of countries to create (default: 10)'
        )
        parser.add_argument(
            '--users',
            type=int,
            default=50,
            help='Number of users to create (default: 50)'
        )
        parser.add_argument(
            '--blogs',
            type=int,
            default=200,
            help='Number of blogs to create (default: 200)'
        )
        parser.add_argument(
            '--views',
            type=int,
            default=5000,
            help='Number of blog views to create (default: 5000)'
        )
        parser.add_argument(
            '--days',
            type=int,
            default=365,
            help='Number of days of historical data (default: 365)'
        )

    def handle(self, *args, **options):
        fake = Faker()
        
        num_countries = options['countries']
        num_users = options['users']
        num_blogs = options['blogs']
        num_views = options['views']
        num_days = options['days']
        
        self.stdout.write(self.style.WARNING('Clearing existing data...'))
        BlogView.objects.all().delete()
        Blog.objects.all().delete()
        User.objects.all().delete()
        Country.objects.all().delete()
        
        # Create countries
        self.stdout.write(self.style.SUCCESS(f'Creating {num_countries} countries...'))
        countries = []
        country_data = [
            ('United States', 'US'),
            ('United Kingdom', 'GB'),
            ('Canada', 'CA'),
            ('Germany', 'DE'),
            ('France', 'FR'),
            ('Japan', 'JP'),
            ('Australia', 'AU'),
            ('India', 'IN'),
            ('Brazil', 'BR'),
            ('South Korea', 'KR'),
            ('Spain', 'ES'),
            ('Italy', 'IT'),
            ('Netherlands', 'NL'),
            ('Sweden', 'SE'),
            ('Singapore', 'SG'),
        ]
        
        for i in range(min(num_countries, len(country_data))):
            name, code = country_data[i]
            country = Country.objects.create(name=name, code=code)
            countries.append(country)
        
        # Create users
        self.stdout.write(self.style.SUCCESS(f'Creating {num_users} users...'))
        users = []
        for i in range(num_users):
            user = User.objects.create_user(
                username=fake.user_name() + str(i),  # Ensure uniqueness
                email=fake.email(),
                password='password123',
                country=random.choice(countries),
                bio=fake.text(max_nb_chars=200),
                is_active=random.choice([True, True, True, False])  # 75% active
            )
            # Set random creation date
            days_ago = random.randint(0, num_days)
            user.created_at = timezone.now() - timedelta(days=days_ago)
            user.save()
            users.append(user)
        
        # Create blogs
        self.stdout.write(self.style.SUCCESS(f'Creating {num_blogs} blogs...'))
        blogs = []
        for i in range(num_blogs):
            author = random.choice(users)
            blog = Blog.objects.create(
                title=fake.sentence(nb_words=6),
                content=fake.text(max_nb_chars=1000),
                author=author,
                country=author.country,
                is_published=random.choice([True, True, True, False])  # 75% published
            )
            # Set random creation date (after user creation)
            max_days_ago = (timezone.now() - author.created_at).days
            if max_days_ago > 0:
                days_ago = random.randint(0, min(max_days_ago, num_days))
            else:
                days_ago = 0
            blog.created_at = timezone.now() - timedelta(days=days_ago)
            blog.save()
            blogs.append(blog)
        
        # Create blog views
        self.stdout.write(self.style.SUCCESS(f'Creating {num_views} blog views...'))
        for i in range(num_views):
            blog = random.choice(blogs)
            viewer = random.choice(users + [None, None])  # Some anonymous views
            
            # Views should be after blog creation
            max_days_ago = (timezone.now() - blog.created_at).days
            if max_days_ago > 0:
                days_ago = random.randint(0, min(max_days_ago, num_days))
            else:
                days_ago = 0
            
            view = BlogView.objects.create(
                blog=blog,
                viewer=viewer,
                country=viewer.country if viewer else random.choice(countries),
                ip_address=fake.ipv4()
            )
            view.viewed_at = timezone.now() - timedelta(
                days=days_ago,
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            view.save()
            
            # Progress indicator
            if (i + 1) % 1000 == 0:
                self.stdout.write(f'  Created {i + 1}/{num_views} views...')
        
        # Summary
        self.stdout.write(self.style.SUCCESS('\n' + '='*50))
        self.stdout.write(self.style.SUCCESS('Sample data generation complete!'))
        self.stdout.write(self.style.SUCCESS('='*50))
        self.stdout.write(f'Countries: {Country.objects.count()}')
        self.stdout.write(f'Users: {User.objects.count()}')
        self.stdout.write(f'Blogs: {Blog.objects.count()}')
        self.stdout.write(f'Blog Views: {BlogView.objects.count()}')
        self.stdout.write(self.style.SUCCESS('='*50))
        self.stdout.write(self.style.WARNING('\nYou can now test the analytics APIs:'))
        self.stdout.write('  /analytics/blog-views/?object_type=country&range=month')
        self.stdout.write('  /analytics/top/?top=user&range=year')
        self.stdout.write('  /analytics/performance/?compare=month')
