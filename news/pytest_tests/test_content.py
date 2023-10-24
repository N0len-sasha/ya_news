import pytest

from django.urls import reverse

from news.models import News, Comment
from django.utils import timezone



@pytest.mark.django_db
def test_news_count_on_home_page(client):
    for i in range(11):
        News.objects.create(
            title=f'Заголовок {i}',
            text=f'Текст новости {i}'
        )
    response = client.get(reverse('news:home'))

    assert len(response.context['news_list']) == 10


@pytest.mark.django_db
def test_news_sorted_by_date(client):
    news1 = News.objects.create(title='Новость 1', text='Текст новости 1')
    news2 = News.objects.create(title='Новость 2', text='Текст новости 2')
    news3 = News.objects.create(title='Новость 3', text='Текст новости 3')

    news1.date = '2023-10-01'
    news1.save()
    news2.date = '2023-10-03'
    news2.save()
    news3.date = '2023-10-02'
    news3.save()

    response = client.get(reverse('news:home'))
    news_list = response.context['news_list']

    assert news_list[0] == news2
    assert news_list[1] == news3
    assert news_list[2] == news1


@pytest.mark.django_db
def test_comments_sorted_by_date(client, author):
    news = News.objects.create(title='Заголовок новости', text='Текст новости')

    comment1 = Comment.objects.create(news=news,
                                      author=author,
                                      text='Текст комментария 1')
    comment2 = Comment.objects.create(news=news,
                                      author=author,
                                      text='Текст комментария 2')
    comment3 = Comment.objects.create(news=news,
                                      author=author,
                                      text='Текст комментария 3')

    comment1.created = timezone.make_aware(timezone.datetime(2023, 10, 1))
    comment1.save()
    comment2.created = timezone.make_aware(timezone.datetime(2023, 10, 3))
    comment2.save()
    comment3.created = timezone.make_aware(timezone.datetime(2023, 10, 2))
    comment3.save()
    response = client.get(reverse('news:detail', args=[news.id]))
    news = response.context['news']
    comment_list = news.comment_set.all()

    assert comment_list[0] == comment1
    assert comment_list[1] == comment3
    assert comment_list[2] == comment2


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, id_for_args):
    response = client.get(reverse('news:detail', args=(id_for_args,)))
    assert 'form' not in response.context


@pytest.mark.django_db
def test_authorized_client_has_form(author_client, id_for_args):
    response = author_client.get(reverse('news:detail', args=(id_for_args,)))
    assert 'form' in response.context
