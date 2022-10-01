from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from typing import Union
import re

from django.urls import reverse_lazy

STRIP_HTML_TAGS = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
# God bless stack overflow!


class BaseModel(models.Model):
    """A dirty little hack to allow PyCharm community edition (and, possibly other IDEs) to correctly resolve
    .objects for models. # God bless stack overflow!
    """

    objects = models.Manager()

    class Meta:
        abstract = True


class SiteUser(BaseModel):
    """Extension on User model.
        # user_id	PK; FK ON USERS
        # display_username	VARCHAR
        # is_author	BOOL
        # can_publish	BOOL
        # is_editor	BOOL
        # is_admin	BOOL
        # is_moderator	BOOL
        # muted_until	DATETIME
        # banned_until	DATETIME
        # post_karma	BIGINT
        # comment_karma	BIGINT
        # date_registered	DATETIME
        # total_posts	INT
        # total_comments	INT
    """

    user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
    display_username = models.CharField(max_length=100, unique=True)
    is_author = models.BooleanField(default=False)
    can_publish = models.BooleanField(default=False)
    is_editor = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_moderator = models.BooleanField(default=False)
    muted_until = models.DateTimeField(null=True, blank=True)
    banned_until = models.DateTimeField(null=True, blank=True)
    post_karma = models.BigIntegerField(default=0, editable=False)
    comment_karma = models.BigIntegerField(default=0, editable=False)
    date_registered = models.DateTimeField(auto_now_add=True, editable=False)
    total_posts = models.IntegerField(default=0, editable=False)
    total_comments = models.IntegerField(default=0, editable=False)
    # misc_properties = models.JSONField(null=True, blank=True, editable=False) #  sqlite can't do this

    def __str__(self):
        return self.display_username

    def get_compound_rating(self) -> Union[int, None]:
        """Returns a metric that measures Author's overall popularity."""
        posts_by_author = Post.objects.filter(author=self)

        if not len(posts_by_author):
            return None  # user haven't posted anything

        posts_rating = posts_by_author.aggregate(pr=Sum('updoot_count'))['pr']

        comments_rating = Comment.objects.filter(user=self).aggregate(cr=Sum('updoot_count'))['cr']

        # .exclude() used to not count the rating for author's own comments on his own post twice
        comments_for_authors_posts_rating = \
            Comment.objects.filter(post__in=posts_by_author)\
                .exclude(user=self).aggregate(apcr=Sum('updoot_count'))['apcr']

        if comments_rating is None:
            comments_rating = 0
        if comments_for_authors_posts_rating is None:
            comments_for_authors_posts_rating = 0

        return posts_rating * 3 + comments_rating + comments_for_authors_posts_rating


class Tags(BaseModel):
    """# tag_id	SERIAL PK	title	VARCHAR	count	INT"""
    title = models.CharField(max_length=120, unique=True)
    count = models.IntegerField(default=0, editable=False)

    def __str__(self):
        return self.title


class PostTags(BaseModel):
    """ post_id	INT tag_id	INT"""
    post = models.ForeignKey('Post', on_delete=models.CASCADE)
    tag = models.ForeignKey(Tags, on_delete=models.CASCADE)
    unique_together = ['post', 'tag']  # only one instance of tag per post




class Post(BaseModel):
    """Articles or News. TODO: "slug" field for URLS
        # post_id	SERIAL PK
        # category_id	INT
        # title VARCHAR
        # is_article	BOOL
        # author	INT
        # content	TEXT
        # updoot_count	INT
        # published	BOOL
        # publication_date	DATETIME
    """
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True)
    is_article = models.BooleanField(default=False)
    title = models.CharField(max_length=255)
    author = models.ForeignKey('SiteUser', on_delete=models.CASCADE)
    content = models.TextField()
    updoot_count = models.IntegerField(default=0, editable=False)
    published = models.BooleanField(default=False)
    publication_date = models.DateTimeField(null=True, blank=True)
    tags = models.ManyToManyField(Tags, through='PostTags')

    def __str__(self):
        return self.title

    def like(self):
        """Note: this shouldn't be called directly. Only then record in PostUpdoots is created/updated/deleted"""
        self.updoot_count += 1
        self.save()

    def dislike(self):
        """Note: this shouldn't be called directly. Only then record in PostUpdoots is created/updated/deleted"""
        self.updoot_count -= 1
        self.save()

    def get_preview(self, num_chars: int = 124) -> str:
        """Returns preview of article text with tags stripped, enveloped in <p> tag."""
        # todo make this return "...Foo..." instead of "...Foo ba..."
        # todo allow user to specify different tags via optional arguments
        return '<p>' + re.sub(STRIP_HTML_TAGS, '', str(self.content))[:num_chars] + '...</p>\n'

    def get_absolute_url(self):
        return reverse_lazy('show_post', kwargs={'pk': self.pk})


class Comment(BaseModel):
    """Comments for posts. Note: nested comments are not implemented at the moment
    # comment_id	BIGSERIAL PK
    # post_id	INT
    # user_id	INT
    # content	TEXT
    # parent_comment_id	BIGINT
    # parent_comment_path	VARCHAR
    # comments_depth	SMALLINT
    # comment_by_op	BOOL
    # updoot_count	INT
    # updoot_count_thread	BIGINT ;)
    # replies_count	INT
    # publication_date	DATETIME
    # has_been_edited	BOOL
    """

    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(SiteUser, on_delete=models.SET_NULL, null=True)
    content = models.TextField()
    parent_comment_id = models.IntegerField(default=0, editable=False)
    parent_comment_path = models.CharField(default='', editable=False, max_length=255)
    comments_depth = models.SmallIntegerField(default=0, editable=False)
    comment_by_op = models.BooleanField(default=False, editable=False)
    updoot_count = models.IntegerField(default=0, editable=False)
    updoot_count_thread = models.BigIntegerField(default=0, editable=False)
    replies_count = models.IntegerField(default=0, editable=False)
    publication_date = models.DateTimeField(auto_now_add=True, editable=False)
    has_been_edited = models.BooleanField(default=False, editable=False)

    # def get_all_parent_comments(self):
    #     parents = str(self.parent_comment_path).split('/')[1:-1]
    #     return BBWComment.objects.filter(parent_comment_id__in = parents)


    def like(self):
        """Note: this shouldn't be called directly. Only then record in CommentUpdoots is created/updated/deleted"""
        self.updoot_count += 1
        self.save()

    def dislike(self):
        """Note: this shouldn't be called directly. Only then record in CommentUpdoots is created/updated/deleted"""
        self.updoot_count -= 1
        self.save()


class Category(BaseModel):
    """Only one category per post. TODO: slug field for URLS
    # category_id	SERIAL PK
    # title	VARCHAR
    # count	INT
    """
    title = models.CharField(max_length=100, unique=True)
    count = models.IntegerField(default=0, editable=False)

    def __str__(self):
        return self.title


class PostUpdoots(BaseModel):
    """is_updoot=True means upvote, is_updoot=False means downvote
    # post_id	INT
    user_id	INT
    is_updoot	BOOL
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(SiteUser, on_delete=models.CASCADE)
    is_updoot = models.BooleanField(default=True, editable=False)
    unique_together = ['post', 'user']  # only one updoot per post per user


class CommentUpdoots(BaseModel):
    """is_updoot=True means upvote, is_updoot=False means downvote
    # comment_id	INT
    user_id	INT
    is_updoot	BOOL
    """
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    user = models.ForeignKey(SiteUser, on_delete=models.CASCADE)
    is_updoot = models.BooleanField(default=True, editable=False)
    unique_together = ['comment', 'user']  # only one updoot per comment per user



