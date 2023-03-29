<!-- doctree start -->
Table of contents:
- [About the documentation](/docs/README.md)
- [Arguments Types](/docs/arguments_types.md)
- [Custom properties](/docs/custom_properties.md)
- [Generator functions](/docs/generator_functions.md)
- [Tutorial](/docs/tutorial.md)

In this article you can read about:
- [Using the generator with Regolith](#using-the-generator-with-regolith)
- [Using the generator without Regolith (not recommended)](#using-the-generator-without-regolith-not-recommended)
- [Writing the `TEMPLATE.md` file](#writing-the-templatemd-file)
- [Creating PDF files from the outputs of the generator](#creating-pdf-files-from-the-outputs-of-the-generator)
<!-- doctree end -->

# Tutorial

There are two ways of using the library - with or without Regolith. The next two sections describe both methods. Depending on your needs, you may wish to skip one of them.

## Using the generator with Regolith

Using the generator with Regolith is easy and recommended. You need to add the generator to your project just like any other Regolith filter. 

You can find the installation instructions on the README page of the content guide generator filter here: https://github.com/Shapescape-Software/content_guide_generator#-installation

After adding the filter to your Regolith project, you can configure its outputs by modifying the TEMPLATE.md file. You can read more about the template file [here](/docs/tutorial.md#writing-the-templatemd-file)

## Using the generator without Regolith (not recommended)

This library comes with a command line tool (`shapescape-content-guide-generator.exe`) that can be used independently of Regolith. If you want to use it, you need to install the library first. You can do this by running the following command:

```
pip install git+https://github.com/Shapescape-Software/content-guide-generator-module
```
(this assumes you have Python 3.10 or higher installed)

It is not recommended to use this tool if you can use Regolith instead. The command line tool is useful if you are working in a project that is not based on Regolith. The downside of this kind of workflow is that you can't put [custom properties](/docs/custom_properties.md) in your code, because Minecraft would treat it as invalid code.

The lack of custom properties means that the generated content guide won't be as complete as it could be. It will still be useful as a base for writing a complete content guide, but some parts will need to be written manually.

As the tool is not intended to be used in Regolith-based projects, it doesn't know the structure of the project. You need to include the paths to the resource pack, behaviour pack and data folder in the command line arguments. You can also include the path to the output file, but you don't have to. In this case the output will be saved in the data folder in the `OUTPUT.md` file.

The tool comes with a help command that you can use to run it:
```
shapescape-content-guide-generator.exe --help
```
The output of this will look like this:
```
usage: shapescape-content-guide-generator.exe [-h] -r RP -b BP -d DATA [-o OUTPUT]

A tool that generates content guides for Minecraft maps.

options:
  -h, --help            show this help message and exit
  -r RP, --rp RP        The path to the resource pack
  -b BP, --bp BP        The path to the behavior pack
  -d DATA, --data DATA  The path to the data folder
  -o OUTPUT, --output OUTPUT
                        The path to the output file
```
As you can see it requires 3 arguments: `-r`, `-b` and `-d` and one optional argument `-o`.

- `-r` or `--rp` is the path to the resource pack
- `-b` or `--bp` is the path to the behavior pack
- `-d` or `--data` is the path to the data folder
- `-o` or `--output` is the path to the output file.

Example usage:
```
shapescape-content-guide-generator.exe -r "path/to/rp" -b "path/to/bp" -d "path/to/data" -o "out.md"
```

> **WARNING**
>
> The `data` folder must have the same structure as in Regolith. This means that it must contain the file `TEMPLATE.md`. You can read about this in the [next section](/docs/tutorial.md#writing-the-templatemd-file).

## Writing the `TEMPLATE.md` file

The `TEMPLATE.md` file is the main way to customise the content guide. It is basically a normal Markdown file, but you can insert `:generate:` functions into it to generate certain parts of the content guide. You can read more about the generator functions in the [Generator Functions](/docs/generator_functions.md) section.

You can find an example of the `TEMPLATE.md` on the Content Guide Generator Regolith filter repository, in its default `data` folder:
https://github.com/Shapescape-Software/content_guide_generator/blob/master/content_guide_generator/data/TEMPLATE.md


If you're using Regolith, this file will be created automatically when the filter is installed. If you're using the command line tool, you'll need to create this file manually in the path you specify in the `-d' argument.

> WARNING
>
> If you're not working with Regolith, note that this file contains references to other files. It uses the `:generate: insert()` function, which inserts the contents of one `md` file into another. If you want to use this template, you need to copy the whole `data` folder, not just the `TEMPLATE.md` file.

If you look at the template file, there is not too much to explain. You have to write normal Markdown, but some of the lines start with `:generate: function_name()`. All the functions are described in the [Generator functions](/docs/generator_functions.md) section, but you probably won't need to edit them at all. Some of the functions will work better if you also modify the entities and items in your behaviour pack to include custom properties. You can read more about custom properties in the [Custom Properties](/docs/custom_properties.md) section.

## Creating PDF files from the outputs of the generator
The Content Guide Generator does not generate PDF files. It only generates Markdown files. If you want to create PDF files from the Markdown files, you can use a tool like Markdown PDF plugin for VS Code: https://marketplace.visualstudio.com/items?itemName=yzane.markdown-pdf