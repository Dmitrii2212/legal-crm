from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from .forms import ClientForm
from .models import Client


class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    paginate_by = 25

    def get_queryset(self):
        clients = super().get_queryset()
        self.search = self.request.GET.get("q", "").strip()
        self.client_type = self.request.GET.get("type", "")

        if self.search:
            clients = clients.filter(
                Q(full_name__icontains=self.search)
                | Q(tax_id__icontains=self.search)
                | Q(registration_number__icontains=self.search)
                | Q(phone__icontains=self.search)
                | Q(email__icontains=self.search)
                | Q(contact_name__icontains=self.search)
            )
        if self.client_type in Client.Type.values:
            clients = clients.filter(client_type=self.client_type)

        return clients

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            search=self.search,
            selected_type=self.client_type,
            client_types=Client.Type.choices,
            **kwargs,
        )


class ClientDetailView(LoginRequiredMixin, DetailView):
    model = Client


class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm


class ClientUpdateView(LoginRequiredMixin, UpdateView):
    model = Client
    form_class = ClientForm
