import numeral from "numeral";

function formatInteger(integer) {
  if (integer == null) {
    return "-";
  }
  return numeral(integer).format("0,0").replace(/,/g, "\xa0");
}

function labelKFormatter(val) {
  return numeral(val).format("0.[0]a");
}

function formatFloat(num, decimalPlaces) {
  if (!decimalPlaces) decimalPlaces = 1;
  return numeral(num).format(`0.[${"0".repeat(decimalPlaces)}]`);
}

function format2SignificantPlaces(num) {
  if (!num) return 0;
  if (num > 9) return formatInteger(num);
  if (num >= 1) return numeral(num).format("0.[0]");
  let strNum = String(num);
  let numSignificant = 0;
  let result = "0.";
  for (let ch of strNum.slice(2)) {
    if (numSignificant == 0 || ch != "0") result += ch;
    if (numSignificant > 0) return result;
    numSignificant += 1;
  }
}

function ensureInt(inp) {
  if (typeof inp === "string") {
    return Number.parseInt(inp, 10);
  }
  return inp;
}

export {
  formatInteger,
  formatFloat,
  format2SignificantPlaces,
  ensureInt,
  labelKFormatter,
};
