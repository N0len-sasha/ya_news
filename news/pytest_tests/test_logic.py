import pytest

from django.urls import reverse
from news.forms import WARNING

from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_can_create_comment(client,
                                           news,
                                           comment_form_data):
    url = reverse('news:detail', args=(news.id,))
    client.post(url, data=comment_form_data)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_user_can_create_comment(author_client,
                                 id_for_args,
                                 comment_form_data):
    url = reverse('news:detail', args=(id_for_args,))
    author_client.post(url, data=comment_form_data)
    assert Comment.objects.count() == 1


@pytest.mark.django_db
def test_author_can_edit_comment(author_client,
                                 news,
                                 comment,
                                 comment_form_data):
    url = reverse('news:edit', args=(news.id,))
    author_client.post(url, comment_form_data)
    comment.refresh_from_db()
    assert comment.text == comment_form_data['text']


@pytest.mark.django_db
def test_non_author_cant_edit_comment(admin_client,
                                      news,
                                      comment,
                                      comment_form_data):
    url = reverse('news:edit', args=(news.id,))
    admin_client.post(url, comment_form_data)
    comment.refresh_from_db()
    assert comment.text != comment_form_data['text']


@pytest.mark.django_db
def test_author_can_delete_comment(author_client,
                                   news,
                                   comment):
    url = reverse('news:delete', args=(news.id,))
    author_client.post(url)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_non_author_cant_delete_comment(admin_client,
                                        news,
                                        comment):
    url = reverse('news:delete', args=(news.id,))
    admin_client.post(url)
    assert Comment.objects.count() == 1


@pytest.mark.django_db
def test_warning_words_form(author_client,
                            id_for_args,
                            comment_form_data):
    comment_form_data['text'] += 'редиска, негодяй'
    url = reverse('news:detail', args=(id_for_args,))
    response = author_client.post(url, data=comment_form_data)
    assert Comment.objects.count() == 0
    form = response.context['form']
    assert 'text' in form.errors
    assert WARNING in form.errors['text']
