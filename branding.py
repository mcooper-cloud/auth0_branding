#!/usr/bin/env python3

'''

    Read from a config file or a directory of config files and use 
    values parsed from the config file to render data into a single 
    Jinja template or a directory of Jinja templates

'''

import os
import argparse
from configparser import ConfigParser, ExtendedInterpolation
import json
import requests
from urllib.parse import urlparse


###############################################################################
###############################################################################
##
## Arguments - allows user to call from command line
##
###############################################################################
###############################################################################


class Args(object):

    parser = argparse.ArgumentParser(description='Pipeline deployment utility')

    parser.add_argument(
        '--branding-json', 
        dest='branding_json', 
        nargs=1, 
        help='Path to a the JSON file containing branding configuration'
    )

    parser.add_argument(
        '--prompts-json', 
        dest='prompts_json', 
        nargs=1, 
        help='Path to a the JSON file containing prompts configuration'
    )

    parser.add_argument(
        '--html-template', 
        dest='html_template', 
        nargs=1, 
        help='Path to a the Universal Login HTML template'
    )

    parser.add_argument(
        '--delete',
        dest='delete', 
        action='store_true',
        help='Remove both branding themes and Universal Login templates'
    )

    def print_help(self):
        self.parser.print_help()
        exit(1)
        return

    def parse(self):
        args = self.parser.parse_args()
        return args


###############################################################################
###############################################################################
##
## Auth0
##
###############################################################################
###############################################################################


