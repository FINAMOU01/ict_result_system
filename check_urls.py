import django
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
django.setup()

from django.urls import get_resolver

resolver = get_resolver()
print(f"Total top-level patterns: {len(resolver.url_patterns)}")

for p in resolver.url_patterns:
    pattern_str = str(p.pattern)
    print(f"\nPattern: '{pattern_str}'")
    if hasattr(p, 'url_patterns'):
        print(f"  This is an include with {len(p.url_patterns)} nested patterns")
        print("  All patterns:")
        for nested in p.url_patterns:
            pstr = str(nested.pattern)
            if 'download' in pstr or 'professor' in pstr:
                print(f"    >>> {pstr} <<<")
            else:
                print(f"    - {pstr}")
