from http import HTTPStatus
import pytest

from pytest_lazyfixture import lazy_fixture
from pytest_django.asserts import assertRedirects
from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.parametrize(
    ('name', 'args'),
    (
        ('news:home', None),
        ('news:detail', lazy_fixture('news_id_for_args')),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None)
    )
)
def test_pages_availability_for_anonymous_user(client, name, args):
    """Главная страница доступна анонимному пользователю.
    Страница отдельной новости доступна анонимному пользователю.
    Страницы регистрации пользователей, входа в учётную запись и
    выхода из неё доступны анонимным пользователям.
    """
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'myclient, expected_status',
    (
        (lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND),
        (lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
@pytest.mark.parametrize(
    'args', (lazy_fixture('comment_id_for_args'), )
)
def test_pages_availability_for_different_users(
        myclient, name, args, expected_status
):
    """Страницы удаления и редактирования комментария
    доступны автору комментария.
    Авторизованный пользователь не может зайти на страницу редактирования или
    удаления чужих комментариев (возвращается ошибка 404).
    """
    url = reverse(name, args=args)
    response = myclient.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', lazy_fixture('comment_id_for_args')),
        ('news:delete', lazy_fixture('comment_id_for_args')),
    ),
)
def test_redirects(client, name, args):
    """При попытке перейти на страницу редактирования или удаления комментария
    анонимный пользователь перенаправляется на страницу авторизации.
    """
    login_url = reverse('users:login')
    url = reverse(name, args=args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
