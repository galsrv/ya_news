from datetime import datetime, timedelta
from django.urls import reverse
import pytest

from django.utils import timezone

from news.models import News, Comment
from yanews import settings


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def commentator(django_user_model):
    return django_user_model.objects.create(username='Комментатор')


@pytest.fixture
def commentator_client(client, commentator):
    client.force_login(commentator)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок новости',
        text='Текст новости'
    )
    return news


@pytest.fixture
def news_bulk():
    today = datetime.today()
    news_bulk = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(news_bulk)
    return news_bulk


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )
    return comment


@pytest.fixture
def comments_bulk(author, news):
    now = timezone.now()
    for index in range(2):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Текст комментария {index}'
        )
        comment.created = now + timedelta(days=index)
        comment.save()
    return comments_bulk


@pytest.fixture
def news_id_for_args(news):
    return news.id,


@pytest.fixture
def comment_id_for_args(comment):
    return comment.id,


@pytest.fixture
def detail_url(news_id_for_args):
    return reverse('news:detail', args=(news_id_for_args))


@pytest.fixture
def form_data(news, author):
    return {
        'news': news,
        'author': author,
        'text': 'Новый текст комментария'
    } 