class Auth0(object):

    def __init__( self, 
                  client_id=None, 
                  client_secret=None,
                  auth0_domain=None ):

        if client_id is None or client_secret is None or auth0_domain is None:
            ##
            ## get client_id, client_secret, auth0_domain from env
            ##
            self.client_id = os.environ.get('AUTH0_CLIENT_ID')
            self.client_secret = os.environ.get('AUTH0_CLIENT_SECRET')
            self.auth0_domain = os.environ.get('AUTH0_DOMAIN')

        else:

            self.client_id = client_id
            self.client_secret = client_secret
            self.auth0_domain = auth0_domain


        base_url = 'https://{}'.format(self.auth0_domain)

        self.mgmt_endpoint = os.environ.get('AUTH0_MGMT_API_ENDPOINT')

        print('[+] Auth0 Domain (reflects custom domain): {}'.format(self.auth0_domain))
        print('[+] Base URL: {}'.format(base_url))
        print('[+] Auth0 MGMT Endpoint: {}'.format(self.mgmt_endpoint))


        ##
        ## use the base MGMT FQDN to get token
        ##
        auth0_domain = 'https://{}'.format(urlparse(self.mgmt_endpoint).netloc)
        print('[+] Auth0 Domain (reflects MGMT domain): {}'.format(auth0_domain))

        ##
        ##********************************************************************
        ##
        ## URL Formats for Token endpoint:
        ##
        ##      https://[AUTH0_DOMAIN]/oauth/token
        ##
        ##********************************************************************
        ##
        if auth0_domain.endswith('/'):
            self.token_endpoint = '{}oauth/token'.format(auth0_domain)
        else:
            self.token_endpoint = '{}/oauth/token'.format(auth0_domain)

        print('[+] Token Endpoint: {}'.format(self.token_endpoint))

        ##
        ##********************************************************************
        ##
        ## URL Formats for Global Branding API:
        ##
        ##      https://[AUTH0_DOMAIN]/api/v2/branding
        ##
        ##********************************************************************
        ##
        if self.mgmt_endpoint.endswith('/'):
            self.global_branding_url = '{}branding'.format(self.mgmt_endpoint)
        else:
            self.global_branding_url = '{}/branding'.format(self.mgmt_endpoint)

        print('[+] Global Branding URL: {}'.format(self.global_branding_url))


        ##
        ##********************************************************************
        ##
        ## URL Formats for Branding Themes API:
        ##
        ##      https://[AUTH0_DOMAIN]/api/v2/branding/themes
        ##      https://[AUTH0_DOMAIN]/api/v2/branding/themes/default
        ##      https://[AUTH0_DOMAIN]/api/v2/branding/themes/{ID}
        ##
        ##********************************************************************
        ##
        if self.mgmt_endpoint.endswith('/'):
            self.branding_themes_url = '{}branding/themes'.format(self.mgmt_endpoint)
        else:
            self.branding_themes_url = '{}/branding/themes'.format(self.mgmt_endpoint)

        self.default_branding_themes_url = '{}/default'.format(self.branding_themes_url)

        print('[+] Branding Themes URL: {}'.format(self.branding_themes_url))
        print('[+] Branding Themes Default URL: {}'.format(self.default_branding_themes_url))


        ##
        ##********************************************************************
        ##
        ## URL Formats for Prompts API:
        ##
        ##      https://[AUTH0_DOMAIN]/api/v2/prompts
        ##      https://[AUTH0_DOMAIN]/api/v2/prompts/{prompt}/custom-text/{language}
        ##
        ##********************************************************************
        ##

        if self.mgmt_endpoint.endswith('/'):
            self.prompts_url = '{}prompts'.format(self.mgmt_endpoint)
        else:
            self.prompts_url = '{}/prompts'.format(self.mgmt_endpoint)

        print('[+] Custom Prompts URL: {}'.format(self.prompts_url))


        ##
        ##********************************************************************
        ##
        ## URL Formats for Universal Login Templates:
        ##
        ##      PUT /api/v2/branding/templates/universal-login
        ##
        ##********************************************************************
        ##
        if self.mgmt_endpoint.endswith('/'):
            self.template_url = '{}branding/templates/universal-login'.format(self.mgmt_endpoint)
        else:
            self.template_url = '{}/branding/templates/universal-login'.format(self.mgmt_endpoint)

        print('[+] Universal Login Template URL: {}'.format(self.template_url))


        ##
        ## now go get a token
        ##
        self.get_token()


    ##########################################################################
    ##########################################################################
    ##
    ## get token
    ##
    ##########################################################################
    ##########################################################################


    def get_token(self):

        if self.mgmt_endpoint.endswith('/'):
            audience = '{}'.format(self.mgmt_endpoint)
        else:
            audience = '{}/'.format(self.mgmt_endpoint)

        token_data = {
            'client_id' : self.client_id,
            'client_secret' : self.client_secret,
            'audience' : audience,
            'grant_type' : 'client_credentials'
        }

        print('[+] Getting access token from : {}'.format(self.token_endpoint))

        token_response = requests.post(self.token_endpoint, json=token_data)

        print('[+] Token response: {}'.format(token_response))

        self.access_token = token_response.json()['access_token']

        return self.access_token


    ##########################################################################
    ##########################################################################
    ##
    ## create request
    ##
    ##########################################################################
    ##########################################################################


    def create_request(
        self, url=None, headers=None, get=False, 
        put=False, post=False, patch=False, delete=False,
        json_data=None, data=None, theme_id=None 
    ):

        if url is None or headers is None:
            return None
        else:

            response = None

            if get is True:
                ##
                ## HTTP GET
                ##
                print('[+] HTTP GET: {}'.format(url))
                response = requests.get(url, headers=headers)

            elif put is True:
                ##
                ## HTTP PUT
                ##
                print('[+] HTTP PUT: {}'.format(url))
                if json_data is not None:
                    response = requests.put(url, headers=headers, json=json_data)
                elif data is not None:
                    response = requests.put(url, headers=headers, data=data)
                else:
                    return None

            elif post is True:
                ##
                ## HTTP POST
                ##
                print('[+] HTTP POST: {}'.format(url))
                if json_data is not None:
                    response = requests.post(url, headers=headers, json=json_data)
                elif data is not None:
                    response = requests.post(url, headers=headers, data=data)
                else:
                    return None

            elif patch is True:
                ##
                ## HTTP PATCH
                ##
                print('[+] HTTP PATCH: {}'.format(url))
                if json_data is not None:
                    response = requests.patch(url, headers=headers, json=json_data)
                elif data is not None:
                    response = requests.patch(url, headers=headers, data=data)
                else:
                    return None

            elif delete is True:
                ##
                ## HTTP DELETE
                ##
                print('[+] HTTP DELETE: {}'.format(url))
                response = requests.delete(url, headers=headers)


            try:
                response_data = response.json()
                print('[+] HTTP response body is JSON: \n {}'.format(json.dumps(response_data, indent=4)))
            except Exception as e:
                print('[-] HTTP response is not JSON')
                response_data = response
                print('[+] HTTP response body: \n {}'.format(response_data))

            return response_data


    ##########################################################################
    ##########################################################################
    ##
    ## get default branding
    ##
    ##########################################################################
    ##########################################################################


    def get_default_branding(self, headers=None):

        if headers is not None:

            default_branding_response = self.create_request(
                url = self.default_branding_themes_url, 
                headers=headers,
                get=True
            )

            default_json = default_branding_response
            default_brand_id = default_branding_response['themeId']

            print('[+] Default branding theme ID: {}'.format(default_brand_id))

        else:

            return None

        return tuple([default_json, default_brand_id])


    ##########################################################################
    ##########################################################################
    ##
    ## set prompts
    ##
    ##########################################################################
    ##########################################################################


    def set_prompts(self, json_data=None):

        patch = False
        put = False
        post = False
        get = False

        url = None
        prompts_response = None
        prompts_json = None

        if json_data is not None:

            headers = {'Authorization' : 'Bearer {}'.format(self.access_token)}

            ##
            ##********************************************************************
            ##
            ## URL Formats for Prompts API:
            ##
            ##      https://[AUTH0_DOMAIN]/api/v2/prompts
            ##      https://[AUTH0_DOMAIN]/api/v2/prompts/{prompt}/custom-text/{language}
            ##
            ##********************************************************************
            ##

            for j in json_data:

                prompt = j

                for l in json_data[j]:
                    language = l

                    screens = json_data[j][l]

                    prompts_url = '{}/{}/custom-text/{}'.format(self.prompts_url, prompt, language)

                    print('[+] Using prompt update URL: {}'.format(prompts_url))
                    print('[+] Using prompt update paylaod: \n{}'.format(screens))

                    prompts_response = self.create_request(
                        url = prompts_url,
                        headers=headers,
                        json_data=screens,
                        put=True
                    )

                    print('[+] Prompts response: {}'.format(prompts_response))

        else:
            return None


        return True


    ##########################################################################
    ##########################################################################
    ##
    ## create branding
    ##
    ##########################################################################
    ##########################################################################


    def create_branding(self, json_data=None, theme_id=None):

        patch = False
        put = False
        post = False
        get = False

        url = None
        branding_response = None
        branding_json = None

        if json_data is not None:

            headers = {'Authorization' : 'Bearer {}'.format(self.access_token)}

            if theme_id is None:

                try:

                    ##
                    ## no theme ID provided ... use default profile ID
                    ##
                    default_branding = self.get_default_branding(headers=headers)
                    default_brand_id = default_branding[1]

                    patch = True
                    put = False
                    post = False
                    get = False

                    url = '{}/{}'.format(self.branding_themes_url, default_brand_id)

                except Exception as e:
                    ##
                    ## didn't find the default branding theme and don't have
                    ## a theme ID ... so create a new theme
                    ##
                    print('[-] Default branding theme not found: {}'.format(e))
                    patch = False
                    put = False
                    post = True
                    get = False

                    url = self.branding_themes_url

            else:
                patch = True
                put = False
                post = False
                get = False

                url = '{}/{}'.format(self.branding_themes_url, theme_id)


            print('[+] Using branding profile: \n{}'.format(json.dumps(json_data, indent=4)))

            if post is True:

                ##
                ## create branding theme using HTTP POST
                ##
                branding_response = self.create_request(
                    url = url,
                    headers=headers,
                    json_data=json_data,
                    post=True
                )

            elif patch is True:
                ##
                ## create branding theme using HTTP POST
                ##
                branding_response = self.create_request(
                    url = url,
                    headers=headers,
                    json_data=json_data,
                    patch=True
                )

            ##
            ## if a Logo URL is in the JSON data it needs to be updated
            ## in the global branding profile as well as the branding theme
            ## otherwise the page temaplate variable '{{ branding.logo_url }}' 
            ## does not contain the correct logo path
            ##
            if 'widget' in json_data:
                if 'logo_url' in json_data['widget']:
                    print('[+] Global branding logo URL needs to be updated')

                    url = self.global_branding_url
                    branding_data = {
                        'favicon_url': json_data['widget']['logo_url'],
                        'logo_url': json_data['widget']['logo_url']
                    }
                    global_branding_response = self.create_request(
                        url = url,
                        headers=headers,
                        json_data=branding_data,
                        patch=True
                    )

        else:

            return None

        return branding_json


    ##########################################################################
    ##########################################################################
    ##
    ## delete branding
    ##
    ##########################################################################
    ##########################################################################


    def delete_branding(self, theme_id=None):

        url = None

        headers = {'Authorization' : 'Bearer {}'.format(self.access_token)}

        if theme_id is None:

            try:

                ##
                ## no theme ID provided ... use default profile ID
                ##
                default_branding = self.get_default_branding()
                default_brand_id = default_branding[1]
                url = '{}/{}'.format(self.branding_themes_url, default_brand_id)

            except Exception as e:
                ##
                ## didn't find the default branding theme and don't have
                ## a theme ID ... so create a new theme
                ##
                print('[-] Default branding theme not found: {}'.format(e))
                return None

        else:
            url = '{}/{}'.format(url, theme_id)

        print('[+] Deleting branding profile: {}'.format(theme_id))

        if url is not None:
            branding_response = self.create_request(url=url, headers=headers, delete=True)
        else:
            return None


        return branding_response


    ##########################################################################
    ##########################################################################
    ##
    ## create template
    ##
    ##########################################################################
    ##########################################################################


    def create_template(self, html_data=None):

        template_response = None

        if html_data is not None:

            headers = {
                'Authorization' : 'Bearer {}'.format(self.access_token),
                'content-type':'text/html'
            }

            template_response = self.delete_template()

            ##
            ## create branding theme using HTTP POST
            ##
            template_response = self.create_request(
                url = self.template_url,
                headers=headers,
                data=html_data,
                put=True
            )

        else:

            return None

        return template_response


    ##########################################################################
    ##########################################################################
    ##
    ## delete template
    ##
    ##########################################################################
    ##########################################################################


    def delete_template(self):

        headers = {'Authorization' : 'Bearer {}'.format(self.access_token)}

        print('[+] Deleting current HTML Template')
        template_response = self.create_request(url=self.template_url, headers=headers, delete=True)

        return template_response


