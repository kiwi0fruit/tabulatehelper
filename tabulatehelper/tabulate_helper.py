import pandas as pd
import re
from typing import Iterable, Union, Tuple
from tabulate import tabulate


class TabulateHelperError(Exception):
    pass


def join_row(row: Iterable[str]) -> str:
    return '|' + '|'.join(row) + '|'


def split_md_table(string: str) -> Tuple[str, Tuple[str, ...], Tuple[str, ...], str, str]:
    """
    Returns ``(md_headers, headers, formats, table_body, line_sep)``.
    First is a pipe format str, second is a tuple of str keys.
    Or returns ``('', (), formats, table_body, line_sep)`` if header is absent.
    """
    err = 'tabulate returned GFM pipe table with invalid first two lines: {}'
    split = string.split('\n', 2)
    line_sep = '\r\n' if split[0][-1] == '\r' else '\n'
    def table_body(pos: int) -> str: return '\n'.join(split[pos:])
    lines = list(map(lambda s: s.rstrip('\r'), split[:2]))

    md_headers, headers, formats = '', (), None
    for line in reversed(lines):
        if formats:
            match = re.match(r'^\|.*[^\\]\|$', line)
            headers = tuple(map(
                lambda s: s.strip(' '),
                re.split(r'(?<=[^\\])\|', line[1:-1])
            ))
            if match and len(headers) == len(formats):
                md_headers = line
            else:
                raise TabulateHelperError(err.format(lines))
        elif re.match(r'^\|:?-+:?(\|:?-+:?)*\|$', line):
            formats = tuple(line[1:-1].split('|'))
    if formats:
        return md_headers, headers, formats, table_body(pos=2 if headers else 1), line_sep
    else:
        raise TabulateHelperError(err.format(lines))


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
    if (headers is None) and isinstance(tabular_data, pd.DataFrame):
        headers = tuple(map(str, tabular_data.columns))

    if headers is not None:
        kwargs['headers'] = headers
    kwargs['tablefmt'] = "pipe"
    kwargs['showindex'] = showindex

    md_tbl = tabulate(tabular_data, **kwargs)

    # Override align md_tbl formats with custom formats:
    # ---------------------------------------------
    md_headers, _headers, default_formats, table_body, line_sep = split_md_table(md_tbl)
    width = len(default_formats)
    # Set headers Markdown code:
    if not _headers and (headers is None):
        md_headers = re.sub(r'[^|]', ' ', join_row(default_formats))

    # Process formats to _formats:
    # ---------------------------------------------
    _formats = [''] * width
    if isinstance(formats, dict):
        for key in formats.keys():
            if isinstance(key, int) and not isinstance(key, bool):
                i = key
                if (i >= 0) and (i < width):
                    _formats[i] = formats[key]
                elif (i < 0) and (-i <= width):
                    _formats[width + i] = formats[key]
            elif isinstance(key, str):
                if key in _headers:
                    _formats[_headers.index(key)] = formats[key]
    elif formats is None:
        pass
    else:
        if isinstance(formats, str):
            if re.match(r'^[lrcLRC\-]+$', formats):
                fmts = list(formats)
            else:
                fmts = formats.split('|')
                fmts = fmts[(1 if fmts[0] == '' else 0):(-1 if fmts[-1] == '' else None)]
        else:
            fmts = list(formats)
        _formats = ([''] * (width - len(fmts)) + fmts)[:width]

    # Check _formats:
    # ---------------------------------------------
    for fmt in _formats:
        try:
            if not re.match(r'^(:?-+:?|[lrcLRC])$', fmt) and fmt:
                raise ValueError("Incorrect Markdown table format: '{}'".format(fmt))
        except TypeError as e:
            raise TypeError("Incorrect Markdown table format: '{}'. {}".format(fmt, e))

    # Replace l r c with :- -: :-:
    # ---------------------------------------------
    rep = dict(l=':-', r='-:', c=':-:', L=':-', R='-:', C=':-:')
    _formats = [rep.get(fmt, fmt) for fmt in _formats]

    # Apply _formats to default_formats:
    # ---------------------------------------------
    _formats = join_row(fmt[0] + def_fmt[1:-1] + fmt[-1] if fmt else def_fmt
                        for fmt, def_fmt in zip(_formats, default_formats))

    # ---------------------------------------------
    if return_headers_only:
        if not md_headers:
            return ''
        else:
            return line_sep.join((md_headers, _formats, re.sub(r'[^|]', ' ', _formats)))
    else:
        return line_sep.join(filter(None, (md_headers, _formats, table_body)))


def md_header(tabular_data: Union[pd.DataFrame, object],
              headers: tuple = None,
              showindex: Union[bool, None] = False,
              formats: Union[dict, str, Iterable[str]] = None,
              **kwargs) -> str:
    """
    Returns only table header + empty row.
    If header is absent then returns empty string.

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
    kwargs :
        Other tabulate.tabulate(...) optional keyword arguments

    Returns
    -------
    md :
        Markdown table header + empty row
    """
    return md_table(tabular_data, headers=headers, showindex=showindex,
                    formats=formats, return_headers_only=True, **kwargs)
