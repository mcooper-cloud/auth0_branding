

# Auth0 Branding Tooling

## Usage

`./branding.py --html-template [path] --branding-json [path] --prompts-json [path]`


# Auth0 Branding API

See: https://auth0.com/docs/api/management/v2#!/Branding/patch_branding_theme

## Borders

| Option | Value |
| --- | --- |
| button_border_weight | int |
| buttons_style | [sharp, rounded, pill] |
| button_border_radius | int |
| input_border_weight | int |
| inputs_style | [sharp, rounded, pill] |
| input_border_radius | int |
| widget_corner_radius | int |
| widget_border_weight | int |
| show_widget_shadow | [true, false] |

## Colors

| Option | Value |
| --- | --- |
| primary_button | hex color |
| primary_button_label | hex color |
| secondary_button_border | hex color |
| secondary_button_label | hex color |
| base_focus_color | hex color |
| base_hover_color | hex color |
| links_focused_components | hex color |
| header | hex color |
| body_text | hex color |
| widget_background | hex color |
| widget_border | hex color |
| input_labels_placeholders | hex color |
| input_filled_text | hex color |
| input_border | hex color |
| input_background | hex color |
| icons | hex color |
| error | hex color |
| success | hex color |

## Display Name

| Option | Value |
| --- | --- |
| displayName | string |


## Fonts

| Option | Value |
| --- | --- |
|font_url | URI |
|reference_text_size | int |
|title | font obj |
|subtitle | font obj |
|body_text | font obj |
|buttons_text | font obj |
|input_labels | font obj |
|links | font obj |
|links_style | [normal, underlined] |

Reference font object:

```
"title": {
    "bold": true|false,
    "size": int
}
```


## Page Background

| Option | Value |
| --- | --- |
| page_layout | [left, right, center] |
| background_color | hex color |
| background_image_url | URI |


## Widget

| Option | Value |
| --- | --- |
| logo_position | [left,right, center] |
| logo_url | URL |
| logo_height| int |
| header_text_alignment | [left, right, center] |
| social_buttons_layout | [top, bottom] |


# Auth0 Page Templates API

See:

- https://auth0.com/docs/api/management/v2#!/Branding/put_universal_login
- https://auth0.com/docs/customize/universal-login-pages/universal-login-page-templates

# Auth0 Prompts API

See:

- https://auth0.com/docs/api/management/v2#!/Prompts/patch_prompts
- https://auth0.com/docs/customize/universal-login-pages/customize-login-text-prompts

## Prompt JSON Format

```
{
    "PROMPT" : {
        "LANGUAGE": {
            "SCREEN" : {
                "KEY" : "VALUE",
            }
        }
    }
}
```

Each prompt and language combination can support multple screen objects nested within.

# Delete Branding

Note: to delete custom prompts, it is necessary to pass in empty values for any previously set custom prompts.

`./branding.py --delete --prompts-json [path to blank values]`


