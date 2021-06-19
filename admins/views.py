from django.shortcuts import render, HttpResponseRedirect
from django.contrib import messages
from django.urls import reverse
from admins.forms import UserAdminRegisterForm, UserAdminProfileForm
from django.contrib.auth.decorators import user_passes_test  # декоратор для обязательной авторизации
from users.models import User


# Create your views here.
# CRUD

# top page
@user_passes_test(lambda u: u.is_superuser)
def index(request):
    context = {'title': 'GeekShop - Admin'}
    return render(request, 'admins/admin.html', context)


# READ
@user_passes_test(lambda u: u.is_superuser)
def admin_users(request):
    context = {'title': 'GeekShop - Admin | Пользователи', 'users': User.objects.all()}
    return render(request, 'admins/admin-users-read.html', context)


# CREATE
@user_passes_test(lambda u: u.is_superuser)
def admin_users_create(request):
    if request.method == 'POST':
        form = UserAdminRegisterForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Регистрация прошла успешно!!')
            return HttpResponseRedirect(reverse('admins:admin_users'))
    else:
        form = UserAdminRegisterForm()

    context = {'title': 'GeekShop - Admin | Регистрация', 'form': form}
    return render(request, 'admins/admin-users-create.html', context)


# UPDATE
@user_passes_test(lambda u: u.is_superuser)
def admin_users_update(request, id_user=None):
    selected_user = User.objects.get(id=id_user)
    if request.method == 'POST':
        form = UserAdminProfileForm(data=request.POST, files=request.FILES, instance=selected_user)
        if form.is_valid():
            form.save()
            messages.success(request, f'Изменения данных пользователя "{selected_user}" успешно сохранены!!')
            return HttpResponseRedirect(reverse('admins:admin_users'))
    else:
        form = UserAdminProfileForm(instance=selected_user)

    context = {'title': 'GeekShop - Admin | Пользователь',
               'form': form,
               'selected_user': selected_user,
               }
    return render(request, 'admins/admin-users-update-delete.html', context)


# DELETE
@user_passes_test(lambda u: u.is_superuser)
def admin_users_delete(request, id_user):
    user = User.objects.get(id=id_user)
    user.is_active = False
    user.save()
    messages.success(request, f'Пользователь "{user}" успешно удален!!')
    return HttpResponseRedirect(reverse('admins:admin_users'))


@user_passes_test(lambda u: u.is_superuser)
def admin_users_recovery(request, id_user):
    user = User.objects.get(id=id_user)
    user.is_active = True
    user.save()
    messages.success(request, f'Пользователь "{user}" успешно Востановлен!!')
    return HttpResponseRedirect(reverse('admins:admin_users'))