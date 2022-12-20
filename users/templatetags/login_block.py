from django import template
from users.forms import UserLoginForm

register = template.Library()


@register.inclusion_tag('users/login_block.html')
def login_now():
    form = UserLoginForm()
    return {'form_login':form}
