import format from "date-fns/format";
import parse from "date-fns/parse";
import lastDayOfMonth from 'date-fns/lastDayOfMonth';
import startOfMonth from 'date-fns/startOfMonth';
import addDays from 'date-fns/addDays'

function isoDateFormat(date) {
  return format(date, "yyyy-MM-dd");
}

function ymDateFormat(date) {
  return format(date, "yyyy-MM");
}

function parseDateTime(text) {
  return parse(text, "yyyy-MM", new Date());
}

function isoDateTimeFormat(date) {
  return format(date, "yyyy-MM-dd HH:mm:ss");
}

function firstOfTheMonthFromIso(isoStr) {
  let date = startOfMonth(new Date(isoStr))
  return {
    readable: format(date, 'dd.MM.yyyy'),
    api: format(date, 'yyyy-MM-dd'),
  }
}

function lastOfTheMonthFromIso(isoStr) {
  let date = lastDayOfMonth(new Date(isoStr))
  return {
    readable: format(date, 'dd.MM.yyyy'),
    api: format(addDays(date, 1), 'yyyy-MM-dd'),
  }
}

export {
  isoDateFormat,
  ymDateFormat,
  parseDateTime,
  isoDateTimeFormat,
  firstOfTheMonthFromIso,
  lastOfTheMonthFromIso
};
