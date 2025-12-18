# Using custom gvapython modules

The `shared/scripts` directory contains user-defined Python scripts that can be loaded as modules by the `gvapython` element.

To add and use a new script:

1. Drop your script into `shared/scripts` (for example `my_custom_logic.py`).
2. In your pipeline description, set the `module` property on the `gvapython` element to the script filename. Example: `gvapython module=tracked_object_filter.py`.

No additional effort is needed—referencing the filename via `module` is sufficient after the file is placed in this directory.
