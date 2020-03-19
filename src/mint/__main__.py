# -*- coding: utf-8 -*-
"""
mint.

:license: Apache 2.0
"""
import json
import os
import re
from pathlib import Path

import click

import semver
import mint
from mint.cli_methods import run_method, edit_inputs_model_configuration, edit_parameter_config_or_setup, \
    edit_inputs_setup, run_method_setup
from mint.downloader import check_size, parse_inputs, parse_outputs
from mint.emulatorapi import get_summary, list_summaries, obtain_results
from mint.utils import obtain_id, download_file, download_data_file, humansize, SERVER, check_is_none
from mint.modelcatalogapi import get_setup, list_setup, get_model, list_model_configuration, get_model_configuration
from mint import _utils, _makeyaml
from mint._utils import log
import texttable as tt
from modelcatalog import DatasetSpecification, SampleResource

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


@click.group()
@click.option("--verbose", "-v", default=0, count=True)
def cli(verbose):
    _utils.init_logger()
    lv = ".".join(_utils.get_latest_version().split(".")[:3])
    cv = ".".join(mint.__version__.split(".")[:3])

    if semver.compare(lv, cv) > 0:
        click.secho(
            f"""WARNING: You are using mint version {mint.__version__}, however version {lv} is available.
You should consider upgrading via the 'pip install --upgrade mint' command.""",
            fg="yellow",
        )


"""
Run a modelconfiguration or modelconfiguration
"""
@click.command(help="Run a setup_name by name.")
@click.argument(
    "name",
    type=click.STRING
)
@click.option(
    '--edit',
    is_flag=True
)

def run(edit, name):
    setup = get_setup(name)
    edit_inputs_setup(setup)
    run_method_setup(setup)

def download_files(inputs, outputs, thread_directory):
    model_directory_inputs = thread_directory / 'inputs'
    model_directory_outputs = thread_directory / 'outputs'
    Path.mkdir(model_directory_inputs, parents=True, exist_ok=True)
    Path.mkdir(model_directory_outputs, parents=True, exist_ok=True)

    files = inputs + outputs
    size = 0
    for file in files:
        size += int(check_size(file['download_url']))
    click.secho("You are going to download {}".format(humansize(size)), fg="green")
    if not click.confirm('Do you want to continue?'):
        return

    click.secho("The destination directory is: {}".format(thread_directory.absolute()), fg="yellow")
    for file in outputs:
        data_specification_id = file['id']
        _, filename = download_data_file(file['download_url'], model_directory_outputs, data_specification_id)
        click.secho("Downloaded: {}".format(filename), fg="green")

    for file in inputs:
        _, filename = download_data_file(file['download_url'], model_directory_inputs)
        click.secho("Downloaded: {}".format(filename), fg="green")
