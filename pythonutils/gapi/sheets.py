""" interface with the google sheets API. Important notes:
- any spreadsheet to be used must share with the email listed in the service-creds.json file (listed as `client_email`)
"""
import gspread
import pdb
import os
from oauth2client.service_account import ServiceAccountCredentials
from functools import partial

# TODO: We should really encapsulate all this functionality in an object, but that will be a breaking change

def __get_handle():
    """ authorize a Google Sheets handler and return that handle
    :return: `GC` google sheets handler interface
    """
    scope = ['https://spreadsheets.google.com/feeds']

    credentials = ServiceAccountCredentials.from_json_keyfile_name(os.environ['GAPI_SERVICE_CREDS'], scope)

    return gspread.authorize(credentials)


def with_handler(fn):
    """ decorator to add a Google sheets authorized handler to the wrapped function as a kwarg
    :param fn:
    :return:
    """
    def _inner(*args, **kwargs):
        kwargs['gc'] = kwargs.pop('gc', __get_handle())
        return fn(*args, **kwargs)

    return _inner


@with_handler
def get_workbook(wbook_name, gc=None):
    return gc.open(wbook_name)


@with_handler
def get_worksheet(wbook_name, sheet_name=None, sheet_ix=None, gc=None):
    workbook = get_workbook(wbook_name, gc=gc)

    if sheet_ix is not None:
        return workbook.get_worksheet(sheet_ix)
    elif sheet_name:
        return workbook.worksheet(sheet_name)
    else:
        raise ValueError("either a sheet_name or sheet_ix must be passed")


def get_all_cells(worksheet):
    """ get all the values of all the cells as a list of lists where each sublist contains the cells values as strings
    :param worksheet: `Worksheet` as returned by `get_worksheet`
    :return: `list` of `list` of `string`
    """
    return worksheet.get_all_values()


def get_cell_value(worksheet, col=None, row=None):
    """ get the value of the cell at the given col/row index
    :param worksheet:
    :param col:
    :param row:
    :return:
    """
    cell = worksheet.cell(row, col)
    return cell.value


def write_cell_value(worksheet, cell_label=None, col=None, row=None, value=None):
    if cell_label and (col and row):
        raise ValueError("only one of cell_label OR col + row should be passed")

    if cell_label:
        worksheet.update_acell(cell_label, value)
    else:
        worksheet.update_cell(row, col, value)


def write_row(worksheet, row_data, offset=0):
    [write_cell_value(worksheet, col=i + 1, row=offset + 1, value=v) for i, v in enumerate(row_data)]


def export(worksheet, output_path=None, format='pdf'):
    if not output_path.endswith(format):
        raise ValueError("the output_path file type should be the same as the file type of the worksheet export (format)")

    f = open(output_path, 'wb')

    f.write(worksheet.export(format=format))
    f.close()

    return output_path


def clear(worksheet):
    worksheet.clear()