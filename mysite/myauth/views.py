from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView,LogoutView
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import TemplateView, CreateView, DetailView, ListView, UpdateView
from myauth.forms import AvatarUploadForm
from myauth.models import Profile


# Create your views here.


class MyLogoutPage(View):
    def get(self, request):
        logout(request)
        return redirect('myauth:login')

def get_cookie_view(request):
    favorite_color = request.COOKIES.get('favorite_color', 'blue')
    return HttpResponse(f"Favorite color from cookies is: {favorite_color}")

def set_cookie_view(request):
    response = HttpResponse("Cookie set: favorite_color = green")
    response.set_cookie('favorite_color', 'green', max_age=3600)
    return response

def get_session_view(request):
    visit_count = request.session.get('visit_count', 0)
    return HttpResponse(f"Visit count from session: {visit_count}")

def set_session_view(request):
    request.session['visit_count'] = request.session.get('visit_count', 0) + 1
    return HttpResponse("Visit count updated in session.")

class AboutMeView(LoginRequiredMixin, View):
    template_name = "myauth/about-me.html"

    def get(self, request):
        form = AvatarUploadForm(instance=request.user.profile)
        return render(request, self.template_name, {
            'form': form
        })

    def post(self, request):
        form = AvatarUploadForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            return redirect('myauth:about-me')
        return render(request, self.template_name, {
            'form': form
        })

class UsersListView(ListView):
    model = User
    template_name = "myauth/users_list.html"
    context_object_name = "users"

class UserDetailView(DetailView):
    model = User
    template_name = "myauth/user_detail.html"
    context_object_name = "user_obj"

class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = "myauth/register.html"
    success_url = reverse_lazy("myauth:about-me")

    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.object

        Profile.objects.create(user=user)

        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')

        user = authenticate(
            self.request,
            username=username,
            password=password
        )
        login(request=self.request, user=user)
        return response

class AvatarUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    fields = ['avatar']
    template_name = "myauth/avatar_update.html"

    def dispatch(self, request, *args, **kwargs):
        profile = self.get_object()
        if request.user != profile.user and not request.user.is_staff:
            raise PermissionDenied("You are not allowed to edit this avatar.")
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('myauth:user-detail', kwargs={"pk": self.object.user.pk})


