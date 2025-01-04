import sys
import os
import json
import shutil
import time
from typing import List
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QFileDialog
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QTimer, QFileSystemWatcher, QUrl

from project_compiler import compile

from project_handler import ProjectHandler, ensure_proj_formatting

p_hand = ProjectHandler()

QHTML_LOCATION = '../projects/proj.html'

def get_image_link(img_html: str):
    img_html = img_html.replace('"', "'").replace(' ', '')

    if img_html.count("'") < 2:
        return ''

    a = img_html.find("src='") + 5
    b = img_html.find("'", a + 1)

    return img_html[a: b]

class MainWindow(QWidget):
    def __init__(self, object_title:str):
        super().__init__()

        self.object_title = object_title

        if not self.object_title.endswith('.json'):
            self.object_title += '.json'

        self.filepath = f'../projects/{object_title}'
        self.webpath = f'http://localhost:8000/projects/project.html?project={object_title}&local=1'

        self.selected_image_path = None

        self.qhtml_file = QHTML_LOCATION

        self.setWindowTitle("PyQt Application")

        try:
            # TODO: Adjust this to do a remote pull
            with open(self.filepath) as json_file:
                json_dump = json.load(json_file)
        except FileNotFoundError:
            json_dump = {}

        # Main layout
        main_layout = QHBoxLayout()

        # Left side layout (Inputs)
        self.left_layout = QVBoxLayout()

        # Short Title input
        self.short_title_label = QLabel("Short Title:")
        self.short_title_input = QLineEdit()
        self.short_title_input.setText(json_dump.get('projectShortTitle', ''))
        self.left_layout.addWidget(self.short_title_label)
        self.left_layout.addWidget(self.short_title_input)

        # Long Title input
        self.long_title_label = QLabel("Long Title:")
        self.long_title_input = QLineEdit()
        self.long_title_input.setText(json_dump.get('projectLongTitle', ''))
        self.left_layout.addWidget(self.long_title_label)
        self.left_layout.addWidget(self.long_title_input)


        # Label to show title image file
        self.image_file_label = QLabel("No file selected")
        self.left_layout.addWidget(self.image_file_label)

        # Upload button
        image_upload_button = QPushButton("Set Image")
        image_upload_button.clicked.connect(self.set_image)
        self.left_layout.addWidget(image_upload_button)

        self.post_image_filepath(get_image_link(json_dump.get('projectImage', '')))

        tag_label = QLabel("Tags")
        self.left_layout.addWidget(tag_label)

        self.add_tag_button = QPushButton("Add Tag")
        self.add_tag_button.clicked.connect(self.add_tag)
        self.left_layout.addWidget(self.add_tag_button)

        # Layout to hold tags
        self.tag_container = QVBoxLayout()
        self.left_layout.addLayout(self.tag_container)

        self.post_tags(json_dump.get('tags', []))

        tech_label = QLabel("Applicable Technologies")
        self.left_layout.addWidget(tech_label)

        self.add_tech_button = QPushButton("Add Tech")
        self.add_tech_button.clicked.connect(self.add_tech)
        self.left_layout.addWidget(self.add_tech_button)

        # Layout to hold tech
        self.tech_container = QVBoxLayout()
        self.left_layout.addLayout(self.tech_container)

        self.post_tech(json_dump.get('applicableTechnologies', []))

        # GitHub Link input
        self.github_label = QLabel("GitHub Link:")
        self.github_input = QLineEdit()
        self.left_layout.addWidget(self.github_label)
        self.left_layout.addWidget(self.github_input)

        self.github_input.setText(json_dump.get('githubLink', ''))

        # Href Link input
        self.href_label = QLabel("Force Href Link:")
        self.href_input = QLineEdit()
        self.left_layout.addWidget(self.href_label)
        self.left_layout.addWidget(self.href_input)

        self.href_input.setText(json_dump.get('forceHref', ''))

        # Description input
        self.description_label = QLabel("Description:")
        self.description_input = QTextEdit()
        self.left_layout.addWidget(self.description_label)
        self.left_layout.addWidget(self.description_input)

        self.description_input.setPlainText(json_dump.get('projectDescription', '').replace("<p>", "").replace("</p>", ""))

        self.refresh_button = QPushButton('Refresh!')
        self.refresh_button.clicked.connect(self.refresh_webpage)
        self.left_layout.addWidget(self.refresh_button)

        self.upload_button = QPushButton('Upload!')
        self.upload_button.clicked.connect(self.upload_project)
        self.left_layout.addWidget(self.upload_button)

        # Add the left layout to the main layout
        main_layout.addLayout(self.left_layout)

        # Right side layout (Web View)
        self.web_view = QWebEngineView()
        self.web_view.setUrl(QUrl(self.webpath))
        main_layout.addWidget(self.web_view)

        self.web_view.setFixedWidth(1400)

        self.setLayout(main_layout)

        time.sleep(1)
        self.refresh_webpage()

    def refresh_webpage(self):

        shutil.rmtree('../projects/temp') # Remove old files

        compile(p_hand.link_compiler, self.filepath, self.short_title_input.text(), self.long_title_input.text(), self.selected_image_path, self.description_input.toPlainText(), self.get_techs(), self.qhtml_file, self.get_tags(), self.github_input.text(), self.href_input.text())

        time.sleep(.5)

        self.web_view.setUrl(QUrl(f'{self.webpath}&nocache={time.time()}'))

        time.sleep(.1)

        self.web_view.reload()
    
    def upload_project(self):

        compile(p_hand.link_compiler, self.filepath, self.short_title_input.text(), self.long_title_input.text(), self.selected_image_path, self.description_input.toPlainText(), self.get_techs(), self.qhtml_file, self.get_tags(), self.github_input.text(), self.href_input.text(), False)

        p_hand.client.upload_file(self.filepath, f'projects/{self.object_title}')

        self.refresh_webpage()

    def post_image_filepath(self, path):
        self.image_file_label.setText(f"Selected: {os.path.basename(path)}")
        self.selected_image_path = os.path.join('../projects', path)
    
    def post_tags(self, tags: List[str]):

        for tag in tags:
            self.add_tag(basetext=tag)
    
    def post_tech(self, techs: List[str]):

        for tech in techs:
            self.add_tech(basetext=tech)

    def set_image(self):
        # Open a file dialog and get the selected file path
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "", "All Files (*.*)")
        if file_path:
            self.post_image_filepath(file_path)

    def add_tag(self, *args, basetext = None):
        # Horizontal layout for a single tag entry
        tag_layout = QHBoxLayout()

        # Delete button
        delete_button = QPushButton("Del")
        delete_button.setFixedWidth(30)
        delete_button.clicked.connect(lambda: self.remove_tag(tag_layout))
        tag_layout.addWidget(delete_button)

        # Text input for the tag
        tag_input = QLineEdit()
        tag_input.setPlaceholderText("Enter tag")

        if basetext is not None:
            tag_input.setText(basetext)

        tag_layout.addWidget(tag_input)

        # Add the tag entry to the container
        self.tag_container.addLayout(tag_layout)

    def remove_tag(self, tag_layout):
        # Remove all widgets in the given layout
        while tag_layout.count():
            widget = tag_layout.takeAt(0).widget()
            if widget:
                widget.deleteLater()

        # Remove the layout itself
        self.tag_container.removeItem(tag_layout)
    
    def get_tags(self):
        # Retrieve all tags as a list
        tags = []
        for i in range(self.tag_container.count()):
            # Get the layout for each tag entry
            tag_layout = self.tag_container.itemAt(i).layout()
            if tag_layout:
                # Extract the QLineEdit widget
                tag_input = tag_layout.itemAt(1).widget()
                if isinstance(tag_input, QLineEdit):
                    tag_text = tag_input.text().strip()
                    if tag_text:  # Add non-empty tags
                        tags.append(tag_text)
        return tags
    
    def get_techs(self):
        # Retrieve all tags as a list
        techs = []
        for i in range(self.tech_container.count()):
            # Get the layout for each tech entry
            tech_layout = self.tech_container.itemAt(i).layout()
            if tech_layout:
                # Extract the QLineEdit widget
                tech_input = tech_layout.itemAt(1).widget()
                if isinstance(tech_input, QLineEdit):
                    tech_text = tech_input.text().strip()
                    if tech_text:  # Add non-empty tags
                        techs.append(tech_text)
        return techs

    def add_tech(self, *args, basetext = None):
        # Horizontal layout for a single tech entry
        tech_layout = QHBoxLayout()

        # Delete button
        delete_button = QPushButton("Del")
        delete_button.setFixedWidth(30)
        delete_button.clicked.connect(lambda: self.remove_tech(tech_layout))
        tech_layout.addWidget(delete_button)

        # Text input for the tech
        tech_input = QLineEdit()
        tech_input.setPlaceholderText("Enter tech")

        if basetext is not None:
            tech_input.setText(basetext)

        tech_layout.addWidget(tech_input)

        # Add the tech entry to the container
        self.tech_container.addLayout(tech_layout)

    def remove_tech(self, tech_layout):
        # Remove all widgets in the given layout
        while tech_layout.count():
            widget = tech_layout.takeAt(0).widget()
            if widget:
                widget.deleteLater()

        # Remove the layout itself
        self.tech_container.removeItem(tech_layout)


