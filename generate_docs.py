import os
import django
import pydoc


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "calorieCounter.settings")
django.setup()

# files with doc
modules = [
    "app.views",
    "app.urls",
    "app.models",
]

for module in modules:
    print(f"Making doc for {module}")
    pydoc.writedoc(module)

print("Done!")