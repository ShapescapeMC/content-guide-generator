<!-- doctree start -->
- [About the documentation](/docs/README.md)
- [Arguments Types](/docs/arguments_types.md)
- [Custom properties](/docs/custom_properties.md)
- [Generator functions](/docs/generator_functions.md)
- [Tutorial](/docs/tutorial.md)
<!-- doctree end -->

# Tutorial

There are two ways of using the library - with or without regolith. The next two sections describe both methods. Depending on your needs, you may wish to skip one of them.

## Using the generator with Regolith

Using the generator with Regolith is easy and recommended. You need to add the generator to your project just like any other Regolith filter.

**1.** Install the filter with the command
```
regolith install github.com/ShapescapeMC/regolith-filters/content_guide_generator
```

If you have Regolith and Python 3.9+ properly installed, it should install the filter and create a virtual environment for it with `content_guide_generator` installed and ready to use. You don't need to manually install `content_guide_generator` on your main Python environment.

**2.** Add the filter to the `filters` list in the Regolith `config.json` file
project:
```json
                    {
                        "filter": "content_guide_generator"
                    },
```
**3.** Running the generator should now create the `OUTPUT.md` file in the filter data directory (`<filters data path>/content_guide_generator/OUTPUT.md`).

**WARNING**.
> 
> The generator expects the filter data directory to contain the `TEMPLATE.md` file (`<filters data path>/content_guide_generator/TEMPLATE.md`). Step 2 of the installation process should take care of this, but if for some reason the file is missing, you will need to create it manually.
> 
> You can read more about the template file below in the section [Writing the TEMPLATE.md file](/docs/tutorial.md#writing-the-templatemd-file).

## Using the generator without Regolith (not recommended)

This library comes with a command line tool (`shapescape-content-guide-generator.exe`) that can be used independently of Regolith. If you want to use it, you need to install the library first. You can do this by running the following command:

```
pip install git+https://github.com/ShapescapeMC/content-guide-generator
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

A good template file can be found here: 
https://github.com/ShapescapeMC/regolith-filters/blob/master/content_guide_generator/data/TEMPLATE.md

> WARNING
>
> Note that this file contains references to other files. It uses the `:generate: insert()` function, which inserts the contents of one `md` file into another. If you want to use this template, you need to copy the whole `data` folder, not just the `TEMPLATE.md` file.

If you're using Regolith, this file will be created automatically when the filter is installed. If you're using the command line tool, you'll need to create this file manually in the path you specify in the `-d' argument.

If you look at the template file, there is not too much to explain. You have to write normal Markdown, but some of the lines start with `:generate: function_name()`. All the functions are described in the [Generator functions](/docs/generator_functions.md) section, but you probably won't need to edit them at all. Some of the functions will work better if you also modify the entities and items in your behaviour pack to include custom properties. You can read more about custom properties in the [Custom Properties](/docs/custom_properties.md) section.

