from django.shortcuts import render, get_object_or_404
from django.core.mail import send_mail
from taggit.models import Tag
from django.db.models import Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger 
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank,TrigramSimilarity
from .models import HomePage, AboutPage, ContactPage, Post,SearchPage
from .forms import CommentForm ,EmailForm,SearchForm

def home(request,tag_slug=None):
  page = HomePage.objects.all()[0]
  post_list = Post.objects.all()

  if tag_slug :
    tag=get_object_or_404(Tag,slug=tag_slug)
    posts=post_list.filter(tags__in=[tag])

  paginator = Paginator(post_list, 3)
  # Get the page number from the query string (default to 1)
  page_number = request.GET.get('page', 1)
  
  try:
      posts = paginator.page(page_number)
  except PageNotAnInteger:
      posts = paginator.page(1)
  except EmptyPage:
      posts = paginator.page(paginator.num_pages)
  tag=None
  return render(request, 'blog/home.html', {'page': page, 'posts': posts,'tag':tag})

def about(request):
  page = AboutPage.objects.all()[0]
  posts = Post.objects.all()
  return render(request, 'blog/about.html', {'page': page, 'posts': posts})

def contact(request):
  page = ContactPage.objects.all()[0]
  posts = Post.objects.all()
  sent = False
  receiver_email = 'ramaalhayek2000@gmail.com'
  if request.method == 'POST':
      form = EmailForm(request.POST)
      if form.is_valid():
          cd = form.cleaned_data
          sender_email = cd['email']  
          phone = cd['phone']
          subject = cd['subject']
          message = cd['message']
          message += f"\nSender's Email: {sender_email}\nPhone: {phone}"
          send_mail(
              subject,
              message,
              sender_email,  
              [receiver_email]  
          )
          sent = True
  else:
      form = EmailForm()
  return render(request, 'blog/contact.html', {'form': form, 'sent': sent,'page': page, 'posts': posts})


def post_detail(request, year, month, day, post):
  post = get_object_or_404(Post, 
                          status=Post.Status.PUBLISHED,
                          publish__year = year,
                          publish__month = month,
                          publish__day = day,
                          slug = post
                          )
  comments = post.comments.filter(active=True)
  post_tags_ids=post.tags.values_list('id',flat=True)
  similar_posts=Post.objects.filter(tags__in=post_tags_ids).exclude(id=post.id)
  similar_posts=similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags','-publish')
  print(similar_posts)

  return render(request, 'blog/post_details.html', {'post': post, 'comments': comments,'similar_posts':similar_posts})

def post_comment(request, post_id):
  post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
  
  comment = None
  
  form = CommentForm(data=request.POST)

  if form.is_valid():
    comment = form.save(commit=False)
    comment.post = post
    comment.save()
    
  return render(request, 'blog/comment.html', {'comment': comment, 'form': form, 'post': post})



def post_search(request):
    page = SearchPage.objects.all()[0]
 # posts = Post.objects.all()
    form = SearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            search_vector = SearchVector('title', 'body')
            search_query = SearchQuery(query, config='english')
            results = Post.objects.annotate(
                search=search_vector,
                rank=SearchRank(search_vector, search_query),
                similarity=TrigramSimilarity('title', query) + TrigramSimilarity('body', query)
            ).filter(similarity__gt=0.1).order_by('-similarity', '-rank')
            
    return render(request, 'blog/search.html', {'page': page,'form': form, 'query': query, 'results': results})
