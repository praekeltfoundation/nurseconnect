from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.translation import get_language_from_request
from django.utils.translation import ugettext_lazy as _
from django.views.generic import FormView
from django.views.generic import TemplateView
from django.views.generic import View

from molo.core.models import ArticlePage
from molo.core.utils import get_locale_code
from molo.profiles import models

from wagtail.wagtailsearch.models import Query

from nurseconnect import forms
from nurseconnect.models import UserProfile

REDIRECT_FIELD_NAME = 'next'
INT_PREFIX = "+27"


class SearchView(TemplateView):
    def get_context_data(self, **kwargs):
        context = super(SearchView, self).get_context_data(**kwargs)
        context["searched"] = False
        context["active"] = "search"
        return context


def search(request, results_per_page=7):
    search_query = request.GET.get("q", None)
    page = request.GET.get("p", 1)
    locale = get_locale_code(get_language_from_request(request))
    if search_query:
        results = ArticlePage.objects.filter(
            languages__language__locale=locale).live().search(search_query)
        Query.get(search_query).add_hit()
    else:
        results = ArticlePage.objects.none()

    paginator = Paginator(results, results_per_page)
    try:
        search_results = paginator.page(page)
    except PageNotAnInteger:
        search_results = paginator.page(1)
    except EmptyPage:
        search_results = paginator.page(paginator.num_pages)

    return render(request, "search/search.html", {
        "active": "search",
        "searched": True,
        "search_query": search_query,
        "search_results": search_results,
        "results": results,
    })


class RegistrationView(FormView):
    """
    Handles user registration
    """
    form_class = forms.RegistrationForm
    template_name = "profiles/register.html"

    def form_valid(self, form):
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password"]
        clinic_code = form.cleaned_data["clinic_code"]

        user = User.objects.create_user(
            username=username,
            password=password
        )
        user.save()
        user.profile.save()

        # Save security question answers
        for index, question in enumerate(
            models.SecurityQuestion.objects.all()
        ):
            answer = form.cleaned_data["question_%s" % index]
            models.SecurityAnswer.objects.create(
                user=user.profile,
                question=question,
                answer=answer
            )

        # Save clinic code
        user.profile.for_nurseconnect.clinic_code = clinic_code
        user.profile.for_nurseconnect.save()

        authed_user = authenticate(username=username, password=password)
        login(self.request, authed_user)
        return HttpResponseRedirect(reverse("home"))

    def get_form_kwargs(self):
        kwargs = super(RegistrationView, self).get_form_kwargs()
        kwargs["questions"] = models.SecurityQuestion.objects.all()
        return kwargs


class MyProfileView(View):
    template_name = "profiles/viewprofile.html"

    def get(self, request, *args, **kwargs):
        settings_form = forms.EditProfileForm(
            prefix="settings_form", user=self.request.user
        )
        edit = ""
        profile_password_change_form = forms.ProfilePasswordChangeForm(
            prefix="profile_password_change_form"
        )
        if kwargs.get("edit") == "edit-settings":
            settings_form.change_field_enabled_state(state=False)
            edit = "edit-settings"
        elif kwargs.get("edit") == "edit-password":
            profile_password_change_form.change_field_enabled_state(
                state=False)
            edit = "edit-password"

        context = {
            "edit": edit,
            "settings_form": settings_form,
            "profile_password_change_form": profile_password_change_form,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        edit = kwargs.get("edit")
        if edit == "edit-settings":
            settings_form = forms.EditProfileForm(
                request.POST,
                prefix="settings_form",
                user=request.user
            )
            if settings_form.is_valid():
                if self.request.user.first_name != \
                        settings_form.cleaned_data["first_name"]:
                    messages.success(
                        request,
                        "First name successfully updated!"
                    )
                self.request.user.first_name = \
                    settings_form.cleaned_data["first_name"]
                if self.request.user.last_name != \
                        settings_form.cleaned_data["last_name"]:
                    messages.success(
                        request,
                        "Last name successfully updated!"
                    )
                self.request.user.last_name = \
                    settings_form.cleaned_data["last_name"]
                if settings_form.cleaned_data["username"]:
                    if self.request.user.username != \
                            settings_form.cleaned_data["username"]:
                        messages.success(
                            request,
                            "Username successfully updated!"
                            " "
                            "PLEASE NOTE: You will need to use your new "
                            "cellphone number to log in going forward."
                        )
                    self.request.user.username = \
                        settings_form.cleaned_data["username"]
                self.request.user.save()
                return HttpResponseRedirect(reverse("view_my_profile"))
            else:
                profile_password_change_form = forms.ProfilePasswordChangeForm(
                    prefix="profile_password_change_form"
                )
                settings_form.change_field_enabled_state(False)
                return render(
                    request,
                    self.template_name,
                    context={
                        "settings_form": settings_form,
                        "profile_password_change_form":
                            profile_password_change_form
                    }
                )

        elif edit == "edit-password":
            profile_password_change_form = forms.ProfilePasswordChangeForm(
                request.POST,
                prefix="profile_password_change_form"
            )
            if profile_password_change_form.is_valid():
                if self.request.user.check_password(
                    profile_password_change_form.cleaned_data[
                        "old_password"
                    ]
                ):
                    self.request.user.set_password(
                        profile_password_change_form.cleaned_data[
                            "new_password"
                        ]
                    )
                    messages.success(
                        request,
                        "Password successfully changed!"
                    )

                    self.request.user.save()
                    return HttpResponseRedirect(reverse("view_my_profile"))
                else:
                    profile_password_change_form.add_error(
                        "old_password",
                        _("The old password is incorrect.")
                    )
            else:
                settings_form = forms.EditProfileForm(
                    prefix="settings_form", user=self.request.user
                )
                profile_password_change_form.change_field_enabled_state(False)
                return render(
                    request,
                    self.template_name,
                    context={
                        "settings_form": settings_form,
                        "profile_password_change_form":
                            profile_password_change_form
                    }
                )


class MenuView(TemplateView):
    template_name = "core/menu.html"

    def get_context_data(self, **kwargs):
        context = super(MenuView, self).get_context_data(**kwargs)
        context["active"] = "menu"
        return context
