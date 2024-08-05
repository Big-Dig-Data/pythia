<i18n src="../locales/common.yaml"></i18n>

<i18n>
en:
    select_date_range: Select date range

cs:
    select_date_range: Vyberte rozmezí dat
</i18n>

<template>
  <div class="d-flex align-center cursor-pointer">
    <div class="sc shrink mr-2">{{ $t("labels.date_range") }}:</div>
    <div>
      <div class="d-flex flex-column" @click="showDialog = true">
        <div>{{ rangeName }}</div>
        <div class="small subdued">{{ rangeValueText }}</div>

        <v-dialog v-model="showDialog" max-width="520px">
          <v-card>
            <v-card-title>{{ $t("select_date_range") }}</v-card-title>
            <v-divider></v-divider>
            <v-card-text>
              <DateRangeSelector />
            </v-card-text>
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn color="primary" text @click="showDialog = false"
                >Close</v-btn
              >
            </v-card-actions>
          </v-card>
        </v-dialog>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters, mapState } from "vuex";
import { ymDateFormat } from "../libs/dates";
import DateRangeSelector from "./DateRangeSelector";

export default {
  name: "SelectedDateRangeWidget",
  components: { DateRangeSelector },
  data() {
    return {
      showDialog: false,
    };
  },
  computed: {
    ...mapState({
      start: (state) => state.dateRange.dateRangeStart,
      end: (state) => state.dateRange.dateRangeEnd,
    }),
    ...mapGetters({
      rangeObject: "selectedDateRange",
    }),
    rangeName() {
      return this.$i18n.t(this.rangeObject.name);
    },
    rangeValueText() {
      let start = this.startDate;
      let end = this.endDate;
      if (start || end) {
        return `${start} - ${end}`;
      }
      return "";
    },
    startDate() {
      if (this.start) {
        return ymDateFormat(this.start);
      }
      return "";
    },
    endDate() {
      if (this.end) {
        return ymDateFormat(this.end);
      }
      return "";
    },
  },
};
</script>

<style scoped lang="scss">
.small {
  font-size: 0.875rem;
}
.subdued {
  color: var(--v-primary-lighten2);
}
</style>
