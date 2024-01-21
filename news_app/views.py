from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, UpdateView, DeleteView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from hitcount.views import HitCountDetailView, HitCountMixin
from hitcount.utils import get_hitcount_model

from .models import News, Category
from .forms import ContactForm, CommentForm
from news_project.custom_permissions import OnlyLoggedSuperUser

def news_list(request):
    news = News.published.all()
    context = {
        'news': news
    }
    return render(request, "news/news.html", context)



def news_detail(request, news):
    news = get_object_or_404(News, slug=news, status=News.Status.PUBLISHED)
    context = {}
    hit_count = get_hitcount_model().objects.get_for_object(news)
    hits = hit_count.hits
    hitcontext = context['hitcount'] = {'pk': hit_count.pk}
    hit_count_respons = HitCountMixin.hit_count(request, hit_count)
    if hit_count_respons.hit_counted:
        # Increment the hit count
        hits = hits + 1
        # Update the context
        hitcontext['hit_counted'] = hit_count_respons.hit_counted
        hitcontext['hit_message'] = hit_count_respons.hit_message
        hitcontext['total_hits'] = hits

    comments = news.comments.filter(active=True)
    comment_count = comments.count()
    new_comments = None

    if request.method == 'POST':
        comment_form = CommentForm(data= request.POST)
        if comment_form.is_valid():
            #yangi comment obyektini yaratamiz lekin saqlamaymiz
            new_comment = comment_form.save(commit=False)
            new_comment.news = news
            new_comment.user = request.user
            #malumotlar bazasiga saqlaymiz
            new_comment.save()
            comment_form = CommentForm()

    else:
        comment_form = CommentForm()
    context = {
        'news': news,
        'comments': comments,
        'new_comments': new_comments,
        'comment_count' : comments.count,
        'comment_form': comment_form,

    }
    return render(request, "news/news_detail.html", context)

def homePageView(request):
    categories = Category.objects.all()
    news_list = News.published.all().order_by('-publish_time')[:5]
    local_one = News.published.filter(category__name = "Mahalliy").order_by('-publish_time')[:1]
    local_news = News.published.all().filter(category__name="Mahalliy").order_by('-publish_time')[:5]

    context = {
        'news_list': news_list,
        'categories': categories,
        'local_one': local_one ,
        'local_news': local_news
    }

    return render(request, "news/home.html", context)


class HomePageView(ListView):
    model = News
    template_name = 'news/home.html'
    context_object_name = 'news'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['news_list'] = News.published.all().order_by('-publish_time')[:5]
        context['mahalliy_xabarlar'] = News.published.all().filter(category__name="Mahalliy").order_by('-publish_time')[:5]
        context['Xorij_xabarlari'] = News.published.all().filter(category__name="Xorij").order_by('-publish_time')[:5]
        context['Sport_xabarlar'] = News.published.all().filter(category__name="Sport").order_by('-publish_time')[:5]
        context['Texnologiya_xabarlar'] = News.published.all().filter(category__name="Texnologiya").order_by('-publish_time')[:5]

        return context

class ContactPageView(TemplateView):
    template_name = "news/contact.html"

    def get(self, request, *args, **kwargs ):
        form = ContactForm()
        context = {
            "form":  form
        }
        return render(request, 'news/contact.html', context)

    def post(self, request, *args, **kwargs ):
        form = ContactForm(request.POST)
        if request.method == "POST" and form.is_valid():
            form.save()
            return HttpResponse("<h2> Biz bilan boglanganingiz uchun tashakkur </h2>")

        context = {
            'form': form
        }

        return render(request, "news/contact.html", context)

class LocalNewsView(ListView):
    model = News
    template_name = "news/mahalliy.html"
    context_object_name = "mahalliy_yangiliklar"

    def get_queryset(self):
        news = self.model.published.all().filter(category__name="Mahalliy")
        return news


class ForeignNewsView(ListView):
    model = News
    template_name = "news/Xorij.html"
    context_object_name = "xorij_yangiliklar"

    def get_queryset(self):
        news = self.model.published.all().filter(category__name="Xorij")
        return news

class TechnologyNewsView(ListView):
    model = News
    template_name = "news/Texnologiya.html"
    context_object_name = "texnologik_yangiliklar"

    def get_queryset(self):
        news = self.model.published.all().filter(category__name="Texnologiya")
        return news


class SportNewsView(ListView):
    model = News
    template_name = "news/Sport.html"
    context_object_name = "sport_yangiliklar"

    def get_queryset(self):
        news = self.model.published.all().filter(category__name="Sport")
        return news


class NewsUpdateView(OnlyLoggedSuperUser, UpdateView):
    model = News
    fields = ('title', 'body', 'image', 'category', 'status', )
    template_name = 'crud/news_edit.html'


class NewsDeleteView(OnlyLoggedSuperUser, DeleteView):
    model = News
    template_name = 'crud/news_delete.html'
    success_url = reverse_lazy('home_page')

class NewsCreateView( LoginRequiredMixin, CreateView):
    model = News
    template_name = 'crud/news_create.html'
    fields = ('title', 'slug', 'image', 'category', 'status')


@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_page_view(request):
    admin_users = User.objects.filter(is_superuser=True)

    context ={
        'admin_users': admin_users
    }
    return render(request, 'pages/admin_page.html', context)


class SearchResultList(ListView):
    model = News
    template_name = 'news/search_result.html'
    context_object_name = 'barcha_yangiliklar'

    def get_queryset(self):
        query = self.request.GET.get('q')
        return News.objects.filter(
            Q(title__icontains=query) | Q(body__icontains=query)
        )