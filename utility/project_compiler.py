from typing import List
import json
import os
import shutil
import htmlmin

from string_helpers import parse_block, optional_block_targeting, isolate_block

from s3_utils import S3Wrapper

# https://icon-sets.iconify.design

CONTENT_FLAG_STRING = '!!Content!!:'

def resize_svg(svg_text: str, size = 4):

    if not 'svg' in svg_text:
        # Text passed is most likely not a svg, and some weird functionality is intended
        # We will respect the users wishes, and pass the text as is.

        return svg_text

    size_string = f'{size}em'

    # Adjust width
    width_from_index = svg_text.find('width=')
    width_to_index = svg_text.find(' ', width_from_index)

    width_string = svg_text[width_from_index: width_to_index]

    svg_text = svg_text.replace(width_string, f'width="{size_string}"', 1)

    # Adjust height
    height_from_index = svg_text.find('height=')
    height_to_index = svg_text.find(' ', height_from_index)

    height_string = svg_text[height_from_index: height_to_index]

    svg_text = svg_text.replace(height_string, f'height="{size_string}"', 1)

    return svg_text

def attach_optional_field(text, object, field):

    if text is None:
        return

    text = text.strip()

    if len(text) == 0:
        return

    object[field] = text

def migrate(file_path: str, s3_wrapper: S3Wrapper, project_name: str, to_remote = False):

    print('Migrating:', file_path, 'to', ['local', 'remote'][to_remote])

    if not os.path.exists(file_path):
        print(f'Warning: File does not exist: {file_path}')
        return

    if os.path.isdir(file_path):
        print(f'Warning: Directory was passed: {file_path}')
        print('Note this is normal upon creating a new project, just assign the project image')
        return

    if not to_remote:
        # Transferring to local temp directory

        # Ensure remote path exists

        temp_path = os.path.abspath('../projects/temp')

        os.makedirs(temp_path, exist_ok = True)

        try:
            shutil.copy(file_path, temp_path)
        except shutil.SameFileError:
            pass

        return os.path.join('temp', os.path.basename(file_path))

    else:
        
        proj_base = project_name

        file_base = os.path.basename(file_path)

        key = os.path.join('content', proj_base, file_base)

        return s3_wrapper.upload_file(file_path, key)

class LinkCompiler:
    def __init__(self, s3_wrapper: 'S3Wrapper', bucket_name: str, region = 'us-east-2'):

        self.client = s3_wrapper

        self.itext = '=!=HERE=!='

        self.search_text = f'https://{bucket_name}.s3.{region}.amazonaws.com'

        self.HREF_KEYS = {
            'mp4': f"<video controls><source src='{self.itext}' type='video/mp4'>Your browser does not support the video tag.</video>",
            'mov': f"<video controls><source src='{self.itext}'>Your browser does not support the video tag.</video>",
            'pdf': f"<embed src='{self.itext}' type='application/pdf'>",
            'png': f"<img src='{self.itext}'>",
            'jpg': f"<img src='{self.itext}'>",
            'jpeg': f"<img src='{self.itext}'>",
        }

        self.HTML_KEYS = {
            '<video': '</video>',
            '<embed': '>',
            '<img': '>',
        }

        self.QUOTE_KEYS = {
            '"': '"',
            "'": "'"
        }
    
    def compile_forward(self, input_string: str, project_name, cloud = False):
        '''Compile a designated string, converting local paths to web paths
        
        (If selected for cloud, this function does do the uploading)'''


        while CONTENT_FLAG_STRING in input_string:

            parsed = parse_block(input_string, CONTENT_FLAG_STRING, '\n')

            path = parsed.replace('"', '')

            file_type = os.path.basename(path).partition('.')[2].lower()

            if not file_type in self.HREF_KEYS:
                raise ValueError(f'Invalid file type: {file_type}\nAttempted to compile: {path}')

            new_path = migrate(path, self.client, project_name, to_remote = cloud)

            processed_file = self.HREF_KEYS[file_type].replace(self.itext, new_path, 1)

            if not CONTENT_FLAG_STRING + parsed in input_string:
                print(CONTENT_FLAG_STRING + parsed)

                print(input_string)

                raise LookupError('Could not forward compile string')

            input_string = input_string.replace(CONTENT_FLAG_STRING + parsed, processed_file, 1)
        
        return input_string
        

    def _single_rev_html_replacement(self, input_string):
        url_location = input_string.find(self.search_text)

        url_block = list(optional_block_targeting(input_string, url_location, self.QUOTE_KEYS))

        url_block[0] += 1
        url_block[1] -= 1

        url = isolate_block(input_string, url_block)

        html_element = isolate_block(input_string, optional_block_targeting(input_string, url_location, self.HTML_KEYS))

        self.client.download_url_to_directory(url, '../projects/temp')

        new_location = os.path.join('../projects/temp', os.path.basename(url))

        return input_string.replace(html_element, '\n\n' + CONTENT_FLAG_STRING + new_location + '\n\n')
    
    def compile_backward(self, input_string: str):

        '''
        Download href'd files in the input string, and replace the html attributes with local content flags
        '''

        while self.search_text in input_string:

            input_string = self._single_rev_html_replacement(input_string)

        return input_string.replace('</', '\n</')
    
    def reverse_compile_image(self, img_html: str):

        flagged_string = self._single_rev_html_replacement(img_html)

        raw_path = flagged_string.replace(CONTENT_FLAG_STRING, '').replace('\n', '')

        name = os.path.basename(raw_path)

        return f'<img src="temp/{name}">'

