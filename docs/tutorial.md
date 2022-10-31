<!-- doctree start -->
- [About the documentation](/docs/README.md)
- [Arguments Types](/docs/arguments_types.md)
- [Custom properties](/docs/custom_properties.md)
- [Generator functions](/docs/generator_functions.md)
- [Tutorial](/docs/tutorial.md)
<!-- doctree end -->

# Tutorial

There is two ways of using the library - with or without Regolith. Next
two sections describe both methods. Depending on your needs, you can
skip reading one of them.

## Using the generator with Regolith

Using the generator with Regolith is simple and recommended way to do it.
You have to add the generator to your project just like any other Regolith
filter.

**1.** Install the filter with command:
```
regolith install github.com/ShapescapeMC/regolith-filters/conetent_guide_generator
```

If you have Regolith and Python 3.9+ properly installed, it should install
the filter and create a virtual environment for it with the
`conetent_guide_generator` installed and ready to use. You don't need to install
`conetent_guide_generator` manually on your main Python environment.

**2.** Add the filter to the `filters` list in the `config.json` file of the Regolith
project:
```json
                    {
                        "filter": "conetent_guide_generator"
                    },
```
**3.** Running the generator should now build the `OUTPUT.md` file in the
filters data directory (`filters_data/content_guide_generator/OUTPUT.md`).

> **WARNING**
> 
>  The generator expects that the data directory of the filter contains the
> `TEMPLATE.md` file (`filters_data/content_guide_generator/TEMPLATE.md`).
> Step 2 from the installation process should handle that but if for some
> reason the file is missing, you have to create it manually.
> 
> You can read more about the template file below in the
> [Writing the TEMPLATE.md file](/docs/tutorial.md#writing-the-template.md-file) section.


## Using the generator without Regolith (not recommended)

This library comes with a commandline tool
(`shapescape-content-guide-generator.exe`) that can be used independently of
Regolith. If you want to use it, you need to install the library first. You can
do this by running the following command:

```
pip install git+https://github.com/ShapescapeMC/content-guide-generator
```
(this assumes that you have Python 3.10 or higher installed)

It is not recommended to use this tool if you can use Regolith
instead. The commandline tool is useful when you work in non-regolith-based
projects. The downside of this kind of workflow is that you can't put
[custom properties](/docs/custom_properties.md) in your code, because Minecraft
it would be treat it as invlid code.

Lack of custom properties means that the generated content guide won't be as
complete as it could be. It will still be useful as a base for writting
complete content guide but some parts will have to be written manually.

Since the tool is not meant to be used in Regolith-based projects, it doesn't
know the structure of the project. You have to include paths to resource
pack, behavior pack and the data folder in the commandline arguments. You
can also include the path to the output file, but you don't have to. In that
case the output will be saved in the data folder in `OUTPUT.md` file.

The tool comes with the help command that you can run with:
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
As you can see it requires 3 arguments: `-r`, `-b` and `-d` and one optional
argument `-o`.

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
> The `data` folder must have the same structure as in Regolith. This means that it has to have
> the `TEMPLATE.md` file. You can read about it in the
> [next section](/docs/tutorial.md#writing-the-template.md-file).

## Writing the `TEMPLATE.md` file

The `TEMPLATE.md` file is the main way to customize the content guide. It is
basically a regular Markdown file but you can insert `:generate:` functions
into it to generate certain parts of the content guide. You can read
more about the generate functions in the [Generator functions](/docs/generator_functions.md)
section.

You can find a good template file here: 
https://github.com/ShapescapeMC/regolith-filters/blob/master/content_guide_generator/data/TEMPLATE.md

If you're using Regolith, this file will be automatically created during the installation
of the filter. If you're using the commandline tool, you have to create this file
manually in the path that you'll specified in the `-d` argument.

Once you look through the template file, there is not to much to explain. You
have to write regular Markdown but some of the lines will start with
`:generate: function_name()`. All of the functions are described in the
[Generator functions](/docs/generator_functions.md) section but it's very
likely that you won't have to edit them at all. Some of the functions work
better if you also modify entities and items in your behavior pack to include
custom properties in them. You can read more about custom properties in the
[Custom properties](/docs/custom_properties.md) section.