// project_loader.js

// Function to get URL parameters
function getUrlParams() {
    const params = {};
    window.location.search.substring(1).split("&").forEach(pair => {
        const [key, value] = pair.split("=");
        if (key) {
            params[decodeURIComponent(key)] = decodeURIComponent(value || '');
        }
    });
    return params;
}

// Function to populate the HTML with JSON data
function populateProject(data) {
    // Update the <title>
    if (data.projectShortTitle) {
        document.title = data.projectShortTitle;
    }

    // Update navbar title
    const navbarTitle = document.getElementById('navbar-title');
    if (navbarTitle && data.projectShortTitle) {
        navbarTitle.textContent = data.projectShortTitle;
    }

    // Update project long title
    const projectLongTitle = document.getElementById('project-long-title');
    if (projectLongTitle && data.projectLongTitle) {
        projectLongTitle.textContent = data.projectLongTitle;
    }

    // Update project image
    const projectImage = document.getElementById('project-image');
    if (projectImage && data.projectImage) {
        projectImage.innerHTML = data.projectImage;
    }

    // Update project description
    const projectDescription = document.getElementById('project-description');
    if (projectDescription && data.projectDescription) {
        projectDescription.innerHTML = data.projectDescription;
    }

    // Update applicable technologies
    const applicableTechnologies = document.getElementById('applicable-technologies');
    if (applicableTechnologies && data.applicableTechnologies) {
        applicableTechnologies.innerHTML = data.applicableTechnologies.join(' ');
    }

    // Update project text
    const projectText = document.getElementById('project-text');
    if (projectText && data.projectText) {
        projectText.innerHTML = data.projectText;
    }
}

// Main function to load the project data
async function loadProject() {
    const params = getUrlParams();
    let jsonFile = params['project'];

    if (!jsonFile) {
        console.error("No 'project' parameter found in the URL.");
        return;
    }

    if(!('local' in params)){

        jsonFile = 'https://logan-public-files.s3.us-east-2.amazonaws.com/projects/' + jsonFile

    }

    try {
        const response = await axios.get(jsonFile);
        const data = response.data;
        populateProject(data);
    } catch (error) {
        console.error("Error loading the project JSON file:", error);
    }
}

// Execute the main function after the DOM is fully loaded
document.addEventListener('DOMContentLoaded', loadProject);
