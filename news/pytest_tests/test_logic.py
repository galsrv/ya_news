from http import HTTPStatus
import pytest

from pytest_django.asserts import assertRedirects, assertFormError
from django.urls import reverse

from news.models import Comment
from news.forms import WARNING, BAD_WORDS


def test_user_can_create_comment(author_client, author, news, form_data):
    """Авторизованный пользователь может отправить комментарий."""
    url = reverse('news:detail', args=(news.id,))
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    # Считаем общее количество комментариев в БД, ожидаем 1 комментарий.
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    # Сверяем атрибуты объекта с ожидаемыми.
    assert new_comment.news == form_data['news']
    assert new_comment.text == form_data['text']
    assert new_comment.author == author


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, news, form_data):
    """Анонимный пользователь не может отправить комментарий."""
    url = reverse('news:detail', args=(news.id,))

    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'

    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


def test_no_bad_words(author_client, news_id_for_args):
    """Если комментарий содержит запрещённые слова, он не будет опубликован."""

    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    url = reverse('news:detail', args=news_id_for_args)

    response = author_client.post(url, data=bad_words_data)
    
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    
    assert comments_count == 0


def test_author_can_edit_comment(
        author_client,
        author,
        form_data,
        news_id_for_args,
        comment):
    """Авторизованный пользователь может редактировать или удалять
    свои комментарии.
    """
    url = reverse('news:detail', args=news_id_for_args)
    edit_url = reverse('news:edit', args=(comment.id,))
    url_to_comments = url + '#comments'

    response = author_client.post(edit_url, form_data)
    assertRedirects(response, url_to_comments)

    comment.refresh_from_db()
    assert comment.news == form_data['news']
    assert comment.text == form_data['text']
    assert comment.author == author


def test_author_can_delete_comment(
        author_client,
        news_id_for_args,
        comment_id_for_args):

    url = reverse('news:detail', args=(news_id_for_args))
    delete_url = reverse('news:delete', args=comment_id_for_args)
    url_to_comments = url + '#comments'

    response = author_client.post(delete_url)

    assertRedirects(response, url_to_comments)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_other_user_cant_edit_comment(
        commentator_client,
        form_data,
        news_id_for_args,
        comment):
    """Авторизованный пользователь не может редактировать или удалять
    чужие комментарии.
    """
    url = reverse('news:edit', args=news_id_for_args)
    response = commentator_client.post(url, form_data)

    assert response.status_code == HTTPStatus.NOT_FOUND

    comment_from_db = Comment.objects.get(id=comment.id)

    assert comment.news == comment_from_db.news
    assert comment.text == comment_from_db.text
    assert comment.author == comment_from_db.author


def test_other_user_cant_delete_comment(
        commentator_client,
        comment,
        news_id_for_args):
    url = reverse('news:delete', args=news_id_for_args)
    response = commentator_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
