from django.conf.urls import url
from django.views.generic import TemplateView

urlpatterns = [
    url(
        r"^atoms/",
        TemplateView.as_view(template_name="styleguide/atoms.html"),
        name="atoms"
    ),
    url(
        r"^molecules/",
        TemplateView.as_view(template_name="styleguide/molecules.html"),
        name="molecules"
    ),
    url(
        r"^organisms/",
        TemplateView.as_view(template_name="styleguide/organisms.html"),
        name="organisms"
    ),
    url(
        r"^templates/",
        TemplateView.as_view(template_name="styleguide/templates.html"),
        name="templates"
    ),
    url(
        r"^pages/",
        TemplateView.as_view(template_name="styleguide/pages.html"),
        name="pages"
    ),
    url(
        r"",
        TemplateView.as_view(template_name="styleguide/index.html"),
        name="index"
    )
]
