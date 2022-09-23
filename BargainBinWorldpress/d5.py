"""Import this file into django shell via "from d5 import *" to fill database with some test data"""

from bbw.models import *
from random import choice as ch, randint
from typing import Union


def get_random_sentences(num_sentences: int = 1) -> str:
    """Used to generate random text for posts and post titles."""

    OBJECTS = ('Евгений Онегин', 'президент профсоюза политруков', 'ликвидатор мухоморов', 'каштановый куст',
                'цианистый калий', 'возмутитель спокойствия', 'погибший на рейве', 'шушпанчик',
                'строительный мусор', 'широко известный очковтиратель', 'крупнейший потребитель электроэнергии',
                'мороз-воевода', 'наблюдательный картограф', 'почётный житель закрытого города')
    ADVERBS = ('стремительно', 'безапелляционно', 'с несвойственным ему рвением', 'будто в замедленной съёмке',
               'не унывая', 'не снимая ботинок', 'после тщательной оценки возможных последствий', 'взгрустнув',
               'засучив рукава', 'смешно семеня', 'не без ущерба для собственного здоровья', 'назло всем')
    VERBS = ('расцарапал лицо', 'создавал многочисленные препоны', 'брызнул слюной в лицо', 'исполнил серенаду',
             'преподнёс сюрприз', 'закрутил все гайки', 'пояснил за жизнь', 'сократил ареал обитания',
             'перегрыз отросток', 'продлил карантин', 'передал бразды', 'испортил спасательный жилет',
             'передаёт привет', 'сбрил брови', 'воздал должное', 'покажет кузькину мать')
    ADJECTIVES = ('красивому', 'серо-фиолетовому', 'пофигистски настроенному', 'потерявшему берега', 'нерешительному',
                  'разводящему пчёл-убийц', 'лыком не вяжущему', 'сидящему на пеньке', 'неликвидному', 'сказочному',
                  'недавно осиротевшему', 'мирно посапывавшему', 'трансцендентному', 'смертоносному', 'асоциальному')
    SUBJECTS = ('человеку из Сыктывкара', 'врачу-оториноларингологу', 'представителю заказчика', 'пакету ценных бумаг',
                'полуторалитровому стакану', 'представителю семейства кошачих', 'фиговому дереву', 'консументу мемасов',
                'лидеру мнений', 'ведру с гайками', 'двойному чизбургеру', 'автомобилю Ока', 'агроному', 'субъекту права',
                'пакету с пакетами', 'двойнику Стива Балмера', 'составителю альманахов', 'порядочному семьянину')

    ENDINGS = ('.', '.', '.', '.', '.', '!', '!',  '!..', '...', '!?', ':-/')

    #####

    coolstory = ''
    for _ in range(num_sentences):
        coolstory += ' '.join([[ch(OBJECTS).capitalize(), ch(ADVERBS), ch(VERBS), ch(ADJECTIVES), ch(SUBJECTS)],
                            [ch(ADJECTIVES).capitalize(), ch(SUBJECTS), ch(ADVERBS), ch(VERBS), ch(OBJECTS)]]
                            [randint(0, 1)]) + ch(ENDINGS) + ' '
    return coolstory


def add_author(name: Union[str, None] = None) -> None:  # assignment 1, 2
    """Only alphanumeric and spaces in name, please. I can't be bothered to check. Leave blank for boring random name."""

    if name is None:
        name = "site user number " + str(randint(1000, 100000))
    newuser = User.objects.create_user(username=name, email=name.replace(' ', '') + '@foobar.domain', password='')
    newbbwuser = SiteUser.objects.create(display_username = name)
    print(f'Создан пользователь {newbbwuser.display_username} c id = {newbbwuser.pk}')
    print('asdfasdfsdf')


def add_tag(title_:str) -> None:  # assignment 3 but tags instead of categories
    """Add a new tag to database"""

    Tags.objects.create(title=title_)
    print(f'Добавили тег "{title_}"')


