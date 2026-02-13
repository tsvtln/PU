function parseErrorMessage(data) {
  let errorMessage = "";
  let tf = "Execute get_vm_tag.py script";

  let dataList = data.split('\\n');

  if (dataList.length === 1) {
    dataList = data.split('\\n');
  }

  for (let i = 0; i < dataList.length; i++){
      if (dataList[i].includes(tf)) {
          errorMessage = dataList[i+2];
          break;
      }
  }


  return errorMessage;

  return errorMessageClean.join(' ');
}
const data_raw = $input.first().json.data;
const errorMessage = parseErrorMessage(data_raw);
return [{ json: { errorMessage } }];
