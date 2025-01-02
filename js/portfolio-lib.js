

// S3 Configuration
const bucketName = 'logan-public-files';
const region = 'us-east-2';
const folderPrefix = 'projects/';
const s3Endpoint = `https://${bucketName}.s3.${region}.amazonaws.com/`;

// Fetch and display project data
async function fetchAndDisplayProjects() {
    try {
        // Fetch list of JSON files from S3
        const url = `${s3Endpoint}?list-type=2&prefix=${encodeURIComponent(folderPrefix)}`;
        const response = await fetch(url, {
            method: 'GET',
            headers: { 'Content-Type': 'application/xml' },
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const textData = await response.text();
        const parser = new DOMParser();
        const xml = parser.parseFromString(textData, "application/xml");
        const contents = xml.getElementsByTagName("Contents");

        const jsonFiles = [];
        for (let i = 0; i < contents.length; i++) {
            const key = contents[i].getElementsByTagName("Key")[0].textContent;
            if (key.endsWith('.json') && key !== folderPrefix) {
                jsonFiles.push(key);
            }
        }

        // Fetch and display each JSON file's content
        const projectContainer = document.querySelector('.grid');
        for (const fileKey of jsonFiles) {
            const jsonUrl = `${s3Endpoint}${encodeURIComponent(fileKey)}`;
            let projectData = await fetchProjectData(jsonUrl);
            projectData['jsonname'] = fileKey;
            if (projectData) {
                addProjectToGrid(projectContainer, projectData);
            }
        }

        // init Masonry
        var $grid = $('.grid').masonry({
          itemSelector: '.grid-item',
          percentPosition: true,
          columnWidth: '.grid-sizer'
        });
        // layout Masonry after each image loads
        $grid.imagesLoaded().progress( function() {
          $grid.masonry();
        });  

    } catch (error) {
        console.error('Error fetching or displaying projects:', error);
    }
}

// Fetch individual project data
async function fetchProjectData(jsonUrl) {
    try {
        const response = await fetch(jsonUrl);
        if (!response.ok) {
            throw new Error(`Failed to fetch JSON: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error(`Error fetching project JSON from ${jsonUrl}:`, error);
        return null;
    }
}

// Add a project to the grid
function addProjectToGrid(container, data) {
    if (!data.projectLongTitle || !data.projectImage || !data.projectDescription) {
        console.warn('Missing required project data:', data);
        return;
    }

    // console.log(data['jsonname'].replace('/', '.html?project='));

    const projectElement = document.createElement('a');

    if(data.forceHref){
      projectElement.href = data['forceHref'];
    }
    else{
      projectElement.href = data['jsonname'].replace('/', '/project.html?project=');
    }

    const gridItem = document.createElement('div');
    gridItem.className = 'grid-item';

    const imageContainer = document.createElement('div');
    imageContainer.className = 'image-container';

    imageContainer.innerHTML = data.projectImage;

    const titleOverlay = document.createElement('div');
    titleOverlay.className = 'title-overlay';
    titleOverlay.innerHTML = `<h2>${data.projectLongTitle}</h2>`;

    const descriptionOverlay = document.createElement('div');
    descriptionOverlay.className = 'description-overlay';
    descriptionOverlay.innerHTML = `<h2>${data.projectLongTitle}</h2>${data.projectDescription}`;

    imageContainer.appendChild(titleOverlay);
    imageContainer.appendChild(descriptionOverlay);
    gridItem.appendChild(imageContainer);
    projectElement.appendChild(gridItem);
    container.appendChild(projectElement);
}

// Call the main function on page load
document.addEventListener('DOMContentLoaded', fetchAndDisplayProjects);


// // init Masonry
// var $grid = $('.grid').masonry({
//   itemSelector: '.grid-item',
//   percentPosition: true,
//   columnWidth: '.grid-sizer'
// });
// // layout Masonry after each image loads
// $grid.imagesLoaded().progress( function() {
//   $grid.masonry();
// });  
