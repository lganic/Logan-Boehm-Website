function addTagElement(tag) {
    // Hashing function to convert a string into a consistent numeric hash
    function hashString(str) {
        let hash = 0x811C9DC5; // FNV offset basis (arbitrary non-zero value)
        const prime = 0x01000193; // FNV prime (constant for good distribution)
        
        for (let i = 0; i < str.length; i++) {
            hash ^= str.charCodeAt(i); // XOR with the current character
            hash = (hash * prime) >>> 0; // Multiply by a prime and ensure a non-negative result
        }
        return hash;
    }

    // Convert hash to HSB and generate a color
    function hashToHSBColor(tagHash) {
        const hue = tagHash % 256; // Hue value between 0-255
        const saturation = 100; // Full saturation
        const brightness = 100; // Full brightness
        return { hue, saturation, brightness };
    }

    // Convert HSB to RGB
    function hsbToRgb(h, s, b) {
        s /= 100;
        b /= 100;

        const k = (n) => (n + h / 60) % 6;
        const f = (n) =>
            b * (1 - s * Math.max(0, Math.min(k(n), 4 - k(n), 1)));

        return [
            Math.round(f(5) * 255), // Red
            Math.round(f(3) * 255), // Green
            Math.round(f(1) * 255), // Blue
        ];
    }

    // Calculate the brightness of an RGB color
    function getBrightness(rgb) {
        // Using perceived brightness formula: 0.299*R + 0.587*G + 0.114*B
        return 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2];
    }

    // Choose text color (black or white) based on brightness
    function chooseTextColor(rgb) {
        const brightness = getBrightness(rgb);
        // If the brightness of the inverse color is closer to black, use white text; otherwise, use black.
        return brightness > 128 ? '#000' : '#fff';
    }

    function toTitleCase(str) {
        return str.split(' ').map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()).join(' ');
    }

    // Create the tag element with the appropriate color
    const tagHash = hashString(tag.toLowerCase().replace(" ", ""));
    const { hue, saturation, brightness } = hashToHSBColor(tagHash);

    const bgColorRgb = hsbToRgb(hue, saturation, brightness);
    const textColor = chooseTextColor(bgColorRgb);

    const tagElement = document.createElement('span');
    tagElement.textContent = toTitleCase(tag);
    tagElement.style.backgroundColor = `rgb(${bgColorRgb.join(",")})`;
    tagElement.style.color = textColor;
    tagElement.style.padding = '5px 10px';
    tagElement.style.margin = '5px';
    tagElement.style.borderRadius = '15px';
    tagElement.style.display = 'inline-block';

    // Add the tag element to the desired container
    const container = document.getElementById('tags-container'); // Ensure you have an element with id 'tags-container'
    if (container) {
        container.appendChild(tagElement);
    } else {
        console.error('Container element not found!');
    }
}

// Example usage
// addTagElement('example tag');
// addTagElement('Example Tag');
// addTagElement('anotherTag');
// addTagElement('robotics');
// addTagElement('a');
// addTagElement('b');
// addTagElement('c');
// addTagElement('d');
// addTagElement('d');
// addTagElement('d');
// addTagElement('g');