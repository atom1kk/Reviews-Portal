from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from PIL import Image
from taggit.managers import TaggableManager
from django.db.models import Count
from django.core.validators import MaxValueValidator, MinValueValidator
import numpy as np
from django.db.models import Avg

DEFAULT_CHOICES = (
	('5', 'Отлично'),
	('4', 'Хорошо'),
	('3', 'Нормально'),
	('2', 'Плохо'),
	('1', 'Ужасно'),
)

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
		verbose_title = 'category'
		verbose_title_plural = 'categories'

	def get_absolute_url(self):
		return reverse('blog:post_list_by_category', args=[self.slug]) 



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
	average_rating = models.FloatField(verbose_name=('Average rating'), default=0,)
	objects = models.Manager()  # Менеджер по умолчанию
	published = PublishedManager()  # Новый менеджер
	tags = TaggableManager()

	class Meta:
		ordering = ('-publish',)  # сортировка статей по дате публикация (по убыванию)

	def average_rating(self):
		all_ratings = list(map(lambda x: x.value, self.comments.all()))
		average = np.array(all_ratings).astype(np.float)
		return np.average(average)

	def __str__(self):
		return self.title

	def get_absolute_url(self):
		return reverse('blog:post_detail', args=[self.publish.year, self.publish.month, self.publish.day, self.slug])




class Comment(models.Model):
	STATUS_CHOICES = (
		('created', 'Created'),
		('active', 'Active'),
	)

	rating_choices = DEFAULT_CHOICES

	value = models.CharField(
		max_length=20, 
		verbose_name=('Оценка'), 
		choices=rating_choices,
		blank=True, null=True
	)

	post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')  # делаем отношение "один ко многим", что бы в статье можно было оставлять несколько комментариев
	name = models.CharField(max_length=80)
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
		return 'Comment by {} on {}'.format(self.name, self.value, self.post)

	def calculate_average_value():
    # Сумма оценок
	    sum_of_value = 0
	    # Количество оценок
	    count = 0
	    # Находим все оценки от 1 до 5
	    for value in range(6):
	        # Получаем объекты оценок
	        objs = Comment.objects.filter(rating_choices=value)
	        # складываем кол-во оценок
	        count += objs.count()
	        # складываем сумму оценок
	        sum_of_value += objs.count() * i
	    # возвращаем среднюю оценку или None, если не удалось посчитать оценку
	    if count > 0:
	        return sum_of_value / count
	    else:
	        return None



