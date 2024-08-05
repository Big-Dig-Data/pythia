<i18n src="../locales/common.yaml"></i18n>
<i18n>
en:
  by_year: By year
  by_month: By month
  loans_24: Standard loans
  loans_25: In-house loans
  date: Date
  click_info: Click on the chart to see works contributing to interest
cs:
  by_year: Po rocích
  by_month: Po měsících
  loans_24: Absenční výpůjčky
  loans_25: Prezenční výpůjčky
  date: Týden
  click_info: Kliknutím na jednotlivé sloupce zobrazíte díla, která byla v daném období půjčována
</i18n>
<template>
  <div>
    <v-row>
      <v-col align="right" class="flex-column">
        <v-btn-toggle v-model="axisToggle" shaped mandatory>
          <v-btn>{{ $t("by_month") }}</v-btn>
          <v-btn>{{ $t("by_year") }}</v-btn>
        </v-btn-toggle>
      </v-col>
    </v-row>
    <BarChartCard
      :url="url"
      dataProp="stats"
      :dimensionFromMeta="true"
      dimensionValueProp="date"
      :allowClick="true"
      @bar-clicked="handleBarClick"
      :metricsFromMeta="true"
      :clickInfo="true"
      :clickInfoText="$t('click_info')"
    />

    <v-bottom-sheet v-model="sheet" scrollable>
      <v-card class="text-center">
        <v-card-text style="height: 300px">
          <v-data-table
            v-if="!initTableLoading"
            :loading="datatableLoading"
            :headers="headers"
            :items="rows"
            :options.sync="options"
            :server-items-length="totalRows"
            :footer-props="{
              'items-per-page-text': $t('table.rows_per_page'),
              'items-per-page-options': [5, 10, 20, 50, 100],
            }"
            item-key="pk"
            dense
            class="elevation-0"
          >
            <template v-slot:top>
              <h2>{{ lo_bound }} - {{ hi_bound }}</h2>
            </template>
            <template v-slot:item.name="{ item }">
              <router-link
                :to="{ name: 'work detail', params: { workId: item.pk } }"
              >
                {{ item.name }}
              </router-link>
            </template>
          </v-data-table>

          <div v-else class="loader">
            <span class="fas fa-cog fa-spin fa-4x"></span>
          </div>
        </v-card-text>
      </v-card>
    </v-bottom-sheet>
  </div>
</template>
<script>
import { mapGetters, mapActions } from "vuex";
import axios from "axios";
import debounce from "lodash/debounce";
import { stringify } from "query-string";
import { topicTypeToQueryParam } from "../libs/api";
import { firstOfTheMonthFromIso, lastOfTheMonthFromIso } from "../libs/dates";
import BarChartCard from "./charts/BarChartCard";

export default {
  name: "ExplicitTopicHitChart",

  components: {
    BarChartCard,
  },

  props: {
    topicType: { required: true, type: String },
    topicId: { required: true, type: Number },
  },

  data() {
    return {
      ignoreGlobalFilters: false,
      loading: false,
      topicTypeToQueryParam,
      axisToggle: 1,
      sheet: false,
      hi_bound: null,
      lo_bound: null,
      api_hi_bound: null,
      api_lo_bound: null,
      datatableLoading: false,
      initTableLoading: false,
      headers: [],
      rows: [],
      totalRows: 0,
      options: { itemsPerPage: 5 },
    };
  },

  computed: {
    ...mapGetters({
      queryParams: "workQueryParams",
      worksetUUID: "selectedWorksetUUID",
    }),
    extraFilter() {
      let out = {};
      out[this.topicTypeToQueryParam[this.topicType]] = this.topicId;
      return out;
    },
    globalFiltersActive() {
      return Object.values(this.queryParams).some((item) => item);
    },
    step() {
      return ["month", "year"][this.axisToggle];
    },
    url() {
      let params = {};
      if (!this.ignoreGlobalFilters) {
        params = { ...params, ...this.queryParams };
      }
      if (this.extraFilter) {
        for (let [key, value] of Object.entries(this.extraFilter)) {
          params["filter_type"] = key;
          params["filter_value"] = value;
        }
      }
      return `/api/hits/workhit/topic-time-stats/?${stringify({
        ...params,
        step: this.step,
      })}`;
    },
    tableUrl() {
      return `/api/bookrank/workset/${this.worksetUUID}/works_table/interest_chart_works/`;
    },
  },

  watch: {
    options: {
      handler() {
        this.fetchTableData();
      },
      deep: true,
    },
  },

  methods: {
    ...mapActions({
      showSnackbar: "showSnackbar",
    }),
    firstOfTheMonthFromIso,
    lastOfTheMonthFromIso,
    handleBarClick(bin) {
      this.initTableLoading = true;
      this.sheet = true;
      this.getDateBounds(bin);
      this.fetchTableData();
    },

    async fetchTableData() {
      try {
        const resp = await axios.get(this.tableUrl, {
          params: {
            page: this.options.page,
            page_size: this.options.itemsPerPage,
            lo_bound: this.api_lo_bound,
            hi_bound: this.api_hi_bound,
            filters: [{ name: this.topicType, id: this.topicId }],
          },
        });
        let headers = resp.data.columns.map((col) => {
          return {
            text: col,
            value: col.replace(" ", "_"),
            sortable: false,
          };
        });
        this.headers = [
          {
            text: this.$i18n.t("columns.title"),
            value: "name",
            sortable: false,
          },
        ].concat(headers);
        this.rows = resp.data.results;
        this.totalRows = resp.data.count;
      } catch (error) {
        this.showSnackbar({
          content: "Error fetching data: " + error,
          color: "error",
        });
      } finally {
        this.initTableLoading = false;
      }
    },

    getDateBounds(bin) {
      if (this.step == "month") {
        let lo = this.firstOfTheMonthFromIso(bin);
        let hi = this.lastOfTheMonthFromIso(bin);
        this.lo_bound = lo.readable;
        this.hi_bound = hi.readable;
        this.api_lo_bound = lo.api;
        this.api_hi_bound = hi.api;
      } else {
        this.api_lo_bound = `${bin}-01-01`;
        this.api_hi_bound = `${parseInt(bin) + 1}-01-01`;
        this.lo_bound = `1.1.${bin}`;
        this.hi_bound = `31.12.${bin}`;
      }
    },
  },
};
</script>

<style scoped lang="scss"></style>