def compile(link_compiler: LinkCompiler, project_json_path: str, short_title: str, long_title: str, image_path: str, description: str, techs: List[str], text_qhtml_path: str, tags: List[str], github_link: str, href_link: str, local: bool = True):

    ref_name = os.path.basename(project_json_path).partition('.')[0]

    digest = {}

    digest['projectShortTitle'] = short_title.strip()
    digest['projectLongTitle'] = long_title.strip()

    digest['projectImage'] = f'<img src="{migrate(image_path, link_compiler.client, ref_name, to_remote=not local)}">'

    digest['projectDescription'] = f'<p>{description.strip()}</p>'

    for index, svg_text in enumerate(techs):
        techs[index] = resize_svg(svg_text)

    digest['applicableTechnologies'] = techs

    digest['tags'] = tags

    attach_optional_field(href_link, digest, 'forceHref')
    attach_optional_field(github_link, digest, 'githubLink')

    with open(text_qhtml_path) as content:

        file_content = content.read()

        compiled_text = link_compiler.compile_forward(file_content, ref_name, cloud = not local)

        minified_html = htmlmin.minify(compiled_text, remove_empty_space=True, remove_optional_attribute_quotes=False)

        digest['projectText'] = minified_html

    with open(project_json_path, 'w') as output_file:
        json.dump(digest, output_file)

