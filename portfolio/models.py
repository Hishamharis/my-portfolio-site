from django.db import models
from django.utils.text import slugify


class Project(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    image = models.ImageField(upload_to='projects/', blank=True, null=True)
    technologies = models.CharField(max_length=500, help_text="Comma-separated: Django, Python, React")
    github_url = models.URLField(blank=True)
    live_url = models.URLField(blank=True)
    featured = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_technologies_list(self):
        return [tech.strip() for tech in self.technologies.split(',')]


class Skill(models.Model):
    CATEGORY_CHOICES = [
        ('backend', 'Backend Development'),
        ('frontend', 'Frontend Development'),
        ('tools', 'Tools & Technologies'),
        ('additional', 'Additional Skills'),
    ]

    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    proficiency = models.IntegerField(help_text="0-100")
    icon = models.CharField(max_length=50, blank=True, help_text="Bootstrap icon class: bi-code-slash")
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['category', 'order']

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class ContactMessage(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    subject = models.CharField(max_length=300)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.subject}"


class SiteVisitor(models.Model):
    """Tracks every visit to the portfolio site."""
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    page = models.CharField(max_length=500, default='/')
    referrer = models.TextField(blank=True, default='')
    user_agent = models.TextField(blank=True, default='')
    visited_at = models.DateTimeField(auto_now_add=True)
    sent_contact = models.BooleanField(default=False)

    class Meta:
        ordering = ['-visited_at']

    def __str__(self):
        return f"{self.ip_address} — {self.page} — {self.visited_at.strftime('%d %b %Y %H:%M')}"


class SiteUpdate(models.Model):
    """
    One row per site update/version.
    Populated automatically by: python manage.py log_update
    """
    version       = models.CharField(max_length=60)
    summary       = models.TextField()
    changed_files = models.TextField(blank=True, default='')
    author        = models.CharField(max_length=200, blank=True, default='')
    machine_ip    = models.GenericIPAddressField(null=True, blank=True)
    deployed_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-deployed_at']

    def __str__(self):
        return f"{self.version} — {self.deployed_at.strftime('%d %b %Y %H:%M')}"


class LoginAttempt(models.Model):
    """
    Tracks every failed login to /admin-panel/.
    Used to auto-block an IP after too many wrong passwords.
    """
    ip_address = models.GenericIPAddressField()
    attempted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-attempted_at']

    def __str__(self):
        return f"{self.ip_address} — {self.attempted_at}"


class SiteSettings(models.Model):
    """Singleton model for site-wide settings"""
    site_title = models.CharField(max_length=200, default="Hisham Haris Portfolio")
    hero_title = models.CharField(max_length=200, default="Hi, I'm Hisham Haris")
    hero_subtitle = models.TextField(default="Full-Stack Developer")
    about_text = models.TextField(blank=True)
    profile_image = models.ImageField(upload_to='profile/', blank=True)
    github_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    email = models.EmailField(blank=True)
    resume_file = models.FileField(upload_to='resume/', blank=True)

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def __str__(self):
        return "Site Settings"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj