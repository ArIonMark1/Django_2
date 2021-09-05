from django.conf import settings
from django.contrib import auth, messages
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.mail import send_mail
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import render

from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from django.views.generic.edit import CreateView, UpdateView, FormView
from users.forms import UserLoginForm, UserRegistrationForm, UserProfileForm, ShopUserProfileEditForm

from baskets.models import Basket
from users.models import User, ShopUserProfile


# Create your views here.

# ====================== CLASS LOGIN ============================
class LoginUsersView(LoginView):
    template_name = 'login.html'
    form_class = UserLoginForm

    def get_context_data(self, **kwargs):
        context = super(LoginUsersView, self).get_context_data(**kwargs)
        context['title'] = 'GeekShop Authorization'
        return context


# ===============================================================
# ==================== CLASS REGISTER ===========================

class UserCreateView(SuccessMessageMixin, CreateView, FormView):
    model = User
    form_class = UserRegistrationForm
    template_name = 'register.html'
    success_url = reverse_lazy('users:login')
    success_message = 'Registration Completed Successfully!!!'

    def form_valid(self, form):
        if form.is_valid():
            user = form.save()

            if send_verify_link(user):
                print('сообщение подтверждения отправленно')
                return HttpResponseRedirect(reverse('users:login'))
            else:
                print('ошибка отправки!!')
                return HttpResponseRedirect(reverse('users:login'))
        else:
            form = UserCreateView.form_class()

        return super(UserCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(UserCreateView, self).get_context_data(**kwargs)

        context['title'] = 'GeekShop Registration'
        return context


# ===============================================================
# ===================== CLASS PROFILE ===========================

# class UserProfileView(SuccessMessageMixin, UpdateView):
#     model = User
#     form_class = UserProfileForm
#     template_name = 'profile.html'
#     success_url = reverse_lazy('users:profile')
#     success_message = 'Your profile has been changed'
#
#     def get_success_url(self):
#         return reverse_lazy('users:profile', args=(self.object.id,))
#
#     def get_context_data(self, **kwargs):
#         context = super(UserProfileView, self).get_context_data(**kwargs)
#
#         if self.request.method == 'POST':
#             user = self.request.user
#             profile = ShopUserProfile.objects.get(user=user)
#
#             user_form = UserProfileForm(instance=user, data=self.request.POST, files=self.request.FILES)
#             profile_form = ShopUserProfileEditForm(instance=user.shopuserprofile, data=self.request.POST)
#
#             if user_form.is_valid() and profile_form.is_valid():
#                 user_form.save()
#                 messages.success(self.request, 'Данные изменены!!')
#         else:
#             user = self.request.user
#             # profile = ShopUserProfile.objects.get(user=user)
#
#             user_form = UserProfileForm(instance=user)
#             profile_form = ShopUserProfileEditForm(instance=user.shopuserprofile)
#
#         context['baskets'] = Basket.objects.filter(user=self.object)
#         context['form'] = user_form, profile_form,
#         return context
#
#     @method_decorator(login_required)
#     def dispatch(self, request, *args, **kwargs):
#         return super(UserProfileView, self).dispatch(request, *args, **kwargs)


# ===============================================================


def profile(request):
    user = request.user
    if request.method == 'POST':
        user_form = UserProfileForm(data=request.POST, instance=user, files=request.FILES)
    #     form = UserProfileForm(instance=user, data=request.POST, files=request.FILES)
        profile_form = ShopUserProfileEditForm(instance=user.shopuserprofile, data=request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            messages.success(request, 'Данные изменены!!')
            return HttpResponseRedirect(reverse('users:profile'))
    else:
        user_form = UserProfileForm(instance=user)
        profile_form = ShopUserProfileEditForm(instance=user.shopuserprofile)

    context = {'title': 'GeekShop - Профиль',
               'user_form': user_form,
               'profile_form': profile_form,
               'baskets': Basket.objects.filter(user=user),
               }
    return render(request, 'profile.html', context)


# ===============================================================
# ====================== CLASS LOGOUT ===========================
# ------- second variant logout -------

class LogoutUserView(LogoutView):
    pass


# ===============================================================
# ========================= verify link =========================

def verify(request, email, activation_key):
    user = User.objects.filter(email=email).first()
    if user:
        if user.activation_key == activation_key and not user.is_activation_key_expired():
            user.is_active = True
            user.save()
            auth.login(request, user, backend='django.contrib.auth.backends.ModelBackend')

    return render(request, 'verify.html')


def send_verify_link(user):
    subject = 'Verify your account'
    link = reverse('users:verify', args=[user.email, user.activation_key])
    message = f'{settings.DOMAIN}{link}'
    return send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email], fail_silently=False)

# ====================================


# @transaction.atomic
# def edit(request):
#     title = 'редактирование'
#     if request.method == 'POST':
#         edit_form = UserRegistrationForm(request.POST, request.FILES, instance=request.user)
#         profile_form = ShopUserProfileEditForm(request.POST, instance=request.user.shopuserprofile)
#         if edit_form.is_valid() and profile_form.is_valid():
#             edit_form.save()
#             return HttpResponseRedirect(reverse('users:profile'))
#         else:
#             edit_form = UserRegistrationForm(instance=request.user)
#             profile_form = ShopUserProfileEditForm(instance=request.user.shopuserprofile)
#
#         content = {'title': title, 'edit_form': edit_form, 'profile_form': profile_form,
#                    'media_url': settings.MEDIA_URL}
#         return render(request, 'profile.html', content)

# ------- login function -------
# ------------------------------
# def login(request):
#     if request.method == 'POST':
#         form = UserLoginForm(data=request.POST)
#
#         if form.is_valid():
#             username = request.POST['username']
#             password = request.POST['password']
#             user = auth.authenticate(username=username, password=password)  # сверяем с базой, есть ли такой юзер
#
#             if user and user.is_active:
#                 auth.login(request, user)
#
#                 return HttpResponseRedirect(reverse('index'))
#     else:
#         form = UserLoginForm()
#
#     context = {'title': 'GeekShop Авторизация', 'form': form}
#     return render(request, 'login.html', context)

# ===============================================================
# ------- profile function -------
# --------------------------------

# @login_required
# def profile(request):
#     user = request.user
#     if request.method == 'POST':
#         form = UserProfileForm(data=request.POST, instance=user, files=request.FILES)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Данные изменены!!')
#             return HttpResponseRedirect(reverse('users:profile'))
#     else:
#         form = UserProfileForm(instance=user)
#
#     context = {'title': 'GeekShop - Профиль',
#                'form': form,
#                'baskets': Basket.objects.filter(user=user),
#                }
#     return render(request, 'profile.html', context)

# ====================================
# ------- first variant logout -------

# class LogoutUserView(View):
#     def get(self, request):
#         auth.logout(request)
#         return HttpResponseRedirect(reverse('index'))

# ------- functional variant logout -------
# def logout(request):
#     auth.logout(request)
#     return HttpResponseRedirect(reverse('index'))
