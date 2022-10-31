<!-- doctree start -->
- [About the documentation](/docs/README.md)
- [Arguments Types](/docs/arguments_types.md)
- [Custom properties](/docs/custom_properties.md)
- [Generator functions](/docs/generator_functions.md)
- [Tutorial](/docs/tutorial.md)
<!-- doctree end -->

# About the documentation
## How to read the documentation
The best place to start is the [tutorial](/docs/tutorial.md). The tutorial page
should be sufficient to get you started with the basics of the library. The
tutorial page has references to the other pages in the documentation.

## Older versions of the documentation
If you're looking for the older version of the documentation just open
it on GitHub using different version tags. The links in the documentation
are set up in such a way that you can use them without getting redirected
to the current state of the repository.

## How to write the documentation
All of the documentation files are saved on this repository in the docs
directory. We chose this solution over the Wiki because it is easier to
maintain and it lets you easily read it for any version of the program.

The list of the pages at the top is automatically generated with the
[generate_doctree.py](/generate_doctree.py) script. If you're add or remove a
page, please run the script to update the list. The first title of the page
is used as the name in the doctree.

All of the links in the documents should use the path relative to the root of
this project. For example a link to this file is:
```md
[About the documentation](/docs/README.md)
```
This will let us have working links in the documentation even for the old
versions of the app.
