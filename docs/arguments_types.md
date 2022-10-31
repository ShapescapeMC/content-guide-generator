<!-- doctree start -->
- [About the documentation](/docs/README.md)
- [Arguments Types](/docs/arguments_types.md)
- [Custom properties](/docs/custom_properties.md)
- [Generator functions](/docs/generator_functions.md)
- [Tutorial](/docs/tutorial.md)
<!-- doctree end -->
# Arguments Types
This section describes the types of arguments that can be used in the
generator functions.

- **String** - text variable. Strings must be written in double quotes (`""`).
  **Examples:**
  - `"Hello World"` - string that says "Hello World".
- **Glob pattern** - a string, with the pattern that matches one or multiple
  file paths. Glob patterns can use special wildcards to match any name
  of a file or directory (single star `*`), any number of characters
  (double star `**`). **Examples:**
  - `"hello/*.json"` - all `.json` files in the `hello` directory
  - `"**/*.mcfunction"` - all `.mcfunction` files in the project
- **List** - multiple values groupped together. Lists use square brackets
  (`[]`). **Examples:**
  - `["hello", "world"]` - list with two strings
  - `["hello", 1, 2, 3]` - list with a string and three numberss
- **null** - no value. Null is spelled as literal `null` (lowercase).
- **bool** - boolean value. Boolean values are written as `true` or `false`.
