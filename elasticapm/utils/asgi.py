#  BSD 3-Clause License
#
#  Copyright (c) 2019, Elasticsearch BV
#  All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are met:
#
#  * Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
#  * Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
#  * Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#  AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#  IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#  DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
#  FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
#  DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#  SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
#  CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#  OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#  OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
This module implements ASGI related helpers adapted from ``werkzeug.asgi``

:copyright: (c) 2010 by the Werkzeug Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from urllib.parse import quote


# `get_headers` comes from scope headers`
def get_headers(scope):
    """
    Returns only proper HTTP headers.
    """
    for key, value in scope.items():
        key = str(key)
        if key.startswith("HTTP_") and key not in ("HTTP_CONTENT_TYPE", "HTTP_CONTENT_LENGTH"):
            yield key[5:].replace("_", "-").lower(), value
        elif key in ("CONTENT_TYPE", "CONTENT_LENGTH"):
            yield key.replace("_", "-").lower(), value


def get_scope(scope):
    """
    Returns our whitelisted environment variables.
    """
    for key in ("REMOTE_ADDR", "SERVER_NAME", "SERVER_PORT"):
        if key in scope:
            yield key, scope[key]


# `get_host` comes from `werkzeug.asgi`
def get_host(scope):
    """Return the real host for the given ASGI environment.  This takes care
    of the `X-Forwarded-Host` header.

    :param scope: the ASGI environment to get the host of.
    """
    scheme = scope.get("scheme")
    if "HTTP_X_FORWARDED_HOST" in scope:
        result = scope["HTTP_X_FORWARDED_HOST"]
    elif "HTTP_HOST" in scope:
        result = scope["HTTP_HOST"]
    else:
        result = scope["SERVER_NAME"]
        if (scheme, str(scope["SERVER_PORT"])) not in (("https", "443"), ("http", "80")):
            result += ":" + scope["SERVER_PORT"]
    if result.endswith(":80") and scheme == "http":
        result = result[:-3]
    elif result.endswith(":443") and scheme == "https":
        result = result[:-4]
    return result


# `get_current_url` comes from `werkzeug.asgi`
def get_current_url(scope, root_only=False, strip_querystring=False, host_only=False, path_only=False):
    """A handy helper function that recreates the full URL for the current
    request or parts of it.  Here an example:

    :param scope: the ASGI environment to get the current URL from.
    :param root_only: set `True` if you only want the root URL.
    :param strip_querystring: set to `True` if you don't want the querystring.
    :param host_only: set to `True` if the host URL should be returned.
    :param path_only: set to `True` if only the path should be returned.
    """
    if path_only:
        tmp = []
    else:
        tmp = [scope["scheme"], "://", get_host(scope)]
    cat = tmp.append
    if host_only:
        return "".join(tmp) + "/"
    cat(quote(scope.get("SCRIPT_NAME", "").rstrip("/")))
    if root_only:
        cat("/")
    else:
        cat(quote("/" + scope.get("PATH_INFO", "").lstrip("/")))
        if not strip_querystring:
            qs = scope.get("QUERY_STRING")
            if qs:
                cat("?" + qs)
    return "".join(tmp)
