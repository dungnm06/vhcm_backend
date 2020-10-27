from rest_framework.response import Response
from rest_framework import status
from vhcm.biz.exception.exception_handler import exception_cleaner
from vhcm.biz.authentication.access_token_updator import access_token_updator


class VhcmMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        response = exception_cleaner(request, response)
        response = access_token_updator(request, response)

        return response

    # def process_exception(self, request, exception):
    #     return Response({'error': True, 'content': exception}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
