import FreeSimpleGUI as sg
import os
import tempfile
from md2docx_python.src.md2docx_python import markdown_to_word

def perform_conversion(markdown_file, output_docx):
    markdown_to_word(markdown_file, output_docx)

def main():
    sg.theme("LightBlue3")

    layout = [
        [sg.Text("Enter Markdown text (leave empty if selecting a file):")],
        [sg.Multiline(key="-MDTEXT-", size=(80, 20))],
        [sg.Text("OR choose a Markdown file:"), sg.Input(key="-FILEIN-"), 
         sg.FileBrowse(file_types=(("Markdown Files", "*.md"),))],
        [sg.Button("Convert and Save"), sg.Button("Exit")]
    ]

    window = sg.Window("Markdown to DOCX Converter", layout, finalize=True)

    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, "Exit"):
            break

        if event == "Convert and Save":
            md_text = values["-MDTEXT-"].strip()
            file_in = values["-FILEIN-"].strip()

            if md_text:
                try:
                    temp_md = tempfile.NamedTemporaryFile(delete=False, suffix=".md", mode="w", encoding="utf-8")
                    temp_md.write(md_text)
                    temp_md.close()
                    source_md = temp_md.name
                except Exception as e:
                    sg.popup_error("Error creating temporary file:", str(e))
                    continue
            elif file_in and os.path.isfile(file_in):
                source_md = file_in
            else:
                sg.popup_error("Please provide Markdown content or select a Markdown file.")
                continue

            output_docx = sg.popup_get_file(
                "Save Word Document",
                save_as=True,
                no_window=True,
                file_types=(("Word Documents", "*.docx"),),
                default_extension=".docx"
            )
            if not output_docx:
                sg.popup_error("No save file selected.")
                if md_text:
                    os.remove(source_md)
                continue

            try:
                perform_conversion(source_md, output_docx)
                sg.popup("Conversion successful!", f"File saved as: {output_docx}")
            except Exception as e:
                sg.popup_error("Conversion failed:", str(e))
            finally:
                if md_text and os.path.exists(source_md):
                    os.remove(source_md)

    window.close()

if __name__ == "__main__":
    main()
