from PyPDF2 import PdfFileMerger

pdf_file_merger = PdfFileMerger()
file = open("myfile.pdf", "w")
pdf_file_merger.merge(position=0, fileobj='file.pdf')
pdf_file_merger.write('out.pdf')
