class PrivateResponses:
    def __init__(self,get_response): self.get_response=get_response
    def __call__(self,request):
        response=self.get_response(request)
        if not request.path.startswith('/static/'):
            response['Cache-Control']='no-store, private'
            response['Pragma']='no-cache'
        response['X-Robots-Tag']='noindex, nofollow'
        response['Content-Security-Policy']="default-src 'self'; script-src 'self'; style-src 'self'; style-src-attr 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
        return response
