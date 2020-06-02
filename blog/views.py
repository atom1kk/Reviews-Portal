from django.shortcuts import render, get_object_or_404
from .models import Post, Comment
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from django.core.mail import send_mail
from .forms import EmailPostForm, CommentForm
from PIL import Image
from taggit.models import Tag

class PostListView(ListView):
	queryset = Post.published.all()
	context_object_name = 'posts'
	paginate_by = 3
	template_name = 'blog/post/list.html'

def post_list(request, tag_slug=None):
	object_list = Post.published.all()  # запрашиваем все опубликованные статьи с помощью менеджера published
	tag = None

	if tag_slug:
		tag = get_object_or_404(Tag, slug=tag_slug)
		object_list = object_list.filter(tags__in=[tag])

	paginator = Paginator(object_list, 3)  # по 3 статьи на страницу
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

