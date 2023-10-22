from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.http import HttpResponse
from .forms import TaskForm
from .models import Task
from django.utils import timezone
from django.contrib.auth.decorators import login_required

# Create your views here.


def home(request):
    return render(request, 'home.html')


def singup(request):
    if request.method == 'GET':
        return render(request, 'singup.html',
                      {
                          'form': UserCreationForm
                      })
    else:
        if request.POST['password1'] == request.POST['password2']:
            # register user
            try:
                user = User.objects.create_user(
                    username=request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('tasks')
            except:
                return render(request, 'singup.html',
                              {
                                  'form': UserCreationForm,
                                  'error': 'Error: El usuario ya existe'
                              })
        else:
            return render(request, 'singup.html',
                          {
                              'form': UserCreationForm,
                              'error': 'Error: Las contraseñas no son iguales '
                          })

@login_required

def tasks(request):
        task = Task.objects.filter(user=request.user, fecha_completada__isnull=True)
        return render(request, 'tasks.html', {'tareas':task})

@login_required
def tasks_completed(request):
        task = Task.objects.filter(user=request.user, fecha_completada__isnull=False)
        return render(request, 'tasks.html', {'tareas':task})

@login_required
def task_detail(request, task_id):
    if request.method == 'GET':
        task = get_object_or_404(Task, pk=task_id, user=request.user)
        form = TaskForm(instance=task)
        return render(request, 'task_details.html', {'task':task, 'form':form})
    else:
        try:
            task = get_object_or_404(Task, pk=task_id)
            form = TaskForm(request.POST, instance=task)
            form.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'task_details.html', {'task':task, 'form':form, 'error':'Error al actualizar los datos'})
   

@login_required
def create_task(request):
    if request.method == 'GET':
        return render(request, 'create_task.html', {'form': TaskForm})
    else:
        try:
            form = TaskForm(request.POST)
            new_task = form.save(commit=False)
            new_task.user = request.user
            new_task.save()
            return redirect('tasks')
        except:
            return render(request, 'create_task.html', {'form': TaskForm, 'error':'Por favor ingresa datos validos o verfica que estes logiado'})

@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.fecha_completada = timezone.now()
        task.save()
        return redirect('tasks')

@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('tasks')


def singout(request):
    logout(request)
    return redirect('home')


def singin(request):

    if request.method == 'GET':
        return render(request, 'login.html', {'form': AuthenticationForm})
    else:
        user = authenticate(
            request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'login.html', {'form': AuthenticationForm, 'error': 'El ususario o contrasenia es incorrecta'})
        else:
            login(request, user)
            return redirect('tasks')
