#!/usr/bin/env python3
from PyPDF2 import PdfFileMerger

pdf_file_merger = PdfFileMerger()
pdf_file_merger.merge(position=1, fileobj='extremely_important.pdf')
pdf_file_merger.merge(position=0, fileobj='file.pdf')
pdf_file_merger.write('out.pdf')
