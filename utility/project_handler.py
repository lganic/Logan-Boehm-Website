from s3_utils import S3Wrapper
from typing import List
import os
from project_compiler import LinkCompiler

BUCKET_NAME = 'logan-public-files'

def ensure_proj_formatting(project_name: str):

    project_name = os.path.basename(project_name)

    if not project_name.endswith('.json'):
        project_name += '.json'

    if project_name == 'projects.json':
        raise ValueError('This project name is reserved for system functionality. Please pick a different one')

    return project_name

class ProjectHandler:
    def __init__(self, bucket_name = BUCKET_NAME, profile = 'personal'):

        self.client = S3Wrapper(bucket_name, profile_name=profile)

        self.link_compiler = LinkCompiler(self.client, bucket_name)

    def list_projects(self):

        all_paths: List[str] = self.client.list_directory('projects')[1:]

        return [path.partition('projects/')[2] for path in all_paths]

    def pull_project(self, project_name):

        project_name = ensure_proj_formatting(project_name)

        download_to_location = os.path.join('../projects', project_name)

        download_from_location = os.path.join('projects', project_name)

        self.client.download_file(download_from_location, download_to_location)
    
    def upload_project(self, project_name):

        project_name = ensure_proj_formatting(project_name)

        upload_from_location = os.path.join('../projects', project_name)

        upload_to_location = os.path.join('projects', project_name)

        self.client.upload_file(upload_from_location, upload_to_location)
    
if __name__ == '__main__':
    
    handler = ProjectHandler()

    print(handler.list_projects())