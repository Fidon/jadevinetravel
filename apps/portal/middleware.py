from django.utils import translation

class PortalLanguageLockMiddleware:
    """
    Forces English for all /portal/ requests.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/portal/'):
            translation.activate('en')
            request.LANGUAGE_CODE = 'en'
        return self.get_response(request)