import json

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)

from .forms import JokeForm
from .models import Joke, JokeVote

class JokeCreateView(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    model = Joke
    form_class = JokeForm
    success_message = 'Joke created.'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class JokeDeleteView(UserPassesTestMixin, DeleteView):
    model = Joke
    success_url = reverse_lazy('jokes:list')

    def delete(self, request, *args, **kwargs):
        result = super().delete(request, *args, **kwargs)
        messages.success(self.request, 'Joke deleted.')
        return result

    def test_func(self):
        obj = self.get_object()
        return self.request.user == obj.user
    

class JokeDetailView(DetailView):
    model = Joke

class JokeListView(ListView):
    model = Joke
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        order_fields, order_key, direction = self.get_order_settings()

        context['order'] = order_key
        context['direction'] = direction
        
        # get all but the last order key, which is 'default'
        context['order_fields'] = list(order_fields.keys())[:-1]

        return context
    
    def get_ordering(self):
        order_fields, order_key, direction = self.get_order_settings()
        
        ordering = order_fields[order_key]

        # if direction is 'desc' or is invalid use descending order
        if direction != 'asc':
            ordering = '-' + ordering

        return ordering

    def get_order_settings(self):
        order_fields = self.get_order_fields()
        default_order_key = order_fields['default_key']
        order_key = self.request.GET.get('order', default_order_key)
        direction = self.request.GET.get('direction', 'desc')
        
        # If order_key is invalid, use default
        if order_key not in order_fields:
            order_key = default_order_key

        return (order_fields, order_key, direction)

    
    def get_order_fields(self):
        # Returns a dict mapping friendly names to field names and lookups.
        return {
            'joke': 'question',
            'category': 'category__category',
            'creator': 'user__username',
            'created': 'created',
            'updated': 'updated',
            'default_key': 'updated'
        }


class JokeUpdateView(SuccessMessageMixin, UserPassesTestMixin, UpdateView):
    model = Joke
    form_class = JokeForm
    success_message = 'Joke updated.'

    def test_func(self):
        obj = self.get_object()
        return self.request.user == obj.user


def vote(request, slug):
    user = request.user # The logged-in user (or AnonymousUser).
    joke = Joke.objects.get(slug=slug) # The joke instance.
    data = json.loads(request.body) # Data from the JavaScript.

    # Set simple variables.
    vote = data['vote'] # The user's new vote.
    likes = data['likes'] # The number of likes currently displayed on page.
    dislikes = data['dislikes'] # The number of dislikes currently displayed.

    if user.is_anonymous: # User not logged in. Can't vote.
        msg = 'Sorry, you have to be logged in to vote.'
    else: # User is logged in.
        if JokeVote.objects.filter(user=user, joke=joke).exists():
            # User already voted. Get user's past vote:
            joke_vote = JokeVote.objects.get(user=user, joke=joke)

            if joke_vote.vote == vote: # User's new vote is the same as old vote.
                msg = 'Right. You told us already. Geez.'
            else: # User changed vote.
                joke_vote.vote = vote # Update JokeVote instance.
                joke_vote.save() # Save.

                # Set data to return to the browser.
                if vote == -1:
                    likes -= 1
                    dislikes += 1
                    msg = "Don't like it after all, huh? OK. Noted."
                else:
                    likes += 1
                    dislikes -= 1
                    msg = 'Grown on you, has it? OK. Noted.'
        else: # First time user is voting on this joke.
            # Create and save new vote.
            joke_vote = JokeVote(user=user, joke=joke, vote=vote)
            joke_vote.save()

            # Set data to return to the browser.
            if vote == -1:
                dislikes += 1
                msg = "Sorry you didn't like the joke."
            else:
                likes += 1
                msg = "Yeah, good one, right?"

    # Create object to return to browser.
    response = {
        'msg': msg,
        'likes': likes,
        'dislikes': dislikes
    }
    return JsonResponse(response) # Return object as JSON.