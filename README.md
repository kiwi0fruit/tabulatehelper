# Tabulate Helper

Converts tabular data like Pandas dataframe to GitHub Flavored Markdown pipe table (wrapper around [tabulate](https://pypi.org/project/tabulate/) module). I use it with  [Pandoctools/Knitty](https://github.com/kiwi0fruit/pandoctools).


# Contents

* [Tabulate Helper](#tabulate-helper)
* [Contents](#contents)
* [Install](#install)
* [Differences from tabulate module](#differences-from-tabulate-module)
* [Usage example](#usage-example)
* [Converting to other formats](#converting-to-other-formats)
* [API](#api)


# Install

Via conda:

```
conda install -c defaults -c conda-forge tabulatehelper
```

Via pip:

```
pip install tabulatehelper
```


# Differences from tabulate module

* With defaults: auto-headers for Pandas data frames,
* With defaults: auto-empty headers for GitHub compatibility,
* Special function that prints header only (useful at the end of long tables),
* Doesn't show index by default,
* `formats` argument can be set that selectively overrides automatic align format.

Example:
```py
import numpy as np
import pandas as pd
from tabulate import tabulate
import tabulatehelper as th

df = pd.DataFrame(np.random.random(16).reshape(4, 4), columns=('a', 'b', 'c', 'd'))

# tabulate wtithout wrapper:
tbl = tabulate(df, df.columns, tablefmt='pipe', showindex=False)

# tabulate helper with overriding align format:
tbl = th.md_table(df, formats={-1: 'c'})

print(tbl)
```

Output:
```
|        a |        b |        c |        d |
|---------:|---------:|---------:|:--------:|
| 0.413284 | 0.932373 | 0.277797 | 0.646333 |
| 0.552731 | 0.381826 | 0.141727 | 0.2483   |
| 0.779889 | 0.012458 | 0.308352 | 0.650859 |
| 0.301109 | 0.982111 | 0.994024 | 0.43551  |
```


## Usage example

Main functions are `tabulatehelper.md_table(...)` and `tabulatehelper.md_header(...)`. Usage example that works both in Atom+Hydrogen and in Pandoctools+Knitty:

```py
from IPython.display import Markdown
import pandas as pd
import numpy as np
import tabulatehelper as th

df = pd.DataFrame(np.random.random(16).reshape(4, 4))

# appended header is useful when very long table
# (can display `df.iloc[[0]]` in hydrogen)
Markdown(f"""

{th.md_table(df)}

: Table {{#tbl:table1}}

{th.md_header(df)}

""")
```


# Converting to other formats

Tabulate can convert to other formats but I prefer using [panflute convert_text](http://scorreia.com/software/panflute/code.html#panflute.tools.convert_text) on `th.md_table` output as it can convert to any Pandoc supported [output format](https://pandoc.org/MANUAL.html#general-options)

    conda install -c defaults -c conda-forge py-pandoc panflute
    pip install py-pandoc panflute


# API

From [tabulate_helper.py](https://github.com/kiwi0fruit/tabulatehelper/tree/master/tabulatehelper/tabulate_helper.py):

```py
def md_table(tabular_data: Union[pd.DataFrame, object],
             headers: tuple = None,
             showindex: Union[bool, None] = False,
             formats: Union[dict, str, Iterable[str]] = None,
             return_headers_only: bool = False,
             **kwargs) -> str:
    """
    Converts tabular data like Pandas dataframe to
    GitHub Flavored Markdown pipe table.

    Markdown table ``formats`` examples:

    * ``dict(foo='-:', bar=':-:', **{-1: 'c'})``,
    * ``'--|-:|:-:'`` or ``'|--|-:|:-:|'`` or ``-rc``,
    * ``['--', '-:', 'C']``

    Parameters
    ----------
    tabular_data :
        tabulate.tabulate(tabular_data[,...]) argument
    headers :
        tabulate.tabulate(..., headers[,...]) optional argument.
        If None and tabular_data is pd.DataFrame then default is
        tabular_data.columns converted to Tuple[str, ...].
        If None then use tabulate.tabulate(...) default
        (but in this particular case if it's absent in the output
        then add blank header).
    showindex :
        tabulate.tabulate(..., showindex[,...]) optional argument.
    formats :
        GitHub Flavored Markdown table align formats: dict, str or list / iterable.
        '-' mean lack of align format, 'l'/'L'/':-' mean left align,
        'r'/'R'/'-:' mean right align, 'c'/'C'/':-:' mean center align.
        dict keys are for tabulate output headers so they should be str.
        int keys mean column number.
    return_headers_only :
        returns only table header + empty row.
        If header is absent then returns empty string.
    kwargs :
        Other tabulate.tabulate(...) optional keyword arguments

    Returns
    -------
    md :
        Markdown table
    """
    ...
```
