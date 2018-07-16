from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.


class UserInfo(AbstractUser):  # 用户信息

    nid = models.AutoField(primary_key=True)
    telephone = models.CharField(max_length=11, null=True, unique=True)
    avatar = models.FileField(upload_to='avatars/', default='avatars/default.png')
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

    blog = models.OneToOneField(to_field='nid', to='Blog', null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.username


class Blog(models.Model):   # 博客信息

    nid = models.AutoField(primary_key=True)
    title = models.CharField(verbose_name='个人博客标题', max_length=64)
    site_name = models.CharField(verbose_name='站点名称', max_length=64)
    theme = models.CharField(verbose_name='博客主题', max_length=32)

    def __str__(self):
        return self.title


class Category(models.Model):   # 博客分类

    nid = models.AutoField(primary_key=True)
    title = models.CharField(verbose_name='分类标题', max_length=32)
    blog = models.ForeignKey('Blog', models.CASCADE,
                             verbose_name='所属博客', to_field='nid')

    def __str__(self):
        return self.title


class Tag(models.Model):

    nid = models.AutoField(primary_key=True)
    title = models.CharField(verbose_name='分类标题', max_length=32)
    blog = models.ForeignKey(
        'Blog', models.CASCADE,
        to_field='nid', verbose_name='所属博客'
    )

    def __str__(self):
        return self.title


class Article(models.Model):  # 文章相关

    nid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50, verbose_name='文章标题')
    desc = models.CharField(max_length=255, verbose_name='文章描述')
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    content = models.TextField()

    comment_count = models.IntegerField(default=0)
    up_cout = models.IntegerField(default=0)
    down_count = models.IntegerField(default=0)
    read = models.IntegerField(default=0)

    user = models.ForeignKey('UserInfo', models.CASCADE,
                             to_field='nid', verbose_name='作者', )
    category = models.ForeignKey(
        to='Category', to_field='nid',
        null=True, on_delete=models.CASCADE
    )
    tags = models.ManyToManyField(
        to="Tag",
        through="ArticleJTag",
    )

    def __str__(self):
        return self.title


class ArticleJTag(models.Model):  # 文章标签多对多表

    nid = models.AutoField(primary_key=True)
    article = models.ForeignKey('Article', models.CASCADE, to_field='nid', verbose_name='文章')
    tag = models.ForeignKey(
        verbose_name='标签',
        to='Tag',
        to_field='nid',
        on_delete=models.CASCADE
    )

    class Meta:
        unique_together = [
            ('article', 'tag')
        ]

        def __str__(self):
            v = self.article.title + self.tag.title
            return v


class ArticleUpDown(models.Model):  # 用户文章点击记录表

    nid = models.AutoField(primary_key=True)
    user = models.ForeignKey('UserInfo', models.CASCADE, null=True)
    article = models.ForeignKey('Article', models.CASCADE, null=True)
    is_up = models.BooleanField(default=True)

    class Meta:
        unique_together = [
            ('article', 'user')
        ]


class Comment(models.Model):   # 评论

    nid = models.AutoField(primary_key=True)
    article = models.ForeignKey('Article',
                                models.CASCADE, to_field='nid', verbose_name='评论文章')

    user = models.ForeignKey(
        'UserInfo', models.CASCADE,
        to_field='nid', verbose_name='评论者'
    )
    content = models.CharField(verbose_name='评论内容', max_length=300)

    create_time = models.DateTimeField('创建时间', None, True)
    parent_comment = models.ForeignKey('Comment', models.CASCADE, null=True)

    def __str__(self):
        return self.content