if __name__ == '__main__':

    name = '../projects/compiled.json'
    short_name = 'short'
    long_name = 'long'
    image_path = '../images/DVD_logo.png'
    description = 'description'
    techs = ['''<svg xmlns="http://www.w3.org/2000/svg" width="256" height="210" viewBox="0 0 256 210"><path d="M80.455 208.842H60.45v-18.359h19.69v4.066H65.802v3.127h13.572v3.835H65.811v3.162h14.644zm115.092 0h-19.69v-18.068h19.383v3.982h-14.106v3.075h13.357v3.771h-13.357v3.115h14.413zm-87.956 0h-8.104L88.83 195.111h-.104v13.731H83.43v-18.359h8.223l10.526 13.748h.103v-13.748h5.309zm64.129 0h-8.092l-10.657-13.731h-.104v13.731h-5.32v-18.359h8.223l10.526 13.748h.103v-13.748h5.32zm-47.678.235l-.824.008l-.625-.002l-.603-.006l-.58-.01l-.56-.014l-.536-.018l-.514-.021l-.493-.026l-.47-.03a16.4 16.4 0 0 1-3.15-.47a6 6 0 0 1-2.099-.984a4.1 4.1 0 0 1-1.258-1.633a8.3 8.3 0 0 1-.625-2.44a32 32 0 0 1-.156-2.969v-.962a31 31 0 0 1 .164-3.417a8.3 8.3 0 0 1 .613-2.454a4.2 4.2 0 0 1 1.262-1.628a5.9 5.9 0 0 1 2.103-.964c.927-.231 1.872-.38 2.825-.447l.317-.019q.233-.016.474-.028l.495-.024l.255-.011l.526-.019l.548-.015l.569-.01l.292-.005l.6-.006l.622-.002h.796l.595.002l.573.006l.552.01l.268.005l.52.015l.497.019l.241.01l.466.025q1.38.07 2.736.335c.66.123 1.298.346 1.892.66c.477.254.887.619 1.194 1.064c.305.47.51.997.602 1.55a12 12 0 0 1 .167 1.841v.97h-5.177v-.223c.01-.36-.057-.719-.195-1.052a1.44 1.44 0 0 0-.76-.68a5.5 5.5 0 0 0-1.412-.343l-.182-.016q-.342-.032-.757-.056l-.344-.016l-.367-.013l-.39-.01l-.413-.006l-.437-.003h-.686l-.448.003l-.633.008l-.395.009l-.375.011l-.353.014l-.168.007a10 10 0 0 0-1.796.227c-.41.088-.797.26-1.135.506c-.29.23-.509.538-.63.888a5.3 5.3 0 0 0-.25 1.216l-.013.178q-.012.166-.021.345l-.017.372l-.012.399l-.007.424l-.002.223v.78l.005.43l.01.402l.014.377q.008.183.02.351l.01.166c.026.465.114.925.263 1.366c.122.348.34.653.63.88c.338.246.725.418 1.135.506q.76.167 1.537.214l.427.021l.353.014l.375.012l.395.009l.417.005l.437.003h1.353l.418-.001l.394-.005q.384-.007.72-.026l.551-.04l.357-.028q.43-.035.772-.086c.337-.048.667-.14.98-.275c.223-.1.419-.253.57-.446a1.45 1.45 0 0 0 .266-.626q.066-.419.064-.844v-.51h-7.045v-3.544h12.158v4.078c.009.777-.049 1.554-.171 2.322a5 5 0 0 1-.621 1.724c-.3.485-.71.894-1.195 1.195a6.4 6.4 0 0 1-1.924.76q-1.204.273-2.436.374l-.351.025q-.349.025-.72.046l-.508.024l-.262.01l-.54.017q-.414.012-.852.017l-.596.005zm19.602-.19h-5.38v-18.224h5.38zM20.573 180.86l-1.372.006l-.77-.002l-.38-.003l-.741-.008q-.549-.009-1.077-.021l-.694-.019l-.674-.023l-.656-.028l-.636-.031l-.31-.018l-.607-.038l-.297-.02a31.6 31.6 0 0 1-5.073-.713a12.1 12.1 0 0 1-3.533-1.37a6.9 6.9 0 0 1-2.234-2.167a8.7 8.7 0 0 1-1.175-3.098a22.4 22.4 0 0 1-.342-4.197V148.4H9.44v17.65q0 .756.025 1.413l.019.427q.021.416.055.788l.017.184a6.8 6.8 0 0 0 .466 1.991c.215.527.565.989 1.015 1.338c.527.379 1.124.65 1.756.797a13.5 13.5 0 0 0 2.386.38l.519.03l.448.02l.47.018l.491.015l.513.011l.535.009l.558.005l.58.001h.796l.579-.001l.556-.006l.27-.004l.524-.011l.254-.007l.492-.017l.237-.01l.459-.021l.22-.013l.216-.013a15 15 0 0 0 2.692-.378a4.7 4.7 0 0 0 1.757-.797a3.4 3.4 0 0 0 1.011-1.338a6.7 6.7 0 0 0 .47-1.991q.111-1.195.112-2.788v-17.686h9.442v20.709a24.5 24.5 0 0 1-.319 4.185a8.6 8.6 0 0 1-1.143 3.11a6.8 6.8 0 0 1-2.21 2.167a12 12 0 0 1-3.524 1.37a31.6 31.6 0 0 1-4.665.685l-.728.048l-.613.037l-.632.034l-.324.015l-.661.027l-.682.023l-.7.02l-.72.014l-.368.006l-.75.01zm67.34-.388H73.8l-18.582-24.014h-.183v24.014H45.78v-32.119h14.336l18.355 24.038h.18v-24.038h9.255v32.103zm16.062-15.902h11.764l.479-.002l.458-.004l.439-.007l.419-.01l.201-.007l.39-.014l.368-.018l.35-.02l.167-.012l.32-.025l.3-.029a5.3 5.3 0 0 0 2.198-.625c.485-.292.836-.762.98-1.31c.171-.73.249-1.477.23-2.226v-.554a8.7 8.7 0 0 0-.23-2.198a2.07 2.07 0 0 0-.992-1.29a5.5 5.5 0 0 0-2.21-.602l-.3-.028l-.319-.025l-.167-.012l-.348-.02l-.367-.018l-.386-.015l-.406-.011l-.425-.01l-.445-.005l-.465-.003h-12.003zm28.57 15.902h-9.327v-2.605q.01-1.214-.112-2.421a4.9 4.9 0 0 0-.481-1.717a2.94 2.94 0 0 0-1.024-1.127a5.2 5.2 0 0 0-1.744-.657a17 17 0 0 0-2.668-.31l-.215-.011l-.446-.02l-.23-.008l-.478-.015l-.498-.012l-.52-.009l-.267-.003l-.55-.005h-.283l-9.727-.001v8.92h-9.35v-32.118h24.901a35.4 35.4 0 0 1 6.025.417l.427.07a9.2 9.2 0 0 1 3.982 1.624a5.86 5.86 0 0 1 2.02 3.019c.404 1.513.591 3.077.557 4.643v1.127a16.5 16.5 0 0 1-.295 3.31a7.2 7.2 0 0 1-.96 2.44a5.6 5.6 0 0 1-1.708 1.693a8.1 8.1 0 0 1-2.577 1.016v.183a13.8 13.8 0 0 1 2.768.705a3.7 3.7 0 0 1 1.7 1.266a5.1 5.1 0 0 1 .845 2.203c.168 1.15.244 2.313.227 3.476v4.91zm41.015 0h-34.886v-32.119h34.336v7.1h-24.99v5.46h23.668v6.707h-23.667v5.532h25.539zm31.54-12.442l-6.542-12.883h-.231l-6.496 12.883zm16.52 12.465h-10.18l-2.942-5.762h-20.02l-2.895 5.762h-10.104l17.24-32.098h11.585zm34.38 0h-30.92v-32.098h9.439v24.647H256zM128 0a64.937 64.937 0 0 1 64.946 64.937c.002 35.867-29.071 64.944-64.937 64.946s-64.943-29.071-64.946-64.938C63.061 29.438 91.556.585 126.927.01zm23.854 7.338c-23.297-9.65-50.113-4.315-67.943 13.516C66.081 38.686 60.748 65.502 70.399 88.8s32.385 38.485 57.602 38.483c34.43-.002 62.34-27.914 62.34-62.345c0-25.216-15.19-47.95-38.487-57.6m-29.743 18.3c-5.436 3.1-8.495 8.157-8.495 12.402c0 5.13 2.336 5.937 4.008 5.592l.201-.047l.098-.028l.189-.062l.09-.035l.175-.074l.082-.04l.156-.083l.143-.088l.129-.09q.03-.023.058-.047v39.394c.206.495.473.962.796 1.39a5.81 5.81 0 0 0 4.767 2.405c1.696 0 3.599-.796 5.25-1.734l.465-.27l.45-.276l.43-.276l.41-.274l.386-.268l.36-.258l.636-.475l.505-.397l.356-.291l.21-.18V49.63c0-3.246-2.445-7.168-4.894-8.506l.338-.046l.396-.035l.38-.021l.445-.01h.161l.34.008l.178.008l.37.023q.286.022.59.06l.412.06c1.325.213 2.837.687 4.21 1.669l.217.16a30 30 0 0 1 2.094-2.307c5.718-5.617 11.21-8.41 16.191-9.97l.744-.225l.368-.106l.732-.2q.363-.095.723-.183l.714-.17l.706-.157l.697-.144l1.03-.197l.337-.061l-.417.346l-.599.526l-.38.348l-.425.403l-.466.456l-.502.508l-.351.367l-.363.388l-.372.41l-.381.432l-.387.452l-.392.473l-.396.492l-.198.254l-.398.52q-.397.532-.79 1.1l-.39.576q-.194.293-.384.594l-.377.61c-2.05 3.408-3.688 7.57-3.688 12.17l.022 6.304l.213 25.094c2.574 2.472 5.883 1.359 9.362-1.204l.465-.35l.233-.181l.467-.374l.235-.193l.469-.394l.234-.203l.47-.413l.471-.425l.706-.655l.705-.673l.693-.677l.69-.687l.457-.463l.91-.93l-.076.352l-.087.374l-.15.6l-.115.424l-.127.443l-.14.46l-.152.479l-.166.494l-.179.51l-.193.524l-.207.538l-.223.551l-.237.564l-.125.286l-.26.58l-.278.59l-.294.598l-.153.303l-.32.611l-.166.309l-.345.621c-3.254 5.728-8.794 12.2-17.986 16.543l-6.372-7.168l-10.753 10.816a39.71 39.71 0 0 1-31.405-16.109c1.144.356 2.325.578 3.52.661c1.76.032 3.668-.613 3.668-3.584V56.479a4.803 4.803 0 0 0-6.045-4.807c-2.451.56-4.66 3.858-6.272 7.061l-.295.599l-.28.592l-.266.582l-.25.568l-.234.548l-.217.526l-.2.499l-.347.899l-.272.741l-.328.953a39.53 39.53 0 0 1 13.684-30.29c6.507-5.515 12.883-7.865 18.066-8.933l.715-.141q.177-.034.352-.065l.69-.118z"/></svg>'''] 
    tags = ['Programming']
    githublink = 'example.com'

    compile(name, short_name, long_name, image_path, description, techs, 'file.txt', tags, githublink, '')

