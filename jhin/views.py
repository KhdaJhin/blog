from django.shortcuts import render, redirect, HttpResponse, reverse
from django.http import JsonResponse
from myblog import settings
import os
from django.db import transaction
import json

# Create your views here.

from django.db.models import F, Q, Count
from django.contrib import auth
from jhin.models import UserInfo, ArticleUpDown, ArticleJTag, Tag, Category, Comment, Article, Blog


def index(request):                   # 上次登录时间没做
    article_list = Article.objects.all()

    return render(request, 'index.html', locals())


def login(request):
    if request.method == 'POST':
        usn = request.POST.get('usn')
        pwd = request.POST.get('pwd')
        user = auth.authenticate(username=usn, password=pwd)
        dic = {'ha': '用户名或密码错误！'}
        print(usn, pwd)
        if user:
            auth.login(request, user)
            dic['clear'] = 1
        return JsonResponse(dic)
    return render(request, 'login.html')


def article(request, username, article_id):
    user = UserInfo.objects.filter(username=username).first()
    # 查询当前站点对象
    user_blog = user.blog

    article_obj = Article.objects.filter(pk=article_id).first()

    comment_list = Comment.objects.filter(article_id=article_id)

    # 查询当前用户的所有分类及文章
    cate_list = Category.objects.filter(blog=user_blog).annotate(c=Count("article__title")).values_list("title", "c")

    # 查询当前用户所有标签及文章
    tag_list = Tag.objects.filter(blog=user_blog).annotate(t=Count("article__title")).values_list("title", "t")

    # 按照日期归档  extra(select={"y_m_date":"strftime('%%Y/%%m',create_time)"})
    date_list = Article.objects.filter(user=user).extra(
        select={"ym": "strftime('%%Y/%%m', create_time)"}).values('ym').annotate(
        tm=Count("title")).values_list('ym', 'tm')

    return render(request, 'article_base.html', locals())


def logout(request):
    auth.logout(request)
    return redirect(reverse('index'))


def blog(request, username, **kwargs):

    # 获取站点对象
    user = UserInfo.objects.filter(username=username).first()
    if not user:
        return HttpResponse('该用户已注销！')
    user_blog = user.blog

    # 查询这个用户发表的所有的文章、随笔
    if not kwargs:
        article_list = Article.objects.filter(user__username=username)
    else:
        condition = kwargs.get('condition')
        cate = kwargs.get('cate')
        if condition == 'category':
            article_list = Article.objects.filter(user__username=username).filter(category__title=cate)
        elif condition == "tag":
            article_list = Article.objects.filter(user__username=username).filter(tags__title=cate)
        else:
            year, moth = cate.split("/")
            article_list = Article.objects.filter(user__username=username).filter(
                create_time__year=year, create_time__month=moth)
    # 查询当前用户的所有分类及文章
    cate_list = Category.objects.filter(blog=user_blog).annotate(c=Count("article__title")).values_list("title", "c")

    # 查询当前用户所有标签及文章
    tag_list = Tag.objects.filter(blog=user_blog).annotate(t=Count("article__title")).values_list("title", "t")

    # 按照日期归档  extra(select={"y_m_date":"strftime('%%Y/%%m',create_time)"})
    date_list = Article.objects.filter(user=user).extra(
        select={"ym": "strftime('%%Y/%%m', create_time)"}).values('ym').annotate(
        tm=Count("title")).values_list('ym', 'tm')
    if not article_list:
        return HttpResponse('未找到当前文章！')
    return render(request, 'blog.html', locals())


def digg(request):
    is_up = json.loads(request.POST.get("is_up"))
    article_id = request.POST.get("article_id")
    user_id = request.user.pk
    response = {"state": True, "msg": None}

    obj = ArticleUpDown.objects.filter(user_id=user_id, article_id=article_id).first()
    if obj:
        response["state"] = False
        response["handled"] = obj.is_up
    else:
        with transaction.atomic():
            new_obj = ArticleUpDown.objects.create(user_id=user_id, article_id=article_id, is_up=is_up)
            if is_up:
                Article.objects.filter(pk=article_id).update(up_count=F("up_count") + 1)
            else:
                Article.objects.filter(pk=article_id).update(down_count=F("down_count") + 1)

    return JsonResponse(response)


def comment(request):

    # 获取数据
    user_id = request.user.pk
    article_id = request.POST.get("article_id")
    content = request.POST.get("content")
    pid = request.POST.get("pid")
    # 生成评论对象
    with transaction.atomic():
        comment = Comment.objects.create(user_id=user_id,article_id=article_id,content=content,parent_comment_id=pid)
        Article.objects.filter(pk=article_id).update(comment_count=F("comment_count")+1)
    response = {"state": True}
    response["timer"] = comment.create_time.strftime("%Y-%m-%d %X")
    response["content"] = comment.content
    response["user"] = request.user.username

    return JsonResponse(response)


def backend(request):
    user = request.user
    article_list = Article.objects.filter(user=user)
    return render(request, "backend/backend.html", locals())


def add_article(request):
    if request.method == "POST":

        title = request.POST.get("title")
        content = request.POST.get("content")
        user = request.user
        cate_pk = request.POST.get("cate")
        tags_pk_list = request.POST.getlist("tags")

        from bs4 import BeautifulSoup
        soup = BeautifulSoup(content, "html.parser")
        # 文章过滤：
        for tag in soup.find_all():
            # print(tag.name)
            if tag.name in ["script", ]:
                tag.decompose()

        # 切片文章文本
        desc = soup.text[0:150]

        article_obj = Article.objects.create(title=title,content=str(soup), user=user, category_id=cate_pk, desc=desc)

        for tag_pk in tags_pk_list:
            ArticleJTag.objects.create(article_id=article_obj.pk, tag_id=tag_pk)

        return redirect("/backend/")
    else:
        blog = request.user.blog
        cate_list=Category.objects.filter(blog=blog)
        tags = Tag.objects.filter(blog=blog)
        return render(request, "backend/add_article.html", locals())


def upload(request):
    obj=request.FILES.get("upload_img")
    name=obj.name

    path=os.path.join(settings.BASE_DIR,"static","upload",name)
    with open(path,"wb") as f:
        for line in obj:
            f.write(line)

    import json

    res={
        "error":0,
        "url":"/static/upload/"+name
    }

    return HttpResponse(json.dumps(res))


def register(request):
    if request.method == 'POST':
        usn = request.POST.get('usn')
        pwd = request.POST.get('pwd')
        eml = request.POST.get('eml')
        tel = request.POST.get('tel')
        ck = UserInfo.objects.filter(username=usn).first()
        if not ck:
            UserInfo.objects.create(
                username=usn, password=pwd,
                email=eml, telephone=tel
            )
            return JsonResponse({"used": 0})
        return JsonResponse({"used": 1})
    return render(request, 'register.html')
