from blog.utils import menu


def get_samblog_context(request):
    return {'mainmenu': menu}