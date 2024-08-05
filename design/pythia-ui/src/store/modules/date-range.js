import addMonths from "date-fns/addMonths";
import addYears from "date-fns/addYears";
import endOfYear from "date-fns/endOfYear";
import startOfYear from "date-fns/startOfYear";
import { isoDateFormat, parseDateTime } from "@/libs/dates";
import startOfMonth from "date-fns/startOfMonth";
import endOfMonth from "date-fns/endOfMonth";

export default {
  state: {
    dateRangeStart: null,
    dateRangeEnd: null,
    dateRangeIndex: 0,
    dateRanges: [
      { name: "date_range.all_available", start: null, end: null },
      { name: "date_range.last_12_mo", start: -12, end: 0 },
      {
        name: "date_range.previous_year",
        start: startOfYear(addYears(new Date(), -1)),
        end: endOfYear(addYears(new Date(), -1)),
      },
      { name: "date_range.custom", custom: true },
    ],
  },

  getters: {
    selectedDateRange: (state) => state.dateRanges[state.dateRangeIndex],
    dateRangeStartText(state) {
      if (state.dateRangeStart) {
        return isoDateFormat(state.dateRangeStart);
      }
      return "";
    },
    dateRangeEndText(state) {
      if (state.dateRangeEnd) {
        return isoDateFormat(state.dateRangeEnd);
      }
      return "";
    },
    dateRangeQueryParams(state, getters) {
      return {
        start_date: getters.dateRangeStartText,
        end_date: getters.dateRangeEndText,
      };
    },
  },

  actions: {
    changeDateRangeObject(context, dateRangeIndex) {
      let drObj = context.state.dateRanges[dateRangeIndex];
      let start = null;
      let end = null;
      if (!drObj.custom) {
        // for custom specified, we do not do anything with the start and end
        if (drObj.start !== null) {
          if (typeof drObj.start === "number") {
            start = addMonths(new Date(), drObj.start);
          } else {
            start = drObj.start;
          }
        }
        if (drObj.end !== null) {
          if (typeof drObj.end === "number") {
            end = addMonths(new Date(), drObj.end);
          } else {
            end = drObj.end;
          }
        }
        context.commit("changeDateRange", {
          index: dateRangeIndex,
          start: start,
          end: end,
        });
      } else {
        context.commit("changeDateRange", { index: dateRangeIndex });
        // if the end of the period is not specified, set it to current data,
        // because 'undefined' and null states are both used for special purposes
        // in the changeDateRange, we use the specific setters here
        if (context.state.dateRangeEnd === null) {
          context.commit("setDateRangeEnd", { date: new Date() });
        }
        if (context.state.dateRangeStart === null) {
          context.commit("setDateRangeStart", {
            date: addMonths(context.state.dateRangeEnd, -24),
          });
        }
      }
    },
    changeDateRangeStart(context, date) {
      if (typeof date === "string") {
        date = startOfMonth(parseDateTime(date));
      }
      context.commit("setDateRangeStart", { date });
    },
    changeDateRangeEnd(context, date) {
      if (typeof date === "string") {
        date = endOfMonth(parseDateTime(date));
      }
      context.commit("setDateRangeEnd", { date });
    },
  },

  mutations: {
    changeDateRange(state, { index, start, end }) {
      state.dateRangeIndex = index;
      if (typeof start !== "undefined") {
        state.dateRangeStart = start;
      }
      if (typeof end !== "undefined") {
        state.dateRangeEnd = end;
      }
    },
    setDateRangeStart(state, { date }) {
      state.dateRangeStart = date;
    },
    setDateRangeEnd(state, { date }) {
      state.dateRangeEnd = date;
    },
  },
};
