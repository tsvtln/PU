
// Get all spans with both classes and text exactly "00MigrationScript"
const matches = Array.from(
  document.querySelectorAll('span.text-ellipsis.flex-self-center')
).filter(el => el.textContent.trim());

// If you just need their text:
const texts = matches.map(el => el.textContent.trim());

// If you need their outerHTML:
// const html = matches.map(el => el.outerHTML);

// Inspect result
console.log(matches);
console.log(texts);
// console.log(html);
