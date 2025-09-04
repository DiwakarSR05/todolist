from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.http import JsonResponse
from django.utils import timezone
from django.contrib import messages
from .models import Task, Category, UserProfile
from .forms import TaskForm, CategoryForm, CustomUserCreationForm, UserUpdateForm, ProfileUpdateForm
from django.utils import timezone
from django.db.models import Q, Count, Case, When, IntegerField
import os

@login_required
def profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(
            request.POST, 
            request.FILES, 
            instance=request.user.userprofile
        )
        
        if user_form.is_valid() and profile_form.is_valid():
            # Handle profile picture removal
            if profile_form.cleaned_data.get('remove_picture'):
                if request.user.userprofile.profile_picture:
                    # Delete the file
                    if os.path.isfile(request.user.userprofile.profile_picture.path):
                        os.remove(request.user.userprofile.profile_picture.path)
                    # Clear the field
                    request.user.userprofile.profile_picture = None
            
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.userprofile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    
    return render(request, 'todo_app/profile.html', context)

@login_required
def profile_view(request):
    return render(request, 'todo_app/profile_view.html')

class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    context_object_name = 'tasks'
    template_name = 'todo_app/task_list.html'
    
    def get_queryset(self):
        # Get all tasks for the current user
        tasks = Task.objects.filter(user=self.request.user)
        
        # Apply filters
        filter_type = self.request.GET.get('filter', 'all')
        
        if filter_type == 'active':
            tasks = tasks.filter(completed=False)
        elif filter_type == 'completed':
            tasks = tasks.filter(completed=True)
        elif filter_type == 'overdue':
            tasks = tasks.filter(
                completed=False, 
                due_date__lt=timezone.now()
            )
        
        return tasks.order_by('-created_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all tasks for stats calculation
        all_tasks = Task.objects.filter(user=self.request.user)
        
        # Calculate stats CORRECTLY
        total_tasks = all_tasks.count()
        completed_tasks = all_tasks.filter(completed=True).count()
        overdue_tasks = all_tasks.filter(
            completed=False, 
            due_date__lt=timezone.now()
        ).count()
        active_tasks = total_tasks - completed_tasks  # This is the correct calculation
        
        # Add stats to context
        context['total_tasks'] = total_tasks
        context['completed_tasks'] = completed_tasks
        context['overdue_tasks'] = overdue_tasks
        context['active_tasks'] = active_tasks  # Add active tasks count
        context['completion_rate'] = round(
            (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 
            2
        )
        
        # Add categories to context
        context['categories'] = Category.objects.filter(user=self.request.user)
        # Add filter option
        context['filter'] = self.request.GET.get('filter', 'all')
        
        return context
    
@login_required
def dashboard(request):
    tasks = Task.objects.filter(user=request.user)
    total_tasks = tasks.count()
    completed_tasks = tasks.filter(completed=True).count()
    overdue_tasks = tasks.filter(
        completed=False, 
        due_date__lt=timezone.now()
    ).count()
    active_tasks = total_tasks - completed_tasks  # Add this line
    
    context = {
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'overdue_tasks': overdue_tasks,
        'active_tasks': active_tasks,  # Add this line
        'completion_rate': round(
            (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 
            2
        ),
        'tasks': tasks.order_by('-created_date')[:5]  # Recent tasks for dashboard
    }
    
    return render(request, 'todo_app/dashboard.html', context)

class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'todo_app/task_form.html'
    success_url = '/'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Task created successfully!')
        return super().form_valid(form)

class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'todo_app/task_form.html'
    success_url = '/'
    
    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        messages.success(self.request, 'Task updated successfully!')
        return super().form_valid(form)

class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    template_name = 'todo_app/task_confirm_delete.html'
    success_url = '/'
    
    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Task deleted successfully!')
        return super().delete(request, *args, **kwargs)

@login_required
def toggle_task_completion(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    task.completed = not task.completed
    task.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'completed': task.completed})
    
    return redirect('task_list')

@login_required
def quick_add_task(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        title = request.POST.get('title')
        if title:
            task = Task.objects.create(
                user=request.user,
                title=title,
                created_date=timezone.now()
            )
            return JsonResponse({
                'status': 'success', 
                'task_id': task.id,
                'task_title': task.title
            })
    return JsonResponse({'status': 'error'})

class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'todo_app/category_form.html'
    success_url = '/'
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Category created successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(user=self.request.user)
        return context

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Log the user in after registration
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Account created successfully!')
                return redirect('task_list')
    else:
        form = CustomUserCreationForm()
    return render(request, 'todo_app/register.html', {'form': form})

# In views.py
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Basic validation
        if not username or not password:
            messages.error(request, 'Please provide both username and password.')
            return render(request, 'todo_app/login.html')
        
        try:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Logged in successfully!')
                
                # Log login activity (optional)
                print(f"User {username} logged in successfully at {timezone.now()}")
                
                return redirect('task_list')
            else:
                messages.error(request, 'Invalid username or password.')
        except Exception as e:
            messages.error(request, f'Login error: {str(e)}')
    
    return render(request, 'todo_app/login.html')

@login_required
def user_logout(request):
    from django.contrib.auth import logout
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('login')

