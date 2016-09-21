import random

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.http import HttpResponseForbidden
from django.http import HttpResponseRedirect
from django.http import QueryDict
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

        user = User.objects.create_user(
            username=username,
            password=password
        )
        user.save()
        # TODO: save security questions
        for index, question in enumerate(
            models.SecurityQuestion.objects.all()
        ):
            answer = form.cleaned_data["question_%s" % index]
            models.SecurityAnswer.objects.create(
                user=user.profile,
                question=question,
                answer=answer
            )
        authed_user = authenticate(username=username, password=password)
        login(self.request, authed_user)
        return HttpResponseRedirect(reverse("home"))

    def render_to_response(self, context, **response_kwargs):
        return super(RegistrationView, self).render_to_response(
            context, **response_kwargs
        )

    def get_form_kwargs(self):
        kwargs = super(RegistrationView, self).get_form_kwargs()
        kwargs["questions"] = models.SecurityQuestion.objects.all()
        return kwargs


# def two_form_view(request):
#     context = {}
#     if request.method == "POST":
#         question_form = QuestionForm(request.POST)
#         answer_form = AnswerForm(request.POST)
#         success = False
#         if 'q_button' in request.POST and question_form.is_valid()
#             question_form.save()
#             success = Treu
#         if 'a_button' in request.POST and answer_form.is_valid()
#             answer_form.save()
#             success = True
#         if success:
#             return HttpResponse(reverse('success'))
#     else:
#         question_form = QuestionForm(request.POST)
#         answer_form = AnswerForm(request.POST)
#
#     context['answer_form'] = answer_form
#     context['question_form'] = question_form
#     return render(request, 'forms.html', context)
#
# def success(request):
#     return render(request, 'success.html', {})


