// START test input values 
inputData = {
    "interval":"year"
}
// END test input values 
var dateFormat;
switch(inputData.interval){
    case "month":
        dateFormat = "D MMM";
        break;
    case "year":
        dateFormat = "D MMM YYYY";
        break;
    default:
        dateFormat = "D MMM";
}
output = [{dateFormat: dateFormat}];