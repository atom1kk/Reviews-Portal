from django.shortcuts import render, get_object_or_404
from .models import Post, Comment, Category
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from django.core.mail import send_mail
from .forms import EmailPostForm, CommentForm, SearchForm
from PIL import Image
from taggit.models import Tag
from django.db.models import Count  # функция агрегации Count позволяет выполнить агрегирующий запрос для подсчета кол-ва тегов на уровне базы данных
from django.contrib.postgres.search import SearchVector

class PostListView(ListView):
	queryset = Post.published.all()
	context_object_name = 'posts'
	paginate_by = 10
	template_name = 'blog/post/list.html'

def post_list(request, tag_slug=None, category_slug=None):
	object_list = Post.published.all()  # запрашиваем все опубликованные статьи с помощью менеджера published
	tag = None
	category = None
	categories = Category.objects.all()

	if category_slug:
		category = get_object_or_404(Category, slug=category_slug)
		posts = posts.filter(category=category)

	if tag_slug:
		tag = get_object_or_404(Tag, slug=tag_slug)  
		object_list = object_list.filter(tags__in=[tag])  # фильтруем статьи с определенным тегом

	paginator = Paginator(object_list, 10)  # по 3 статьи на страницу
	page = request.GET.get('page')

	try:
		posts = paginator.page(page)
	except PageNotAnInteger:
		# Если страница не является целым числом, возвращаем первую страницу
		posts = paginator.page(1)
	except EmptyPage:
		# Если номер страницы больше, чем кол-во страниц, возвращаем последнюю
		posts = paginator.page(paginator.num_pages) 
	return render(request, 'blog/post/list.html', {'page': page, 'posts': posts, 'tag': tag})


def post_detail(request, year, month, day, post):  # делаем переход на определенный пост с небольшим описанием в виде даты добавления поста
	# Получаем нужный пост или ошибку 404
	post = get_object_or_404(Post, slug=post, status='published', publish__year=year, publish__month=month, publish__day=day)
	# Делаем вывод активных комментариев данной статьи
	comments = post.comments.filter(active=True)
	new_comment = None
	if request.method == 'POST':
		# Пользователь отправил комментарий
		comment_form = CommentForm(request.POST, request.FILES) 
		if comment_form.is_valid():
			# Создаем комментарий, но не сохраняем его в базу
			new_comment = comment_form.save(commit=False)
			# Привязываем его к текущему посту
			new_comment.post = post
			# И теперь сохраняем его в базу
			new_comment.save()
			# Формируем список похожих статей
			return render(request, 'blog/post/detail.html', {'post': post, 'comments': comments, 'new_comment': new_comment, 'comment_form': comment_form})
	else:
		comment_form = CommentForm()
		return render(request, 'blog/post/detail.html', {'post': post, 'comments': comments, 'new_comment': new_comment, 'comment_form': comment_form})  #  


def post_share(request, post_id):
	# Получение статьи по идентификатору
	post = get_object_or_404(Post, id=post_id, status='published') 
	sent = False
	if request.method == 'POST': 
		# Форма отправляется на сохранение
		form = EmailPostForm(request.POST)
		# Проверяем правильность заполненных полей
		if form.is_valid():
			# Все поля прошли валидацию 
			cd = form.cleaned_data
			# ... Отправка почты
			post_url = request.build_absolute_uri(post.get_absolute_url())
			subject = '{} ({}) recommends you reading "{}"'.format(cd['name'], cd['email'], post.title)
			message = 'Read "{}" at {}\n\n{}\'s comments: {}'.format(post.title, post_url, cd['name'], cd['comments'])
			send_mail(subject, message, 'murloc.helper@gmail.com', [cd['to']])
			sent = True
			return render(request, 'blog/post/share.html', {'post': post, 'form': form, 'sent': sent})
	else:
		form = EmailPostForm() # Сохраняем форму 
		return render(request, 'blog/post/share.html', {'post': post, 'form': form, 'sent': sent})


def post_search(request):
	form = SearchForm()
	query = None
	results = []
	if request.method == 'GET':
		form = SearchForm(request.GET)
		if form.is_valid():
			query = form.cleaned_data['query']
			results = Post.objects.annotate(search=SearchVector('title', 'body'),).filter(search=query)
			return render(request, 'blog/post/search.html', {'form': form, 'query': query, 'results': results})
	else:
		form = SearchForm()
	return render(request, 'blog/post/search.html', {'form': form, 'query': query, 'results': results})


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