###########################################################################
###########################################################################
##
## lambda handler
##
###########################################################################
###########################################################################


def lambda_handler(event, context):
    ##
    ## Lambda handler
    ##
    with open(event['branding_json'], 'rb') as f:
        branding_json = json.load(f)

    with open(event['prompts_json'], 'rb') as f:
        prompts_json = json.load(f)

    with open(event['html_template'], 'r+') as f:
        html_template = f.read()


    client_id = None
    client_secret = None
    auth0_domain = None

    print('[+] Creating Auth0 management client')
    auth0_tenant = Auth0( client_id=client_id, 
                          client_secret=client_secret,
                          auth0_domain=auth0_domain )

    if event['delete_input']:
        branding_data = auth0_tenant.delete_branding()
        template_data = auth0_tenant.delete_template()

    else:
        branding_data = auth0_tenant.create_branding(json_data=branding_json)
        prompts_data = auth0_tenant.set_prompts(json_data=prompts_json)
        template_data = auth0_tenant.create_template(html_data=html_template)

    return


###########################################################################
###########################################################################
##
## MAIN - install boto3 and AWS CLI to test locally
##
###########################################################################
###########################################################################

if __name__ == '__main__':

    ##########################################################################
    ##########################################################################
    ##
    ## parse arguments
    ##
    ##########################################################################
    ##########################################################################

    a = Args()
    args = a.parse()

    branding_json = args.branding_json[0] if args.branding_json else None
    prompts_json = args.prompts_json[0] if args.prompts_json else None
    html_template = args.html_template[0] if args.html_template else None
    delete_input = args.delete if args.delete else False


    ##########################################################################
    ##########################################################################
    ##
    ## exit on missing flags
    ##
    ##########################################################################
    ##########################################################################


    if branding_json is None:
        print('[-] Requires a JSON file via --branding-json argument')
        a.print_help()
        exit(1)

    if prompts_json is None:
        print('[-] Requires a JSON file via --prompts-json argument')
        a.print_help()
        exit(1)

    if html_template is None:
        print('[-] Requires an HTML file via --html-template argument')
        a.print_help()
        exit(1)


    ##########################################################################
    ##########################################################################
    ##
    ## call the handler
    ##
    ##########################################################################
    ##########################################################################

    context = None
    event = {
        'branding_json' : branding_json,
        'prompts_json' : prompts_json,
        'html_template' : html_template,
        'delete_input' : delete_input
    }

    lambda_handler(event, context)
