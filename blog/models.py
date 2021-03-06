from email import message
from ckeditor.fields import RichTextField
from django.conf import settings
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from taggit.managers import TaggableManager


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status='published')


class Post(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('rejected', 'Rejected'),
    )

    title = models.CharField(max_length=250)
    cover_image = models.ImageField(
        upload_to="static/img/post_cover_images", null=True)
    slug = models.SlugField(
        max_length=250, unique_for_date='publish', blank=True, null=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='blog_posts')
    body = RichTextField()
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    # Admin usauge
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='draft')
    featured = models.BooleanField(default=False, blank=True, null=True)

    objects = models.Manager()  # The default manager eg. Post.objects.all()
    published = PublishedManager()  # Our custom manager eg. Post.published.all()

    tags = TaggableManager()

    class Meta:
        ordering = ('-publish',)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:post_detail', args=[
            self.publish.year,
            self.publish.month,
            self.publish.day,
            self.slug
        ])


@receiver(pre_save, sender=Post)
def blog_post_pre_save(sender, instance, *args, **kwargs):
    instance.slug = slugify(instance.title)


class Comment(models.Model):

    # Sorry i know this comment is too long but i wrote it for someone, please ignore.
    """ The related_name attribute allows you to name the attribute that you use for
    the relationship from the related object back to this one. After defining this, you
    can retrieve the post of a comment object using comment.post and retrieve all
    comments of a post using post.comments.all(). If you don't define the related_
    name attribute, Django will use the name of the model in lowercase, followed by _
    set (that is, comment_set )"""
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='comment')
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return f'Comment by {self.name} on {self.post}'


class ContactUs(models.Model):
    REASON_CHOICES = (
        ('inquiry', 'Inquiry'),
        ('report', 'Report'),
        ('job', 'Job'),
    )
    name = models.CharField(max_length=150)
    email = models.EmailField()
    message = models.TextField()
    telephone = models.IntegerField()
    reason = models.CharField(
        max_length=10, choices=REASON_CHOICES)
    
    class Meta:
        verbose_name = 'Contact Us'
        verbose_name_plural = 'Contact Us'
