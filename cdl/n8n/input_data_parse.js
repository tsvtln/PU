function parseErrorMessage(data) {
  let errorMessage = "";
  let tf = "Execute get_vm_tag.py script";
  let dataList = data.split('\\n');

  for (let i = 0; i < dataList.length; i++){
      if (dataList[i].includes(tf)) {
          errorMessage = dataList[i+3];
          break;
      }
  }

  let errorMessageClean = errorMessage.split(' ').map((v, i) =>
      i === 2 ? v.split(';')[1].split('&')[0] :
      i === 6 ? v.replace(/[\\]/g, '') :
      v
    );

  return errorMessageClean.join(' ');
}


const fs = require('fs');
const data_raw = fs.readFileSync('C:\\pjs\\tsvtln_bin\\trash\\stps.out', 'utf8');

const errorMessage = parseErrorMessage(data_raw);
console.log(errorMessage);
