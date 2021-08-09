.. _faq:

Themes
======

What are themes?
----------------

OpenCart is highly customizable using Twig templates. A theme is a custom copy of design templates that you can install to give your store a custom look and feel. The native OpenCart install method is using FTP, but we prefer to not run an FTP server on our web  server so Peddler allows you to upload a theme to your store securly, without FTP.

How do I install a theme?
-------------------------

To install a theme, place the unzipped theme folder in your Peddler configuration root. So let's say that your theme was at `./mydesign`, you would copy it into your themes directory in the config root like this:

    $ cp -r ./mydesign "$(peddler config printroot)/env/themes/"

With the theme in place, you can upload it with the following command:

    $ peddler local upload-theme mydesign

This will put the theme files in place, but you will need to `activate this theme folder<https://www.opencart.com/blog?page=4&blog_id=207>`_ in your OpenCart admin to see the new theme.

Installing a theme on K8s
-------------------------

The K8s install type is very similar, just use the `k8s` subcommand instead of `local`.

    $ peddler k8s upload-theme mydesign

Does Peddler come with any themes bundled?
------------------------------------------

Not at the moment, but we are working on them. Feel free to contribute!
