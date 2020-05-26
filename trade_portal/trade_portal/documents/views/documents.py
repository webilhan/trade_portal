from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin as Login, AccessMixin
from django.views.generic import (
    DetailView, ListView, CreateView, UpdateView,
)
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, Http404
from django.urls import reverse
from django.shortcuts import redirect

from trade_portal.documents.forms import (
    DocumentCreateForm, DocumentUpdateForm,
)
from trade_portal.documents.models import Document
from trade_portal.utils.monitoring import statsd_timer


class DocumentQuerysetMixin(AccessMixin):

    def get_queryset(self):
        qs = Document.objects.all()
        user = self.request.user

        # filter by the generic availability (can see)
        if not user.is_staff:
            qs = qs.filter(
                created_by_org__in=user.orgs
                # TODO: or available to the user's ABN
            )
        # filter by the current org
        qs = qs.filter(
            created_by_org=user.get_current_org(self.request.session)
        )
        return qs

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if not request.user.is_staff:
            if not request.user.orgs:
                messages.warning(
                    request,
                    "You are not a member of any organisation - which is "
                    "mandatory to access the documents page"
                )
                return redirect('users:detail')
        return super().dispatch(request, *args, **kwargs)


class DocumentListView(Login, DocumentQuerysetMixin, ListView):
    template_name = 'documents/list.html'
    model = Document

    @statsd_timer("view.DocumentListView.dispatch")
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class DocumentCreateView(Login, CreateView):
    template_name = 'documents/create.html'
    form_class = DocumentCreateForm

    @statsd_timer("view.DocumentCreateView.dispatch")
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        k = super().get_form_kwargs()
        k['user'] = self.request.user
        k['current_org'] = self.request.user.get_current_org(self.request.session)
        return k

    def get_success_url(self):
        messages.success(
            self.request,
            "The draft document has been created. You may continue filling it with"
            " the data now"
        )
        return reverse('documents:detail', args=[self.object.pk])


class DocumentUpdateView(Login, DocumentQuerysetMixin, UpdateView):
    template_name = 'documents/update.html'
    form_class = DocumentUpdateForm

    @statsd_timer("view.DocumentUpdateView.dispatch")
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        k = super().get_form_kwargs()
        k['user'] = self.request.user
        k['current_org'] = self.request.user.get_current_org(self.request.session)
        return k

    def get_success_url(self):
        messages.success(
            self.request,
            "The document has been updated"
        )
        return reverse('documents:detail', args=[self.object.pk])


class DocumentDetailView(Login, DetailView):
    template_name = 'documents/detail.html'
    model = Document

    def get_object(self):
        obj = super().get_object()
        obj._recalc_status()
        return obj

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        if 'lodge-document' in request.POST:
            if obj.status == Document.STATUS_COMPLETE:
                obj.lodge()
                messages.success(request, 'The document has been lodged')
                return redirect(obj.get_absolute_url())
        return redirect(request.path_info)


class DocumentFileDownloadView(Login, DocumentQuerysetMixin, DetailView):

    def get_object(self):
        try:
            c = self.get_queryset().get(pk=self.kwargs['pk'])
            doc = c.files.get(id=self.kwargs['file_pk'])
        except ObjectDoesNotExist:
            raise Http404()
        return doc

    def get(self, *args, **kwargs):
        # standard file approach
        document = self.get_object()
        response = HttpResponse(document.file, content_type='application/octet-stream')
        response['Content-Disposition'] = 'attachment; filename="%s"' % document.file.name
        return response
