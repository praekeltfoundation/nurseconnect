import json

from django.forms import ValidationError
from django.contrib import messages
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.utils.translation import get_language_from_request
from django.utils.translation import ugettext_lazy as _
from django.views.generic import FormView
from django.views.generic import TemplateView
from django.views.generic import View
from django.http.request import QueryDict
from django.contrib.auth.tokens import default_token_generator

from molo.profiles.models import SecurityAnswer

from molo.core.models import ArticlePage
from molo.core.templatetags.core_tags import get_pages
from molo.core.utils import get_locale_code
from molo.profiles import models
from molo.surveys.models import MoloSurveyPage
from molo.profiles.views import ForgotPasswordView
from molo.profiles.models import UserProfilesSettings
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
        if user.is_authenticated():
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
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        if not User.objects.filter(username__iexact=username).exists():
            self.request.session["registered"] = False
            self.request.session["username"] = username
            self.request.session["password"] = password
            self.request.session["registration-step"] = 2
            url = reverse("user_register_security_questions")
            return HttpResponseRedirect(url)

        error = _("Username already exists.")
        form.add_error("username", ValidationError(error))
        return self.render_to_response({'form': form})


class RegistrationSecurityQuestionsView(FormView):
    form_class = forms.RegistrationSecurityQuestionsForm
    template_name = "registration/register_security_questions.html"

    def form_valid(self, form):
        answers = []

        for index, question in enumerate(self.questions):
            answer = form.cleaned_data.get("question_{}".format(index))
            if answer:
                answers.append({'question': question.pk, 'answer': answer})

        if self.request.user.is_authenticated():
            username = self.request.user.username
            user = User.objects.filter(username__iexact=username).first()
            for i in answers:
                models.SecurityAnswer.objects.create(suser=user.profile, **i)
            return HttpResponseRedirect(reverse("home"))

        answers = json.dumps({'items': answers})
        self.request.session["registration-step"] = 3
        self.request.session["security_questions"] = answers
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

    def get_context_data(self, **kwargs):
        context = super(
            RegistrationSecurityQuestionsView, self
        ).get_context_data()
        if self.request.user.is_authenticated():
            context["toggle_security_edit"] = True

        return context


class RegistrationClinicCodeView(FormView):
    form_class = forms.RegistrationClinicCodeForm
    template_name = "registration/register_clinic_code.html"

    def form_valid(self, form):
        clinic_name = None
        clinic_code = form.cleaned_data["clinic_code"]
        clinic = get_clinic_code(clinic_code)

        if not clinic:
            error = _("Clinic code does not exist.")
            form.add_error("clinic_code", ValidationError(error))
            return self.render_to_response({'form': form})
        else:
            if clinic[2]:
                clinic_name = clinic[2]

        username = self.request.session.get("username")
        password = self.request.session.get("password")
        user = User.objects.create_user(username=username, password=password)
        user.profile.site = self.request.site
        user.save()
        user.profile.save()

        # Security Questions
        answers = json.loads(self.request.session.get('security_questions'))
        for i in answers.get('items'):
            pk = i.get('question')
            question = models.SecurityQuestion.objects.live().get(pk=pk)
            i.update({'question': question})
            models.SecurityAnswer.objects.create(user=user.profile, **i)

        # Save clinic code
        user.profile.for_nurseconnect.clinic_code = clinic_code
        user.profile.for_nurseconnect.save()
        self.request.session["registration-step"] = 4
        self.request.session["clinic"] = True
        self.request.session["registered"] = True
        self.request.session["cliniccode"] = clinic_code
        self.request.session["cliniccodename"] = clinic_name
        url = reverse("user_register_clinic_code_success")
        return HttpResponseRedirect(url)


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
                    update_session_auth_hash(self.request, self.request.user)
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


class NCSurveySuccess(View):
    def get(self, request, *args, **kwargs):
        survey = get_object_or_404(MoloSurveyPage, slug=kwargs['slug'])
        if isinstance(survey.get_parent().specific, ArticlePage):
            article = survey.get_parent().specific
            return HttpResponseRedirect(
                "{}".format(article.get_url()))
        else:
            return render(request, "surveys/molo_survey_page_success.html")


class NCForgotPasswordView(ForgotPasswordView):
    """ Forgot Password """

    def form_valid(self, form):
        error_message = "The username and security question(s) combination " \
                        + "do not match."
        profile_settings = UserProfilesSettings.for_site(self.request.site)

        if "forgot_password_attempts" not in self.request.session:
            self.request.session["forgot_password_attempts"] = \
                profile_settings.password_recovery_retries

        # max retries exceeded
        if self.request.session["forgot_password_attempts"] <= 0:
            form.add_error(
                None, _("Too many attempts. Please try again later.")
            )
            return self.render_to_response({'form': form})

        username = form.cleaned_data["username"]
        try:

            user = User.objects.get(
                profile__migrated_username=username,
                profile__site=self.request.site)
            username = user.username
        except User.DoesNotExist:
            try:
                user = User.objects.get(
                    username=username, profile__site=self.request.site)
            except User.DoesNotExist:
                self.request.session['forgot_password_attempts'] += 1
                form.add_error('username',
                               _('The username that you entered appears to be '
                                 'invalid. Please try again.'))
                return self.render_to_response({'form': form})

        if not user.is_active:
            # add non_field_error
            form.add_error(None, _(error_message))
            self.request.session["forgot_password_attempts"] -= 1
            return self.render_to_response({'form': form})

        # check security question answers
        answer_checks = []

        if user.profile.security_question_answers.exists():
            for i in range(profile_settings.num_security_questions):
                user_answer = form.cleaned_data["question_%s" % (i,)]
                try:
                    saved_answer = user.profile.securityanswer_set.get(
                        user=user.profile,
                        question=self.security_questions[i]
                    )
                    answer_checks.append(
                        saved_answer.check_answer(user_answer))
                except SecurityAnswer.DoesNotExist:
                    form.add_error(
                        None,
                        _("There are no security questions "
                          "stored against your profile."))
                    return self.render_to_response({'form': form})

            # redirect to reset password page if username and security
            # questions were matched
            if all(answer_checks):
                token = default_token_generator.make_token(user)
                q = QueryDict(mutable=True)
                q["user"] = username
                q["token"] = token
                reset_password_url = "{0}?{1}".format(
                    reverse("molo.profiles:reset_password"), q.urlencode()
                )
                return HttpResponseRedirect(reset_password_url)
            else:
                form.add_error(None, _(error_message))
                self.request.session["forgot_password_attempts"] -= 1
                return self.render_to_response({'form': form})

        token = default_token_generator.make_token(user)
        q = QueryDict(mutable=True)
        q["user"] = username
        q["token"] = token
        reset_password_url = "{0}?{1}".format(
            reverse("molo.profiles:reset_password"), q.urlencode())
        return HttpResponseRedirect(reset_password_url)
