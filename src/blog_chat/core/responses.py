import jinja2
from fastapi.templating import Jinja2Templates

from blog_chat.core.html import minify_html


class MinifiedTemplate(jinja2.Template):
    def render(self, *args, **kwargs):
        rendered = super().render(*args, **kwargs)
        return minify_html(rendered)


def create_templates(directory):
    templates = Jinja2Templates(directory=directory)
    templates.env.template_class = MinifiedTemplate
    templates.env.filters["minify"] = minify_html
    return templates


def minified_template_response(templates, template_name: str, context: dict):
    env = templates.env
    old_class = env.template_class
    env.template_class = MinifiedTemplate
    response = templates.TemplateResponse(template_name, context)
    env.template_class = old_class
    return response
