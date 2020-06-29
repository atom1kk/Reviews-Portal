from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from PIL import Image
from taggit.managers import TaggableManager

class PublishedManager(models.Manager):
	def get_queryset(self):
		return super().get_queryset().filter(status='published')

class CommentedManager(models.Manager):
	def get_queryset(self):
		return super().get_queryset().filter(status='active')

class Category(models.Model):
	title = models.CharField(max_length=200, db_index=True)
	slug = models.SlugField(max_length=200, unique=True)

	class Mate:
		ordering = ('title',)
		verbose_name = 'category'
		verbose_name_pliral = 'caregories'

	def __str__(self):
		return self.title 

class Post(models.Model):
	STATUS_CHOICES = (
		('draft', 'Draft'),
		('published', 'Published'),
	)
	category = models.ForeignKey(Category, related_name='posts', on_delete=models.CASCADE)
	title = models.CharField(max_length=250)   # заголовок статьи 
	slug = models.SlugField(max_length=250, unique_for_date='publish')   # формирования URL-ов в виде букв и цифр для улучшения распознавания поисковой системой
	image = models.ImageField(upload_to='blog/posts_images/', blank=True)
	author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')   # автор публикации
	body = models.TextField()   # сама статья 
	publish = models.DateTimeField(default=timezone.now)   # время когда опубликовано
	created = models.DateTimeField(auto_now_add=True)   # время создания
	updated = models.DateTimeField(auto_now=True)   # время редактирования  
	status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')  # статус блога (например "опубликовано")
	objects = models.Manager()  # Менеджер по умолчанию
	published = PublishedManager()  # Новый менеджер
	tags = TaggableManager()

	class Meta:
		ordering = ('-publish',)  # сортировка статей по дате публикация (по убыванию)

	def __str__(self):
		return self.title

	def get_absolute_url(self):
		return reverse('blog:post_detail', args=[self.publish.year, self.publish.month, self.publish.day, self.slug])

class Comment(models.Model):
	STATUS_CHOICES = (
		('created', 'Created'),
		('active', 'Active'),
	)
	post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')  # делаем отношение "один ко многим", что бы в статье можно было оставлять несколько комментариев
	name = models.CharField(max_length=80)
	email = models.EmailField()
	title = models.CharField(max_length=50)
	body = models.TextField()
	image = models.ImageField(upload_to='comments/images/', blank=True)
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)
	status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
	active = models.BooleanField(default=True)  # Добавляем булевое поле, что бы можно было скрывать определенные комментарии
	commented = CommentedManager()

	class Meta:
		ordering = ('created',)

	def __str__(self):
		return 'Comment by {} on {}'.format(self.name, self.post)





