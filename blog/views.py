from django.db.models import Count, Prefetch
from django.shortcuts import render
from blog.models import Comment, Post, Tag


def serialize_post(post):
    return {
        'title': post.title,
        'teaser_text': post.text[:200],
        'author': post.author.username,
        'comments_amount': post.comments_count,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in post.tags.all()],
        'first_tag_title': post.tags.all()[0].title if post.tags.all() else None,
    }


def serialize_tag(tag):
    return {
        'title': tag.title,
        'posts_with_tag': tag.posts_count,
    }


def index(request):

    tags_qs = Tag.objects.annotate(posts_count=Count('posts'))

    most_popular_posts = (
        Post.objects.popular()
        .select_related('author')
        .prefetch_related(Prefetch('tags', queryset=tags_qs))[:5]
        .fetch_with_comments_count()
    )

    fresh_posts = Post.objects.select_related('author').order_by('published_at')
    fresh_ids = [post.id for post in fresh_posts][-5:]
    most_fresh_posts = (
        Post.objects
        .filter(id__in=fresh_ids)
        .select_related('author')
        .prefetch_related(Prefetch('tags', queryset=tags_qs))
        .fetch_with_comments_count()
    )

    most_popular_tags = Tag.objects.popular()[:5]

    context = {
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
        'page_posts': [serialize_post(post) for post in most_fresh_posts],
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
    }
    return render(request, 'index.html', context)


def post_detail(request, slug):
    tags_qs = Tag.objects.annotate(posts_count=Count('posts'))

    post = (
        Post.objects
        .select_related('author')
        .prefetch_related(Prefetch('tags', queryset=tags_qs))
        .get(slug=slug)
    )

    comments = (
        Comment.objects
        .select_related('author')
        .filter(post=post)
    )
    serialized_comments = []
    for comment in comments:
        serialized_comments.append({
            'text': comment.text,
            'published_at': comment.published_at,
            'author': comment.author.username,
        })

    likes_amount = post.likes.count()

    serialized_post = {
        'title': post.title,
        'text': post.text,
        'author': post.author.username,
        'comments': serialized_comments,
        'likes_amount': likes_amount,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in post.tags.all()],
    }

    most_popular_tags = Tag.objects.popular()[:5]

    most_popular_posts = (
        Post.objects.popular()
        .select_related('author')
        .prefetch_related(Prefetch('tags', queryset=tags_qs))[:5]
        .fetch_with_comments_count()
    )

    context = {
        'post': serialized_post,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
    }
    return render(request, 'post-details.html', context)


def tag_filter(request, tag_title):
    tags_qs = Tag.objects.annotate(posts_count=Count('posts'))

    tag = Tag.objects.get(title=tag_title)

    most_popular_tags = Tag.objects.popular()[:5]

    most_popular_posts = (
        Post.objects.popular()
        .select_related('author')
        .prefetch_related(Prefetch('tags', queryset=tags_qs))[:5]
        .fetch_with_comments_count()
    )

    related_posts = (
        Post.objects
        .filter(tags=tag)
        .select_related('author')
        .prefetch_related(Prefetch('tags', queryset=tags_qs))
        .annotate(comments_count=Count('comment'))
        .order_by('-published_at')[:20]
    )

    context = {
        'tag': tag.title,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        'posts': [serialize_post(post) for post in related_posts],
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
    }
    return render(request, 'posts-list.html', context)


def contacts(request):
    return render(request, 'contacts.html', {})