class MyProfileView(View):
    template_name = "profiles/viewprofile.html"

    def get(self, request, *args, **kwargs):
        settings_form = forms.EditProfileForm(
            prefix="settings_form", user=request.user
        )
        # settings_form.set_initial()
        profile_password_change_form = forms.ProfilePasswordChangeForm(
            prefix="profile_password_change_form"
        )
        edit = ""
        if kwargs.get("edit") == "edit-settings":
            settings_form.change_field_enabled_state(state=False)
            edit = "edit-settings"
        elif kwargs.get("edit") == "edit-password":
            profile_password_change_form.change_field_enabled_state(
                state=False)
            edit = "edit-password"

        context = {
            "edit": edit,
            "active": "profile",  # TODO: questionable - remove later
            "settings_form": settings_form,
            "profile_password_change_form": profile_password_change_form,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        edit = kwargs.get("edit")
        settings_form = forms.EditProfileForm(
            request.POST,
            prefix="settings_form",
            user=request.user
        )
        profile_password_change_form = forms.ProfilePasswordChangeForm(
            request.POST,
            prefix="profile_password_change_form"
        )
        if edit == "edit-settings":
            settings_form.full_clean()
            if settings_form.is_valid():
                self.request.user.first_name = \
                    settings_form.cleaned_data["first_name"]
                self.request.user.last_name = \
                    settings_form.cleaned_data["last_name"]
                if settings_form.cleaned_data["username"]:
                    self.request.user.username = \
                        settings_form.cleaned_data["username"]
                self.request.user.save()
                # import pdb; pdb.set_trace()

                return HttpResponseRedirect(reverse("view_my_profile"))

        elif edit == "edit-password":
            profile_password_change_form.full_clean()
            if profile_password_change_form.is_valid():
                user = self.request.user
                if user.check_password(
                    profile_password_change_form.cleaned_data[
                        "old_password"
                    ]
                ):
                    user.set_password(
                        profile_password_change_form.cleaned_data[
                            "new_password"
                        ]
                    )
                    user.save()
                    return HttpResponseRedirect(reverse("view_my_profile"))
                else:
                    profile_password_change_form.add_error(
                        "old_password",
                        _("The old password is incorrect.")
                    )

        return render(
            self.request,
            self.template_name,
            context={
                "settings_form": settings_form,
                "profile_password_change_form": profile_password_change_form
            }
        )


class ForgotPasswordView(FormView):
    form_class = forms.ForgotPasswordForm
    template_name = "profiles/forgot_password.html"

    def form_valid(self, form):
        error_message = "The username and security question(s) combination " \
                        + "do not match."
        profile_settings = models.UserProfilesSettings.for_site(
            self.request.site
        )

        if "forgot_password_attempts" not in self.request.session:
            self.request.session["forgot_password_attempts"] = \
                profile_settings.password_recovery_retries

        # max retries exceeded
        # TODO: a "time-limited" lockout was requested when this is the case
        if self.request.session["forgot_password_attempts"] <= 0:
            form.add_error(
                None,
                _("Too many attempts. Please try again later.")
            )
            return self.render_to_response({'form': form})

        username = form.cleaned_data["username"]
        try:
            user = User.objects.get_by_natural_key(username)
        except User.DoesNotExist:
            # add non_field_error
            form.add_error(None, _(error_message))
            self.request.session["forgot_password_attempts"] -= 1
            return self.render_to_response({'form': form})

        if not user.is_active:
            # add non_field_error
            form.add_error(None, _(error_message))
            self.request.session["forgot_password_attempts"] -= 1
            return self.render_to_response({'form': form})

        # check security question answers
        # TODO: fix indexes - num_security_questions should not
        # exceed object.all(). This will resolve possible AttributeErrors
        # when some question indexes don't exist
        answer_checks = []
        for i in range(profile_settings.num_security_questions):
            user_answer = form.cleaned_data["question_%s" % (i,)]
            saved_answer = user.profile.securityanswer_set.get(
                user=user.profile,
                question=self.security_questions[i]
            )
            answer_checks.append(
                saved_answer.check_answer(user_answer)
            )

        # redirect to reset password page if username and security
        # questions were matched
        if all(answer_checks):
            token = default_token_generator.make_token(user)
            q = QueryDict(mutable=True)
            q["user"] = username
            q["token"] = token
            reset_password_url = "{0}?{1}".format(
                reverse("reset_password"), q.urlencode()
            )
            return HttpResponseRedirect(reset_password_url)
        else:
            form.add_error(None, _(error_message))
            self.request.session["forgot_password_attempts"] -= 1
            return self.render_to_response({'form': form})

    def get_form_kwargs(self):
        # add security questions for form field generation
        kwargs = super(ForgotPasswordView, self).get_form_kwargs()
        self.security_questions = list(models.SecurityQuestion.objects.all())
        random.shuffle(self.security_questions)
        profile_settings = models.UserProfilesSettings.for_site(
            self.request.site
        )
        kwargs["questions"] = self.security_questions[
            :profile_settings.num_security_questions
        ]
        return kwargs


class ResetPasswordView(FormView):
    form_class = forms.ResetPasswordForm
    template_name = "profiles/reset_password.html"

    def form_valid(self, form):
        username = form.cleaned_data["username"]
        token = form.cleaned_data["token"]

        try:
            user = User.objects.get_by_natural_key(username)
        except User.DoesNotExist:
            return HttpResponseForbidden()

        if not user.is_active:
            return HttpResponseForbidden()

        if not default_token_generator.check_token(user, token):
            return HttpResponseForbidden()

        password = form.cleaned_data["password"]
        confirm_password = form.cleaned_data["confirm_password"]

        if password != confirm_password:
            form.add_error(None,
                           _("The two passwords that you entered do not"
                             " match. Please try again."))
            return self.render_to_response({"form": form})

        user.set_password(password)
        user.save()
        self.request.session.flush()

        return HttpResponseRedirect(
            reverse("reset_password_success")
        )

    def render_to_response(self, context, **response_kwargs):
        username = self.request.GET.get("user")
        token = self.request.GET.get("token")

        if not username or not token:
            return HttpResponseForbidden()

        context["form"].initial.update({
            "username": username,
            "token": token
        })

        return super(ResetPasswordView, self).render_to_response(
            context, **response_kwargs
        )


class MenuView(TemplateView):
    template_name = "core/menu.html"

    def get_context_data(self, **kwargs):
        context = super(MenuView, self).get_context_data(**kwargs)
        context["active"] = "menu"
        return context
