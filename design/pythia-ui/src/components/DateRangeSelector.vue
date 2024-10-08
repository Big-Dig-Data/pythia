<i18n src="../locales/common.yaml"></i18n>

<template>
  <v-container>
    <v-row>
      <v-col>
        <v-select
          :items="dateRanges"
          :label="$t('labels.date_range')"
          v-model="selectedRangeIndex"
          item-value="index"
          item-text="nameLocal"
        ></v-select>
      </v-col>
    </v-row>
    <v-row v-if="dateRange.custom">
      <!-- start date selector -->
      <v-col>
        <v-menu
          v-model="menuStart"
          transition="scale-transition"
          offset-y
          min-width="290px"
        >
          <template v-slot:activator="{ on }">
            <v-text-field
              v-model="start"
              label="Start"
              prepend-icon="fa-calendar-alt"
              readonly
              v-on="on"
            ></v-text-field>
          </template>
          <v-date-picker
            v-model="start"
            type="month"
            no-title
            :locale="$i18n.locale"
            :allowed-dates="allowedStartMonths"
          ></v-date-picker>
        </v-menu>
      </v-col>
      <!-- end date selector -->
      <v-col>
        <v-menu
          v-model="menuEnd"
          transition="scale-transition"
          offset-y
          min-width="290px"
        >
          <template v-slot:activator="{ on }">
            <v-text-field
              v-model="end"
              label="End"
              prepend-icon="fa-calendar-alt"
              readonly
              v-on="on"
            ></v-text-field>
          </template>
          <v-date-picker
            v-model="end"
            type="month"
            no-title
            scrollable
            :locale="$i18n.locale"
            :allowed-dates="allowedEndMonths"
          >
          </v-date-picker>
        </v-menu>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { mapActions, mapGetters, mapState } from "vuex";
import { ymDateFormat } from "../libs/dates";

export default {
  name: "DateRangeSelector",
  data() {
    return {
      menuStart: false,
      menuEnd: false,
    };
  },
  computed: {
    ...mapState({
      dateRangesRaw: (state) => state.dateRange.dateRanges,
      dateRangeIndex: (state) => state.dateRange.dateRangeIndex,
      startRaw: (state) => state.dateRange.dateRangeStart,
      endRaw: (state) => state.dateRange.dateRangeEnd,
    }),
    ...mapGetters({
      dateRange: "selectedDateRange",
    }),
    dateRanges() {
      return this.dateRangesRaw.map((item, index) => {
        return { ...item, index: index, nameLocal: this.$i18n.t(item.name) };
      });
    },
    selectedRangeIndex: {
      get() {
        return this.dateRangeIndex;
      },
      set(value) {
        this.setDateRangeIndex(value);
      },
    },
    start: {
      get() {
        return ymDateFormat(this.startRaw);
      },
      set(value) {
        this.setDateRangeStart(value);
      },
    },
    end: {
      get() {
        return ymDateFormat(this.endRaw);
      },
      set(value) {
        this.setDateRangeEnd(value);
      },
    },
  },
  methods: {
    ...mapActions({
      setDateRangeIndex: "changeDateRangeObject",
      setDateRangeStart: "changeDateRangeStart",
      setDateRangeEnd: "changeDateRangeEnd",
    }),
    allowedEndMonths(value) {
      let start = this.start;
      if (start) {
        return value >= start;
      }
      return true;
    },
    allowedStartMonths(value) {
      let end = this.end;
      if (end) {
        return value <= end;
      }
      return true;
    },
  },
};
</script>

<style scoped></style>
