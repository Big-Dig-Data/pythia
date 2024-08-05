<i18n src="../locales/common.yaml"></i18n>
<i18n>
en:
  growth: Growth
cs:
  growth: Růst
</i18n>

<template>
  <div>
    <v-text-field
      v-model="search"
      clearable
      :placeholder="$t('search')"
    ></v-text-field>

    <v-skeleton-loader v-if="loading" type="paragraph@5"> </v-skeleton-loader>

    <v-data-table
      v-else
      v-model="selected"
      :headers="
        score_type === 'candidate_count' ? headers : headers.slice(0, 2)
      "
      :items="rows"
      item-key="pk"
      :options.sync="options"
      :server-items-length="totalRows"
      :loading="loading"
      show-select
      :single-select="false"
      :footer-props="{
        'items-per-page-text': '',
        'items-per-page-options': [],
      }"
      class="elevation-2"
      dense
    >
      <template #item.name="{ item }">
        <ShortenText :text="item.name" :length="40" />
      </template>
      <template #item.score="{ item }">
        {{ formatInteger(item.score) }}
      </template>
      <template #item.relative_growth="{ item }">
        <v-tooltip bottom>
          <template v-slot:activator="{ on, attrs }">
            <span v-bind="attrs" v-on="on">
              {{ item.relative_growth }}
            </span>
          </template>
          <span>
            {{ item.relative_growth }} ({{ item.score_yr_b4 }} ->
            {{ item.score_past_yr }})
          </span>
        </v-tooltip>
      </template>
      <template v-slot:pageText="props">
        {{ $t("table.row_counter", props) }}
      </template>
    </v-data-table>
  </div>
</template>

<script>
import axios from "axios";
import numeral from "numeral";
import debounce from "lodash/debounce";
import { mapActions, mapGetters } from "vuex";
import { formatInteger } from "../libs/numbers";
import ShortenText from "./ShortenText";
import cloneDeep from "lodash/cloneDeep";
import isEqual from "lodash/isEqual";

export default {
  name: "TopicsFilterTable",
  components: { ShortenText },
  props: {
    value: { required: true, type: Array },
    header: { required: true, type: String },
    urlArg: { required: true, type: String },
    candidate_count_filters: { default: () => {}, type: Object },
    score_type: { default: "candidate_count", type: String },
  },

  data() {
    return {
      selected: cloneDeep(this.value),
      rows: [],
      options: { itemsPerPage: 10 },
      totalRows: 0,
      loading: false,
      justFetchingUrl: null,
      justFetchingParams: null,
      search: "",
      selectedRows: [],
    };
  },

  computed: {
    ...mapGetters({
      worksetUUID: "selectedWorksetUUID",
    }),
    urlParams() {
      return {
        page: this.options.page,
        page_size: this.options.itemsPerPage,
        q: this.search,
        candidates_filter: this.score_type === "candidate_count" ? 1 : 0,
        show_candidates_count: this.score_type === "candidate_count" ? 1 : 0,
        candidate_count_filters: this.candidate_count_filters,
        score_type: this.score_type === "growth" ? "growth" : "score",
      };
    },
    dataUrl() {
      if (!this.worksetUUID) return null;
      return `/api/bookrank/workset/${this.worksetUUID}/et_filters/${this.urlArg}/`;
    },
    headers() {
      return [
        {
          text: this.header,
          value: "name",
          sortable: false,
        },
        {
          text:
            this.score_type == "candidate_count"
              ? this.$i18n.t("columns.score")
              : this.$t("growth"),
          value:
            this.score_type == "candidate_count" ? "score" : "relative_growth",
          align: "right",
          sortable: false,
        },
        {
          text: this.$i18n.t("pages.candidates"),
          value: "candidates_count",
          align: "right",
          sortable: false,
        },
      ];
    },
  },

  methods: {
    ...mapActions({
      showSnackbar: "showSnackbar",
    }),
    formatInteger,
    async fetchData() {
      if (!this.dataUrl) return null;
      this.loading = true;
      this.justFetchingUrl = this.dataUrl;
      this.justFetchingParams = cloneDeep(this.urlParams);
      try {
        const response = await axios.get(this.dataUrl, {
          params: this.urlParams,
        });
        if (this.score_type === "growth") {
          this.rows = response.data.results.map((row) => {
            row.relative_growth = this.formatGrowth(row.relative_growth);
            return row;
          });
        } else {
          this.rows = response.data.results;
        }
        this.totalRows = response.data.count;
        this.$emit("ready", true);
      } catch (error) {
        this.showSnackbar({
          content: "Error fetching data: " + error,
          color: "error",
        });
      } finally {
        this.loading = false;
      }
    },

    formatGrowth(val) {
      if (val == null) return "-";
      return numeral(val).format(`+0,0%`).replace(/,/g, "\xa0");
    },
  },

  watch: {
    selected() {
      let selectedIds = this.selected.map((item) => item.pk);
      this.$emit("input", selectedIds);
    },
    value() {
      let selectedIds = this.selected.map((item) => item.pk);
      if (!isEqual(selectedIds, this.value)) {
        this.selected = this.rows.filter((item) =>
          this.value.includes(item.pk)
        );
      }
    },
    dataUrl: {
      handler(newUrl) {
        if (newUrl !== this.justFetchingUrl) this.fetchData();
      },
      immediate: true,
    },
    urlParams: {
      handler() {
        if (!isEqual(this.justFetchingParams, this.urlParams)) {
          this.fetchData();
        }
      },
      deep: true,
    },
  },
};
</script>
