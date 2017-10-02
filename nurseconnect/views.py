from django.forms import ValidationError
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
from molo.core.templatetags.core_tags import get_pages
from molo.core.utils import get_locale_code
from molo.profiles import models

from wagtail.wagtailsearch.models import Query

from nurseconnect import forms
from nurseconnect.services import get_clinic_code

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
    search_query = search_query.strip()

    if search_query:
        results = ArticlePage.objects.filter(
            languages__language__locale=locale
        ).values_list("pk", flat=True)
        # Elasticsearch backend doesn"t support filtering
        # on related fields, at the moment.
        # So we need to filter ArticlePage entries using DB,
        # then, we will be able to search
        results = ArticlePage.objects.filter(pk__in=results)
        results = results.live().search(search_query)
        # At the moment only ES backends have highlight API.
        if hasattr(results, "highlight"):
            results = results.highlight(
                fields={
                    "title": {},
                    "subtitle": {},
                    "body": {},
                },
                require_field_match=False
            )

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


class HomePageView(TemplateView):
    def get_context_data(self, **kwargs):
        context = super(HomePageView, self).get_context_data()
        user = self.request.user
        exists = user.profile.securityanswer_set.filter(
            user=user.profile).exists()
        if not exists:
            context["no_security_answers"] = True
        return context


class RegistrationCompleteView(TemplateView):
    def get(self, request, *args, **kwargs):
        request.session["registration-step"] = 0
        username = self.request.session["username"]
        password = self.request.session["password"]
        authed_user = authenticate(username=username, password=password)
        login(self.request, authed_user)

        return HttpResponseRedirect(reverse("home"))


class RegistrationView(TemplateView):
    def get(self, request, *args, **kwargs):
        if request.session.get("registration-step"):
            if request.session["registration-step"] == 1:
                return HttpResponseRedirect(
                    reverse("user_register_msisdn")
                )
            elif request.session["registration-step"] == 2:
                return HttpResponseRedirect(
                    reverse("user_register_security_questions")
                )
            elif request.session["registration-step"] == 3:
                return HttpResponseRedirect(
                    reverse("user_register_clinic_code")
                )
            elif request.session["registration-step"] == 4:
                return HttpResponseRedirect(
                    reverse("user_register_clinic_code_success")
                )

        return HttpResponseRedirect(reverse("user_register_msisdn"))


class RegistrationMSISDNView(FormView):
    form_class = forms.RegistrationMSISDNForm
    template_name = "registration/register_msisdn.html"

    def form_valid(self, form):
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password"]
        if User.objects.filter(
            username__iexact=username
        ).exists():
            form.add_error(
                "username",
                ValidationError(_("Username already exists."))
            )
            return self.render_to_response({'form': form})
        user = User.objects.create_user(
            username=username,
            password=password
        )
        user.save()
        user.profile.save()

        self.request.session["registration-step"] = 2
        self.request.session["username"] = username
        self.request.session["password"] = password
        self.request.session["registered"] = False

        return HttpResponseRedirect(
            reverse("user_register_security_questions")
        )


class RegistrationSecurityQuestionsView(FormView):
    form_class = forms.RegistrationSecurityQuestionsForm
    template_name = "registration/register_security_questions.html"

    def form_valid(self, form):
        username = self.request.session["username"]
        user = User.objects.filter(username__iexact=username).first()

        # Save security question answers
        for index, question in enumerate(
            self.questions
        ):
            answer = form.cleaned_data["question_%s" % index]
            models.SecurityAnswer.objects.create(
                user=user.profile,
                question=question,
                answer=answer
            )
        self.request.session["registration-step"] = 3
        return HttpResponseRedirect(reverse("user_register_clinic_code"))

    def get_form_kwargs(self):
        kwargs = super(
            RegistrationSecurityQuestionsView, self
        ).get_form_kwargs()
        self.questions = models.SecurityQuestion.objects.live().filter(
            languages__language__is_main_language=True)

        # create context dictionary with request for get_pages()
        request = {"request": self.request}
        translated_questions = get_pages(
            request, self.questions, self.request.LANGUAGE_CODE)
        kwargs["questions"] = translated_questions
        return kwargs


