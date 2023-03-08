from django.views.generic.base import TemplateView
from siteartifacts.models import AboutPage, PolicyPage, HelpPage, HelpItem, IndexPage
from django.views.generic.edit import FormView
from siteartifacts.forms import ContactForm



class PolicyView(TemplateView):
    template_name = 'policy.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['policy'] = PolicyPage.objects.last()
        return context

class AboutView(TemplateView):
    template_name='about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['about'] = AboutPage.objects.last()
        return context

class HelpView(TemplateView):
    template_name='help.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        help = HelpPage.objects.last()
        if help:
            helpitems = help.helpitems.all()
            context['help'] = help
            if helpitems:
                context['helpitems'] = helpitems
        return context

class ContactView(FormView):
    template_name = 'contact.html'
    form_class = ContactForm
    success_url = 'about'

    def form_valid(self, form):
        self.send_email(form.cleaned_data)
        return super().form_valid(form)

    def send_email(self, valid_data):
        print(valid_data)
        pass