from django.urls import reverse
import pytest
from pytest_lazyfixture import lazy_fixture

from yanews import settings

HOME_URL = reverse('news:home')


@pytest.mark.django_db
def test_news_count(client, news_bulk):
    """Количество новостей на главной странице — не более 10."""
    response = client.get(HOME_URL)
    object_list = response.context['object_list']
    news_count = len(object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, news_bulk):
    """Новости отсортированы от самой свежей к самой старой.
    Свежие новости в начале списка.
    """
    response = client.get(HOME_URL)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(client, news, comments_bulk, news_id_for_args):
    """Комментарии на странице отдельной новости отсортированы
    от старых к новым: старые в начале списка, новые — в конце.
    """
    response = client.get(reverse('news:detail', args=(news_id_for_args)))
    assert 'news' in response.context
    all_comments = news.comment_set.all()
    assert all_comments[0].created < all_comments[1].created


@pytest.mark.parametrize(
    'user, outcome',
    (
        (lazy_fixture('client'), False),
        (lazy_fixture('author_client'), True)
    )
)
@pytest.mark.django_db
def test_anonymous_client_has_no_form_but_author_has(
    user,
    outcome,
    detail_url
):
    """Анонимному пользователю не видна форма для отправки комментария
    на странице отдельной новости, а авторизованному видна.
    """
    response = user.get(detail_url)
    assert ('form' in response.context) == outcome
