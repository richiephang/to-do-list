from asyncio import Task
from audioop import reverse
from itertools import count
from statistics import mode
from django.shortcuts import render, redirect
# from django.http import HttpResponseRedirect
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy #reverse page for user
from .models import Task

from django.contrib.auth.views import LoginView # user login 
from django.contrib.auth.mixins import LoginRequiredMixin # to ensure user log in before enter any page
from django.contrib.auth.forms import UserCreationForm # register
from django.contrib.auth import login # directly logged in user after they register


# from .models import TodoItem
# # Create your views here.
# def todoView(request):
#     all_todo_items = TodoItem.objects.all()
#     return render(request, 'todo.html',
#     {'all_items': all_todo_items})

# def addTodo(request):
    
#     new_item = TodoItem(content = request.POST['content'])
#     new_item.save()
#     return HttpResponseRedirect('/todolist/')
#     # create a new todo all_items
#     #  save
#     #  redirect the browser to '/todolist/'

# def deleteTodo(request, todo_id):
#     item_to_delete = TodoItem.objects.get(id = todo_id)
#     item_to_delete.delete()
#     return HttpResponseRedirect('/todolist/')

class CustomLoginView(LoginView):
    template_name = 'todolist/login.html'
    fields = '__all__'
    redirect_authenticated_user = True #prevent logged in user at this page

    def get_success_url(self):
        return reverse_lazy('tasks')

class RegisterPage(FormView):
    template_name = 'todolist/register.html'
    form_class = UserCreationForm #built in user creation form by django, register doesn't do it automatically like login
    redirect_authenticated_user = True # not working here
    success_url = reverse_lazy('tasks')

    def form_valid(self, form):
        user = form.save() # return user because form use userCreationForm 
        if user is not None: # if user success created
            login(self.request, user) #direct login
        return super(RegisterPage, self).form_valid(form)

    def get(self, *args, **kwargs): # do it manually, prevent logged in user enter this page
        if self.request.user.is_authenticated:
            return redirect('tasks')
        return super(RegisterPage, self).get(*args, **kwargs)

class TaskList(LoginRequiredMixin, ListView):
    model = Task
    context_object_name = 'task_list'

    def get_context_data(self, **kwargs): # to show the data belong to that user only
        context = super().get_context_data(**kwargs)
        context['task_list'] = context['task_list'].filter(user=self.request.user)
        context['count'] = context['task_list'].filter(complete=False).count()
        
        search_input = self.request.GET.get('search-area') or ''
        if search_input:
            context['task_list'] = context['task_list'].filter(
                title__icontains=search_input)
        context['search_input'] = search_input # to make search text remain in box
        return context

class TaskDetail(LoginRequiredMixin, DetailView):
    model = Task
    context_object_name = 'task_detail'

class TaskCreate(LoginRequiredMixin, CreateView):
    model = Task
    fields = ['title','description','complete']
    success_url = reverse_lazy('tasks')
    #default template is task_form.html  modelname_form.html
    #template_name = 'todolist/xxx.html'   << chg template name
    def form_valid(self, form):  # to ensure the data created under the user 
        form.instance.user = self.request.user
        return super(TaskCreate, self).form_valid(form)

class TaskUpdate(LoginRequiredMixin, UpdateView):
    model = Task
    fields = ['title','description','complete']
    success_url = reverse_lazy('tasks')
    #default template is task_form.html  modelname_form.html


class DeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    context_object_name = 'task_detail'
    success_url = reverse_lazy('tasks')
