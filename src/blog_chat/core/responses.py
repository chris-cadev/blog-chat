import jinja2
from fastapi.templating import Jinja2Templates

from blog_chat.core.html import minify_html
from blog_chat.core.static import static_url


class MinifiedTemplate(jinja2.Template):
    def render(self, *args, **kwargs):
        rendered = super().render(*args, **kwargs)
        return minify_html(rendered)


def create_templates(directory):
    templates = Jinja2Templates(directory=directory)
    templates.env.template_class = MinifiedTemplate
    templates.env.filters["minify"] = minify_html
    templates.env.globals["static_url"] = static_url
    return templates
