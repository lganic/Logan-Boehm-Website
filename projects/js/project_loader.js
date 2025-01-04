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
        projectImage.children[0].id = 'img-id';
        projectImage.children[0].classList.add('proj-image');
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

    // Add tags
    if (data.tags){
        data.tags.forEach((tag) => addTagElement(tag));
    }

    // Add github link (if it exists)
    const githubDiv = document.getElementById('github-link');
    if (githubDiv && data.githubLink){
        githubDiv.innerHTML = `<a href="${data.githubLink}" target="_blank"><img style="width:80%" src="https://img.shields.io/badge/GitHub-Source Code Here-blue?style=social&logo=github" alt="GitHub link">`
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

    adjustImageHeight();
}

// Execute the main function after the DOM is fully loaded
document.addEventListener('DOMContentLoaded', loadProject);

function adjustImageHeight() {

    const img = document.getElementById('img-id'); 

    if (img){
        img.onload = function () {
            const div = document.getElementById('description-div');
            const img_holder = document.getElementById('project-image');
        
            if (!(div && img && img_holder)) {
                return;
            }
        
            const regular_width = img.naturalWidth;
            const regular_height = img.naturalHeight;
        
            // Attempt to fit heightwise
            let calc_width = div.offsetHeight * regular_width / regular_height;
        
            if (calc_width < img_holder.offsetWidth){
                // Itll fit!
                img.style.height = `${div.offsetHeight}px`;
                img.style.width = `${calc_width}px`;

                missing_width = img_holder.offsetWidth - calc_width;

                img.style.marginLeft = `${missing_width / 2}px`;

                return;
            }

            // Fit Widthwise

            let calc_height = img_holder.offsetWidth * regular_height / regular_width;

            img.style.width = `${img_holder.offsetWidth}px`;
            img.style.height = `${calc_height}px`;

            missing_height = div.offsetHeight - calc_height;

            img.style.marginTop = `${missing_height / 2}px`;
        }

        // If the image is already loaded (e.g., cached), trigger the function immediately
        if (img.complete) {
            img.onload();
        }
    }

}

// Trigger on window resize
window.onresize = adjustImageHeight;
