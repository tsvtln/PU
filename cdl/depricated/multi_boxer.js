// Script to select all checkboxes on a webpage
// This can be run in browser console or as a bookmarklet

function selectAllCheckboxes() {
    // Find all checkbox inputs on the page
    const checkboxes = document.querySelectorAll('input[type="checkbox"]');
    
    console.log(`Found ${checkboxes.length} checkboxes on the page`);
    
    // Check each checkbox
    checkboxes.forEach((checkbox, index) => {
        if (!checkbox.checked) {
            checkbox.checked = true;
            
            // Trigger change event in case there are event listeners
            const event = new Event('change', { bubbles: true });
            checkbox.dispatchEvent(event);
            
            console.log(`Checked checkbox ${index + 1}: ${checkbox.name || checkbox.id || 'unnamed'}`);
        } else {
            console.log(`Checkbox ${index + 1} was already checked: ${checkbox.name || checkbox.id || 'unnamed'}`);
        }
    });
    
    console.log('All checkboxes have been selected!');
}

// Alternative function to select checkboxes with specific patterns
function selectCheckboxesByPattern(pattern) {
    // Find checkboxes matching a specific name pattern (like "checkrow")
    const selector = `input[type="checkbox"][name*="${pattern}"]`;
    const checkboxes = document.querySelectorAll(selector);
    
    console.log(`Found ${checkboxes.length} checkboxes matching pattern "${pattern}"`);
    
    checkboxes.forEach((checkbox, index) => {
        if (!checkbox.checked) {
            checkbox.checked = true;
            
            // Trigger change event
            const event = new Event('change', { bubbles: true });
            checkbox.dispatchEvent(event);
            
            console.log(`Checked checkbox: ${checkbox.name}`);
        }
    });
    
    console.log(`All checkboxes matching "${pattern}" have been selected!`);
}

// Function to uncheck all checkboxes
function unselectAllCheckboxes() {
    const checkboxes = document.querySelectorAll('input[type="checkbox"]');
    
    console.log(`Found ${checkboxes.length} checkboxes to uncheck`);
    
    checkboxes.forEach((checkbox, index) => {
        if (checkbox.checked) {
            checkbox.checked = false;
            
            // Trigger change event
            const event = new Event('change', { bubbles: true });
            checkbox.dispatchEvent(event);
            
            console.log(`Unchecked checkbox ${index + 1}: ${checkbox.name || checkbox.id || 'unnamed'}`);
        }
    });
    
    console.log('All checkboxes have been unselected!');
}

// Function to toggle all checkboxes
function toggleAllCheckboxes() {
    const checkboxes = document.querySelectorAll('input[type="checkbox"]');
    
    console.log(`Toggling ${checkboxes.length} checkboxes`);
    
    checkboxes.forEach((checkbox, index) => {
        checkbox.checked = !checkbox.checked;
        
        // Trigger change event
        const event = new Event('change', { bubbles: true });
        checkbox.dispatchEvent(event);
        
        console.log(`Toggled checkbox ${index + 1}: ${checkbox.name || checkbox.id || 'unnamed'} - now ${checkbox.checked ? 'checked' : 'unchecked'}`);
    });
    
    console.log('All checkboxes have been toggled!');
}

// Function specifically for checkrow0 to checkrow19 checkboxes
function selectAllCheckrowBoxes() {
    let checkedCount = 0;
    
    // Loop through checkrow0 to checkrow19
    for (let i = 0; i <= 19; i++) {
        const checkboxName = `checkrow${i}`;
        const checkbox = document.querySelector(`input[name="${checkboxName}"]`);
        
        if (checkbox) {
            if (!checkbox.checked) {
                checkbox.checked = true;
                
                // Trigger change event
                const event = new Event('change', { bubbles: true });
                checkbox.dispatchEvent(event);
                
                console.log(`Checked: ${checkboxName}`);
                checkedCount++;
            } else {
                console.log(`Already checked: ${checkboxName}`);
            }
        } else {
            console.log(`Not found: ${checkboxName}`);
        }
    }
    
    console.log(`\nCheckrow Summary: ${checkedCount} checkboxes were newly checked`);
    return checkedCount;
}

// Function to uncheck all checkrow0-checkrow19 boxes
function unselectAllCheckrowBoxes() {
    let uncheckedCount = 0;
    
    for (let i = 0; i <= 19; i++) {
        const checkboxName = `checkrow${i}`;
        const checkbox = document.querySelector(`input[name="${checkboxName}"]`);
        
        if (checkbox && checkbox.checked) {
            checkbox.checked = false;
            
            // Trigger change event
            const event = new Event('change', { bubbles: true });
            checkbox.dispatchEvent(event);
            
            console.log(`Unchecked: ${checkboxName}`);
            uncheckedCount++;
        }
    }
    
    console.log(`\nUnchecked ${uncheckedCount} checkrow boxes`);
    return uncheckedCount;
}

// Main execution - select all checkboxes
console.log('Starting checkbox selection script...');

// Use the specific checkrow function for your use case
console.log('Targeting checkrow0 through checkrow19...');
selectAllCheckrowBoxes();

// If you want to select ALL checkboxes instead, uncomment the line below:
// selectAllCheckboxes();

// If you want to target specific checkboxes like "checkrow", uncomment the line below:
// selectCheckboxesByPattern('checkrow');

// Usage instructions:
console.log(`
=== USAGE INSTRUCTIONS ===
1. Copy and paste this script into your browser's developer console (F12)
2. Or use these functions individually:
   - selectAllCheckboxes()           // Check ALL checkboxes on page
   - selectAllCheckrowBoxes()        // Check only checkrow0-checkrow19
   - unselectAllCheckrowBoxes()      // Uncheck only checkrow0-checkrow19
   - unselectAllCheckboxes()         // Uncheck ALL checkboxes  
   - toggleAllCheckboxes()           // Toggle ALL checkboxes
   - selectCheckboxesByPattern('checkrow')  // Check checkboxes containing 'checkrow'

=== QUICK BOOKMARKLETS ===
All checkboxes:
javascript:(function(){document.querySelectorAll('input[type="checkbox"]').forEach(cb=>{cb.checked=true;cb.dispatchEvent(new Event('change',{bubbles:true}));});})();

Only checkrow0-19:
javascript:(function(){for(let i=0;i<=19;i++){const cb=document.querySelector('input[name="checkrow'+i+'"]');if(cb){cb.checked=true;cb.dispatchEvent(new Event('change',{bubbles:true}));}}})();
`);