if __name__ == "__main__":

    new_or_old = '.'

    while new_or_old not in ('new', 'old', '', 'continue'):
        print('New project, old, or continue editing?')
        new_or_old = input('(old) ? ').lower()

    if new_or_old == '':
        new_or_old = 'old'

    if new_or_old == 'old':
        print('All projects: ')
        print('-' * 20)

        for item in p_hand.list_projects():
            print('-', item.partition('.')[0])

        print('-' * 20)

        name = ensure_proj_formatting(input('name: '))

        p_hand.pull_project(name)

        print('Reverse compiling project...')

        with open(f'../projects/{name}') as json_file:
            contents = json.load(json_file)

        contents['projectImage'] = p_hand.link_compiler.reverse_compile_image(contents['projectImage'])
    
        with open(f'../projects/{name}', 'w') as json_file:
            json.dump(contents, json_file)

        reverse_compilation = p_hand.link_compiler.compile_backward(contents['projectText'])

        with open(QHTML_LOCATION, 'w') as f:

            f.write(reverse_compilation)

    elif new_or_old == 'new':

        name = ensure_proj_formatting(input('name: '))

        with open(os.path.join('../projects', name), 'w') as f:
            f.write('{}')

        with open(QHTML_LOCATION, 'w') as f:

            f.write('<p>Default Text</p>')

    else:

        name = ensure_proj_formatting(input('name: '))

    # name = 'cobot'

    app = QApplication(sys.argv)

    # Create and show the main window
    window = MainWindow(name)
    window.resize(1800, 1200)
    window.show()

    sys.exit(app.exec_())
