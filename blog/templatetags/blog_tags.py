from django import template
from ..models import Post, Comment, Category
from django.db.models import Count

register = template.Library()

@register.inclusion_tag('blog/post/latest_posts.html')
def show_latest_posts(count=5):
	latest_posts = Post.published.order_by('-publish')[:count]
	return {'latest_posts': latest_posts}

@register.simple_tag
def get_most_commented_posts(count=5):
	return Post.published.annotate(total_comments=Count('comments')).order_by('total_comments')[:count]
	
@register.inclusion_tag('blog/post/latest_comments.html')
def show_latest_comments(count=5):  # 2й блок в боковой панеле (раздел Comments)
	latest_comments = Comment.commented.order_by('-created')[:count]
	return {'latest_comments': latest_comments}

@register.simple_tag
def get_most_commented_posts_detail(count=5):  # 2й блок в боковой панеле (раздел Popular)
	return Post.published.annotate(total_comments=Count('comments')).order_by('total_comments')[:count]

@register.inclusion_tag('blog/post/all_tags.html')
def show_all_tags(count=20):  # 2й блок в боковой панеле (раздел Tags)
	all_tags = Post.tags.order_by('-name')
	return {'all_tags': all_tags}

@register.simple_tag
def get_most_popular_categories(count=10):
	return Category.title.annotate(total_posts=Count('posts')).order_by('total_posts')[:count]
