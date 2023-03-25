from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.http import Http404

from .models import BlogPost, Entry
from .forms import BlogPostForm, EntryForm

# Create your views here.


def index(request):
    """Головна сторінка додатку Learning Log"""
    return render(request, 'blogs/index.html')


@login_required
def topics(request):
    """Виводить список тем"""
    topics = BlogPost.objects.filter(owner=request.user).order_by('date_added')
    context = {'topics': topics}
    return render(request, 'blogs/topics.html', context)


@login_required
def topic(request, topic_id):
    """Виводить одну тему і всі ії записи"""
    topic = BlogPost.objects.get(id=topic_id)
    if topic.owner != request.user:
        raise Http404
    entries = topic.entry_set.order_by('-date_added')
    context = {'topic': topic, 'entries': entries}
    return render(request, 'blogs/topic.html', context)


@login_required
def new_topic(request):
    """Додає нову тему"""
    if request.method != 'POST':
        # Дані не відправлялись, створюється пуста форма
        form = BlogPostForm()
    else:
        # Обробка даних з форми
        form = BlogPostForm(data=request.POST)
        if form.is_valid():
            new_topic = form.save(commit=False)
            new_topic.owner = request.user
            new_topic.save()
            return redirect(reverse('blogs:topics'))

    context = {'form': form}
    return render(request, 'blogs/new_topic.html', context)


@login_required
def new_entry(request, topic_id):
    """Додає новий запис до певної теми"""
    topic = BlogPost.objects.get(id=topic_id)
    if request.method != 'POST':
        form = EntryForm()
    else:
        form = EntryForm(data=request.POST)
        if form.is_valid():
            new_entry_object = form.save(commit=False)
            new_entry_object.topic = topic
            new_entry_object.save()
            return redirect('blogs:topic', topic_id=topic_id)

    context = {'form': form, 'topic': topic, }
    return render(request, 'blogs/new_entry.html', context)


@login_required
def edit_entry(request, entry_id):
    """Редагує існуючий запис"""
    entry = Entry.objects.get(id=entry_id)
    topic = entry.topic
    if topic.owner != request.user:
        raise Http404

    if request.method != 'POST':
        form = EntryForm(instance=entry)
    else:
        form = EntryForm(instance=entry, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('blogs:topic', topic_id=topic.id)

    context = {
        'entry': entry,
        'topic': topic,
        'form': form,
    }
    return render(request, 'blogs/edit_entry.html', context)
