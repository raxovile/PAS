import pyttsx3, PyPDF2

pdfReader = PyPDF2.PdfFileReader(open("book.pdf", "rb"))
audioConverter = pyttsx3.init()

for page_num in range(pdfReader.numPages):
    text = pdfReader.getPage(page_num).extractText()
    clean_text = text.strip().replace('\n', ' ' )
    print(clean_text)

audioConverter.save_to_file(clean_text, "audio.mp3")
audioConverter.runAndWait()

audioConverter.stop()