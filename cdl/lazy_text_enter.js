// == USAGE ==
// Generate exactly 500 characters
// document.querySelector('input').value = generateLoremChars(500);
//
// For textarea
// document.querySelector('textarea').value = generateLoremChars(500);
//
// with event trigger for reactive forms
// const input = document.querySelector('input, textarea');
// input.value = generateLoremChars(500);
// input.dispatchEvent(new Event('input', { bubbles: true }));

function generateLoremChars(charCount) {
    const lorem = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum. Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo.";

    // Repeat Lorem text until we have enough characters
    let result = lorem;
    while (result.length < charCount) {
        result += " " + lorem;
    }

    // Trim to exact character count
    return result.substring(0, charCount);
}