# {
#     "projectShortTitle": "Testing",
#     "projectLongTitle": "Testing project!",
#     "projectImage": "<img class='img-responsive' src='https://via.placeholder.com/150'>",
#     "projectDescription": "<p>This is a project that contains no S3 images, for testing purposes</p>",
#     "applicableTechnologies": [
#         "<svg xmlns='http://www.w3.org/2000/svg' width='5em' height='5em' viewBox='0 0 256 256'><g fill='none'><rect width='256' height='256' fill='#00979c' rx='60'/><path fill='#fff' fill-rule='evenodd' d='M19 136.512v-16.417c.344-.171.344-.513.344-.855c5.163-22.402 19.276-35.912 41.65-41.214c1.893-.513 3.958-.342 5.852-1.026H77.86c.172.342.689.171 1.033.171c11.015 1.197 20.997 5.13 29.774 11.971c7.573 5.643 13.425 12.826 18.76 20.521c.688 1.026 1.033 1.026 1.721 0c3.098-4.446 6.368-8.721 10.154-12.654c9.122-9.748 20.137-16.589 33.561-18.983c1.893-.513 4.13-.342 6.024-1.026h10.67c.172.342.517.171.861.171c3.27.342 6.368 1.026 9.466 1.881c23.062 6.67 39.412 27.704 38.035 51.475c-1.033 20.009-11.187 34.374-28.914 43.437c-8.777 4.789-18.415 5.986-28.397 5.815c-13.08-.171-24.439-4.618-34.249-13.168c-6.885-5.986-12.22-13.168-17.211-20.693c-.688-1.026-1.033-.855-1.721.171c-3.098 4.618-6.368 9.235-10.154 13.681c-6.712 7.525-14.457 13.681-24.095 16.931c-11.876 4.104-23.923 4.275-35.97 1.026c-17.383-4.96-29.258-15.905-35.798-32.664c-1.033-2.736-1.55-5.814-2.41-8.551m54.73 25.139c9.81.342 18.243-2.907 25.471-9.576c7.401-6.841 12.736-15.392 18.072-23.771c.172-.513.172-.855-.172-1.368c-4.475-7.012-9.122-14.023-15.318-19.838c-11.875-11.287-25.816-15.049-41.477-10.09c-12.908 4.276-21.17 13.339-23.063 27.02c-1.893 12.826 3.098 23.087 13.424 30.783c6.885 4.959 14.63 7.011 23.063 6.84m109.115 0c3.786 0 7.573-.171 11.187-1.197c13.596-4.104 22.546-12.484 25.128-26.507c2.581-13.852-2.754-24.968-14.457-32.834c-12.908-8.893-31.668-8.038-44.748 1.71c-8.777 6.498-14.629 15.22-20.481 24.284c-.344.513-.172.855 0 1.368c4.647 7.353 9.294 14.707 15.318 21.034c7.572 8.038 16.694 12.655 28.053 12.142' clip-rule='evenodd'/><path fill='#fff' fill-rule='evenodd' d='M73.558 122.831c5.507 0 11.187.171 16.694 0c1.377 0 1.549.342 1.549 1.71a20.7 20.7 0 0 0 0 4.618c.172 1.368-.172 1.71-1.721 1.71H68.05c-3.786 0-7.572-.171-11.359 0c-1.205 0-1.549-.342-1.549-1.71c.172-1.539.172-3.078 0-4.789c0-1.197.344-1.539 1.55-1.539c5.507.171 11.186 0 16.866 0m108.427-10.945c1.376 0 2.753.171 3.958 0c.861 0 1.205.342 1.205 1.197c-.172 2.395 0 4.789-.172 7.183c0 1.197.344 1.539 1.549 1.539c2.237-.171 4.647 0 7.056-.171c1.033 0 1.377.171 1.377 1.368v7.867c0 .855-.344 1.197-1.205 1.197c-2.409-.171-4.819 0-7.4-.171c-1.033 0-1.377.342-1.377 1.368c.172 2.394 0 4.788.172 7.183c0 1.026-.344 1.539-1.377 1.539a58.5 58.5 0 0 0-7.745 0c-1.032 0-1.377-.342-1.377-1.368c.172-2.566 0-4.96.172-7.525c0-.855-.344-1.197-1.204-1.197c-2.41.171-4.819 0-7.229.171c-1.377 0-1.549-.513-1.549-1.539c0-2.394.172-4.789 0-7.183c-.172-1.368.517-1.71 1.721-1.71c2.41.171 4.647 0 7.057.171c.86 0 1.204-.342 1.204-1.197c-.172-2.394 0-4.959-.172-7.353c0-1.027.345-1.369 1.377-1.369c1.377.171 2.582 0 3.959 0' clip-rule='evenodd'/></g></svg>"
#     ],
#     "projectText": "<p>HELLO! THIS IS SOME TESTING TEXT</p>",
#     "tags": [
#         "Robotics",
#         "AI",
#         "Computer Vision",
#         "Programming"
#     ],
#     "githubLink": "https://github.com/lganic/Ai-tic-tac-toe-project"
# }