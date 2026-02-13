function getVariables(data) {
  let varMessage = "";
  let tf = "Output result as JSON";
  let dataList = data.split('\\n');

  for (let i = 0; i < dataList.length; i++){
      if (dataList[i].includes(tf)) {
          varMessage = dataList[i+3];
          break;
      }
  }
  varMessage = (((varMessage.replace(/&quot;/g, '')).replace(/\\/g, '')).trim()).split(' ');
  varMessage[1].trim();

  return varMessage;

  let errorMessageClean = errorMessage.split(' ').map((v, i) =>
      i === 2 ? v.split(';')[1].split('&')[0] :
      i === 6 ? v.replace(/[\\]/g, '') :
      v
    );

  return errorMessageClean.join(' ');
}


// const data_raw = ;

const variables = getVariables(data_raw);
// return [{ json: { errorMessage } }];