class RegistrationClinicCodeView(FormView):
    form_class = forms.RegistrationClinicCodeForm
    template_name = "registration/register_clinic_code.html"

    def form_valid(self, form):
        clinic_code = form.cleaned_data["clinic_code"]
        clinic = get_clinic_code(clinic_code)

        if not clinic:
            form.add_error(
                "clinic_code",
                ValidationError(_("Clinic code does not exist."))
            )
            return self.render_to_response({'form': form})
        else:
            if clinic[2]:
                clinic_name = clinic[2]

        username = self.request.session["username"]
        user = User.objects.filter(username__iexact=username).first()

        # Save clinic code
        user.profile.for_nurseconnect.clinic_code = clinic_code
        user.profile.for_nurseconnect.save()
        self.request.session["registration-step"] = 4
        self.request.session["clinic"] = True
        self.request.session["cliniccode"] = clinic_code
        self.request.session["cliniccodename"] = clinic_name

        return HttpResponseRedirect(
            reverse("user_register_clinic_code_success")
        )


class RegistrationClinicCodeSuccessView(TemplateView):
    template_name = "registration/register_clinic_code_success.html"


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
                first_name = settings_form.cleaned_data["first_name"]
                last_name = settings_form.cleaned_data["last_name"]
                username = settings_form.cleaned_data["username"]
                clinic_code = settings_form.cleaned_data["clinic_code"]
                if self.request.user.last_name != last_name or \
                        self.request.user.first_name != first_name:
                    messages.success(
                        request,
                        "Profile successfully updated."
                    )
                    self.request.user.first_name = first_name
                    self.request.user.last_name = last_name
                    self.request.user.save()

                if username and self.request.user.username != username:
                    messages.success(
                        request,
                        "Username successfully updated. "
                        "PLEASE NOTE: You will need to use your new "
                        "cellphone number to log in going forward."
                    )
                    self.request.user.username = username
                    self.request.user.save()
                else:
                    messages.success(
                        request,
                        "Your cellphone number has not changed."
                    )

                if clinic_code:
                    clinic = get_clinic_code(clinic_code)
                    if not clinic:
                        settings_form.add_error(
                            "clinic_code",
                            ValidationError(_("Clinic code does not exist."))
                        )
                        profile_password_change_form = \
                            forms.ProfilePasswordChangeForm(
                                prefix="profile_password_change_form"
                            )
                        settings_form.change_field_enabled_state(False)
                        return render(
                            request,
                            self.template_name,
                            context={
                                "edit": "edit-settings",
                                "settings_form": settings_form,
                                "profile_password_change_form":
                                    profile_password_change_form
                            }
                        )
                    else:
                        if clinic[2]:
                            self.request.session["clinic-name"] = clinic[2]
                        self.request.user.profile.for_nurseconnect.clinic_code\
                            = clinic[0]

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
                        "edit": "edit-settings",
                        "settings_form": settings_form,
                        "profile_password_change_form":
                            profile_password_change_form
                    }
                )

        elif edit == "edit-password":
            profile_password_change_form = forms.ProfilePasswordChangeForm(
                data=request.POST,
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
                        ValidationError("The old password is incorrect.")
                    )
                    settings_form = forms.EditProfileForm(
                        prefix="settings_form", user=self.request.user
                    )
                    profile_password_change_form.change_field_enabled_state(
                        False
                    )
                    return render(
                        request,
                        self.template_name,
                        context={
                            "edit": "edit-password",
                            "settings_form": settings_form,
                            "profile_password_change_form":
                                profile_password_change_form
                        }
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
                        "edit": "edit-password",
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
