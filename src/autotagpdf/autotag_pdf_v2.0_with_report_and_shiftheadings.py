# Copyright 2021 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.

import logging
import os.path
from pathlib import Path

from adobe.pdfservices.operation.auth.credentials import Credentials
from adobe.pdfservices.operation.exception.exceptions import ServiceApiException, ServiceUsageException, SdkException
from adobe.pdfservices.operation.execution_context import ExecutionContext
from adobe.pdfservices.operation.io.file_ref import FileRef

from adobe.pdfservices.operation.client_config import ClientConfig
from adobe.pdfservices.operation.internal.api.dto.request.autotagpdf.autotag_pdf_output_files import \
    AutotagPDFOutputFiles
from adobe.pdfservices.operation.pdfops.autotag_pdf_operation import AutotagPDFOperation
from adobe.pdfservices.operation.pdfops.options.autotagpdf.autotag_pdf_options import AutotagPDFOptions
from adobe.pdfservices.operation.pdfops.options.autotagpdf.pdf_version import PdfVersion

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))

try:
    # get base path.
    base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    # Initial setup, create credentials instance.
    credentials = Credentials.service_account_credentials_builder() \
        .from_file(base_path + "/pdfservices-api-credentials.json") \
        .build()

    # Create an ExecutionContext using credentials and create a new operation instance.
    execution_context = ExecutionContext.create(credentials)
    autotag_pdf_operation = AutotagPDFOperation.create_new()

    # Set operation input from a source file.
    input_file_path = 'autotagPdfInput.pdf'
    source = FileRef.create_from_local_file(base_path + "/resources/" + input_file_path)
    autotag_pdf_operation.set_input(source)

    input_file_name = Path(input_file_path).stem
    base_output_path = base_path + "/output/AutotagPDFWithV20AndReportAndShiftHeadings/"

    if not Path(base_output_path).is_dir():
        Path(base_output_path).mkdir(parents=True, exist_ok=True)
    tagged_pdf_output_path = Path(f'{base_output_path}{input_file_name}-taggedPDF.pdf')
    tagged_xls_output_path = Path(f'{base_output_path}{input_file_name}-report.xlsx')

    # Build AutotagPDF options and set them into the operation
    autotag_pdf_options: AutotagPDFOptions = AutotagPDFOptions.builder() \
        .with_pdf_version(PdfVersion.v20) \
        .with_shift_headings() \
        .with_generate_report() \
        .build()
    autotag_pdf_operation.set_options(autotag_pdf_options)

    # Execute the operation.
    autotag_output_files: AutotagPDFOutputFiles = autotag_pdf_operation.execute(execution_context)

    # Save the result to the specified location.
    FileRef.create_from_local_file(autotag_output_files.pdf_file).save_as(tagged_pdf_output_path)
    if autotag_pdf_options.get_generate_report():
        FileRef.create_from_local_file(autotag_output_files.xls_file).save_as(tagged_xls_output_path)
except (ServiceApiException, ServiceUsageException, SdkException):
        logging.exception("Exception encountered while executing operation")
