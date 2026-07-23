# -*- coding: utf-8 -*-
#
# Galaxy Tool Development Standards and Best Practices documentation build
# configuration file.

# -- General configuration ---------------------------------------------

extensions = [
    "myst_parser",
    "sphinx_design",
]

templates_path = ["_templates"]
source_suffix = [".rst", ".md"]
master_doc = "index"

project = "Galaxy Tool Development Standards and Best Practices"
copyright = "2015-2026, Galaxy IUC and Community"
author = "Galaxy IUC"

version = ""
release = ""

exclude_patterns = ["_build"]

pygments_style = "default"

# -- Options for HTML output -------------------------------------------

html_theme = "pydata_sphinx_theme"

html_theme_options = {
    "logo": {
        "text": "Galaxy Tool Standards",
    },
    "navbar_align": "left",
    "show_prev_next": True,
    "footer_start": ["copyright"],
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/galaxy-iuc/standards",
            "icon": "fa-brands fa-github",
        },
        {
            "name": "Galaxy Project",
            "url": "https://galaxyproject.org",
            "icon": "fa-solid fa-globe",
        },
    ],
    "secondary_sidebar_items": ["page-toc"],
    "navigation_with_keys": True,
}

html_static_path = ["_static"]
html_css_files = ["css/galaxy.css"]
html_title = "IUC Standards"
html_short_title = "IUC Standards"

htmlhelp_basename = "GalaxyIUCStandardsandBestPracticesdoc"

# -- Options for LaTeX output ------------------------------------------

latex_elements = {}

latex_documents = [
    (
        master_doc,
        "GalaxyIUCStandardsandBestPractices.tex",
        "Galaxy IUC Standards and Best Practices Documentation",
        "Galaxy IUC",
        "manual",
    ),
]

# -- Options for manual page output ------------------------------------

man_pages = [
    (
        master_doc,
        "galaxyiucstandardsandbestpractices",
        "Galaxy IUC Standards and Best Practices Documentation",
        [author],
        1,
    )
]