def add_post(user_id: int, category_id: int, is_article: bool = True) -> None:   # assignment 4
    """Generate a post full of random gibberish."""
    new_post_title = get_random_sentences(1)
    new_post_content = ''
    post_author = SiteUser.objects.get(user_id=user_id)
    post_category = Category.objects.get(id=category_id)
    for _ in range(randint(4 + 4 * is_article, 8 + 12 * is_article)):
        new_post_content += f'<p>{get_random_sentences(randint(4, 8))}</p>\n'
    Post.objects.create(title=new_post_title, content=new_post_content, author=post_author,
                        category_id=post_category, is_article=is_article)
    print(new_post_title)
    # print(new_post_content)


def assign_post_tag(post_id: int, tag_id: int) -> None: # assignment 7, but tags instead of categories
    """Adds a tag to post"""
    post = Post.objects.get(id=post_id)
    tag = Tags.objects.get(id=tag_id)
    post.tags.add(tag)
    post.save()


def add_comments(post_id: int, user_id: int, num_comments: int = 20) -> None:  # assignment 6
    """Fill post's comment section with meaningful discussion"""
    post = Post.objects.get(id=post_id)
    user = SiteUser.objects.get(user_id=user_id)
    for _ in range(num_comments):
        Comment.objects.create(user_id=user, post_id = post, content=get_random_sentences(randint(1, 4)))
    print(f'Успешно запилили {num_comments} коментов к посту "{post.title}"')


def randomize_post_scores() -> None:  # assignment 7a
    posts = Post.objects.all()
    for post in posts:
        post.updoot_count = randint(-10, 42)
        post.save()
    print(f'Успешно зарандомили плюсики ко всем постам')


def randomize_comments_scores(post_id) -> None:  # assignment 7b
    post = Post.objects.get(id=post_id)
    comments = Comment.objects.filter(post_id=post)
    for comment in comments:
        comment.updoot_count = randint(-10, 42)
        comment.save()
    print(f'Успешно зарандомили плюсики к комментам к посту {post.title}')


def recalculate_users_ratings() -> None:  # assignment 8, but not using "compound_rating"
    """Recalculates upvotes for all users."""

    for user in SiteUser.objects.all():
        post_karma = Post.objects.filter(author=user).aggregate(pk=Sum('updoot_count'))['pk']
        comment_karma = Comment.objects.filter(user_id=user).aggregate(kk=Sum('updoot_count'))['kk']
        user.post_karma = post_karma if post_karma else 0
        user.comment_karma = comment_karma if comment_karma else 0
        user.save()
    print(f'Обновили рейтинги пользователям {SiteUser.objects.all()} ')


def best_author() -> None:  # assignment 9, but not using compound_rating
    best = SiteUser.objects.order_by('-post_karma')[0]
    print(f'{best.display_username} - лучший автор, у него - {best.post_karma} плюсиков.')


def best_commenter() -> None:  # assignment 9, but not using compound_rating
    best = SiteUser.objects.order_by('-comment')[0]
    print(f'{best.display_username} - лучший комментатор, у него - {best.comment_karma} плюсиков.')


def preview_best_article(want_comments=False) -> None:  # assignment 10, 11
    best = Post.objects.order_by('-updoot_count')[0]
    print(f'лучший пост "{best.title}" был опубликован пользователем {best.author.display_username}.')
    print(f'У него - {best.updoot_count} плюсиков!')
    print(best.get_preview())
    if not want_comments:
        return None
    comments = Comment.objects.filter(post_id=best).order_by('-updoot_count')
    for comment in comments:
        print(f'\n\n{comment.user_id.display_username}||{comment.publication_date}||{comment.updoot_count}')
        print(f'{comment.content}\n====================================================')
    return None


def q(): quit()  # just a shortcut


#  user should not be messing with this file, it's for debug only
print('А ТЫ СДЕЛАЛ БЭКАП, ПРЕЖДЕ ЧЕМ ПОРТИТЬ БАЗУ?')
