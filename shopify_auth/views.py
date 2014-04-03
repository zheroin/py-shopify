from django.http.response import HttpResponseRedirect
from django.shortcuts import render, resolve_url
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib import auth
import shopify


def get_return_address(request):
    return request.REQUEST.get(auth.REDIRECT_FIELD_NAME) or resolve_url(settings.LOGIN_REDIRECT_URL)


def login(request, *args, **kwargs):
    shop = request.REQUEST.get('shop')

    # If the shop parameter has already been provided, attempt to authenticate immediately.
    if shop:
        return authenticate(request, *args, **kwargs)

    return render(request, "shopify_auth/login.html")


def authenticate(request, *args, **kwargs):
    shop = request.REQUEST.get('shop')

    if shop:
        redirect_uri = request.build_absolute_uri(reverse('shopify_auth.views.finalize'))
        shopify_session = shopify.Session(shop)
        scope = settings.SHOPIFY_APP_API_SCOPE
        permission_url = shopify_session.create_permission_url(scope, redirect_uri)

        if settings.SHOPIFY_APP_IS_EMBEDDED:
            # Embedded Apps should use a Javascript redirect.
            return render(request, "shopify_auth/iframe_redirect.html", {
                'redirect_uri': permission_url
            })
        else:
            # Non-Embedded Apps should use a standard redirect.
            return HttpResponseRedirect(permission_url)

    return_address = get_return_address(request)
    return HttpResponseRedirect(return_address)


def finalize(request, *args, **kwargs):
    shop = request.REQUEST.get('shop')

    try:
        shopify_session = shopify.Session(shop)
        shopify_session.request_token(request.REQUEST)
    except:
        login_url = reverse('shopify_auth.views.login')
        return HttpResponseRedirect(login_url)

    # Attempt to authenticate the user and log them in.
    user = auth.authenticate(remote_user = shopify_session.url)
    if user:
        auth.login(request, user)

    return_address = get_return_address(request)
    return HttpResponseRedirect(return_address)
