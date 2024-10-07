from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy

class CustomLoginView(LoginView):
    template_name = 'login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        # Usa el espacio de nombres aquí
        return reverse_lazy('dashboard:dashboard')

    def get_template_names(self):
        print("Looking for template in:", self.template_name)
        return [self.template_name]

