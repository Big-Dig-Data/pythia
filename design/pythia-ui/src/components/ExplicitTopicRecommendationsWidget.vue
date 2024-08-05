<i18n src="../locales/common.yaml"></i18n>
<i18n>
en:
  ordering_criteria: Ordering criteria
  minimum_work_count: Minimum work count
  ordering:
    highest_score: Highest score
    most_works: Most works
    highest_rel_score: Highest score relative to size
  columns:
    title: Title
    score: Score
    score_rel: Relative score
    size: Number of works
    size_rel: '% of selection'
    avg_work_score: Average work score
    interest_size_ratio: Interest / size ratio

cs:
  ordering_criteria: Řadící kritéria
  minimum_work_count: Minimální počet děl ve fondu
  ordering:
    highest_score: Nejvyšší skóre
    most_works: Nejvíce děl
    highest_rel_score: Nejvyšší skóre relativně k počtu děl
  columns:
    title: Název
    score: Skóre
    score_rel: Relativní skóre
    size: Počet děl
    size_rel: Zastoupení ve výběru
    avg_work_score: Průměrný zájem o dílo
    interest_size_ratio: Zájem / počet děl
</i18n>

<template>
  <v-container fluid class="px-0 py-0" style="height: 100%">
    <v-row v-if="showOrderingSelection">
      <v-col :cols="12" :sm="10" :md="6" :lg="4" pr-2>
        <v-select
          v-model="orderBy"
          :label="$t('ordering_criteria')"
          :items="orderingOptions"
          item-text="text"
          item-value="value"
        >
        </v-select>
      </v-col>
      <v-col :cols="12" :sm="2" pl-2>
        <v-select
          v-if="orderBy === 'score_size_ratio'"
          v-model="minTopicSize"
          :label="$t('minimum_work_count')"
          :items="[1, 5, 10, 20, 50]"
        >
        </v-select>
      </v-col>
    </v-row>

    <v-row no-gutters style="height: 100%">
      <v-col :cols="12" :md="selectedRow ? 4 : 12" :lg="selectedRow ? 3 : 12">
        <v-data-table
          :headers="headers"
          :items="rows"
          :loading="rowsLoading"
          sort-desc
          :items-per-page.sync="tablePageSize"
          :page.sync="tablePage"
          :class="selectedRow ? 'elevation-10' : 'elevation-1'"
          :footer-props="{
            'items-per-page-text': $t('table.rows_per_page'),
            'items-per-page-options': showPageSize ? [5, 10, 15, -1] : [5],
          }"
          :server-items-length="totalItems"
          :dense="compactTable"
        >
          <template v-slot:item.name="{ item }">
            <span
              v-if="drillDown"
              class="clickable"
              :class="{ active: selectedRow && selectedRow.pk === item.pk }"
              @click="selectRow(item)"
            >
              {{ item.name }}
            </span>
            <ExplicitTopicLink
              v-else
              :topic-id="item.pk"
              :topic-type="topicType"
              >{{ item.name }}</ExplicitTopicLink
            >
          </template>

          <template v-slot:item.score="{ item }">
            {{ formatInteger(item.score) }}
          </template>
          <template v-slot:item.work_count="{ item }">
            {{ formatInteger(item.work_count) }}
          </template>
          <template v-slot:item.score_rel="{ item }">
            {{ formatNumberToPlaces(100 * item.score_rel, 2) }} %
          </template>
          <template v-slot:item.work_count_rel="{ item }">
            {{ formatNumberToPlaces(100 * item.work_count_rel, 2) }} %
          </template>
          <template v-slot:item.ratio="{ item }">
            {{ formatNumberToPlaces(item.ratio, 2) }}
          </template>
          <template v-slot:pageText="props">
            {{ $t("table.row_counter", props) }}
          </template>
        </v-data-table>
      </v-col>

      <v-col :cols="12" :md="8" :lg="9" v-if="selectedRow && drillDown">
        <ExplicitTopicRelatedTopicsWidget
          :topic-type="topicType"
          :topic-id="selectedRow.pk"
        />
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import axios from "axios";
import * as math from "mathjs";
import { mapActions, mapGetters } from "vuex";
import { stringify } from "query-string";
import { formatInteger } from "../libs/numbers";
import ExplicitTopicRelatedTopicsWidget from "./ExplicitTopicRelatedTopicsWidget";
import ExplicitTopicLink from "./ExplicitTopicLink";
import { topicTypeToQueryParam } from "../libs/api";

export default {
  name: "ExplicitTopicRecommendationsWidget",
  components: { ExplicitTopicLink, ExplicitTopicRelatedTopicsWidget },
  props: {
    topicType: {
      required: true,
      type: String,
      validator: (value) => value in topicTypeToQueryParam,
    },
    extraFilter: {
      required: false,
      type: Object,
    },
    drillDown: {
      default: true,
      type: Boolean,
    },
    showOrderingSelection: {
      default: true,
      type: Boolean,
    },
    defaultMinTopicSize: {
      required: false,
      type: Number,
    },
    defaultPageSize: {
      required: false,
      type: Number,
      default: 15,
    },
    compactTable: {
      default: false,
      type: Boolean,
    },
    ignoreGlobalFilters: {
      default: false,
      type: Boolean,
    },
    showPageSize: {
      default: false,
      type: Boolean,
    },
  },
  data() {
    return {
      rows: [],
      orderBy: "score",
      tablePage: 1,
      tablePageSize: this.defaultPageSize,
      rowsLoading: false,
      minTopicSize: this.defaultMinTopicSize ? this.defaultMinTopicSize : 10,
      totalItems: null,
      numberFormat: {
        notation: "fixed",
        precision: 1,
      },
      selectedRow: null,
      justFetchingUrl: null,
    };
  },
  computed: {
    ...mapGetters({
      worksetUUID: "selectedWorksetUUID",
      queryParams: "workQueryParams",
    }),
    orderingOptions() {
      return [
        {
          text: this.$i18n.t("ordering.most_works"),
          value: "work_count",
        },
        {
          text: this.$i18n.t("ordering.highest_score"),
          value: "score",
        },
        {
          text: this.$i18n.t("ordering.highest_rel_score"),
          value: "score_size_ratio",
        },
      ];
    },
    headers() {
      const all = [
        {
          text: this.$i18n.t("columns.title"),
          value: "name",
          sortable: false,
        },
        {
          text: this.$i18n.t("columns.score"),
          value: "score",
          align: "right",
          sortable: false,
        },
        {
          text: this.$i18n.t("columns.score_rel"),
          value: "score_rel",
          align: "right",
          sortable: false,
        },
        {
          text: this.$i18n.t("columns.size"),
          value: "work_count",
          align: "right",
          sortable: false,
        },
        {
          text: this.$i18n.t("columns.size_rel"),
          value: "work_count_rel",
          align: "right",
          sortable: false,
        },
        {
          text: this.$i18n.t("columns.interest_size_ratio"),
          value: "ratio",
          align: "right",
          sortable: false,
        },
      ];
      if (this.selectedRow) {
        return all.slice(0, 2);
      }
      return all;
    },
    dataUrl() {
      if (this.worksetUUID) {
        let params = {
          page_size: this.tablePageSize,
          page: this.tablePage,
          order_by: this.orderBy,
        };
        if (!this.ignoreGlobalFilters) {
          params = { ...params, ...this.queryParams };
        }
        if (this.orderBy === "score_size_ratio") {
          params["min_topic_size"] = this.minTopicSize;
        }
        if (this.extraFilter) {
          for (let [key, value] of Object.entries(this.extraFilter)) {
            params["filter_type"] = key;
            params["filter_value"] = value;
          }
        }
        return `/api/hits/workhit/stats/${this.worksetUUID}/${
          this.topicType
        }?${stringify(params)}`;
      } else return null;
    },
  },
  methods: {
    ...mapActions({
      showSnackbar: "showSnackbar",
    }),
    formatInteger,
    async fetchData() {
      if (this.dataUrl) {
        this.rowsLoading = true;
        this.justFetchingUrl = this.dataUrl;
        try {
          const response = await axios.get(this.dataUrl);
          this.rows = response.data.results.map((el) => {
            if (this.topicType == "psh") el.name += ` (${el.root_node})`;
            return el;
          });
          this.totalItems = response.data.count;
        } catch (error) {
          this.showSnackbar({
            content: "Error fetching data: " + error,
            color: "error",
          });
        } finally {
          this.rowsLoading = false;
          this.justFetchingUrl = null;
        }
      }
    },
    formatNumber(number) {
      return math.format(number, this.numberFormat);
    },
    formatNumberToPlaces(number, places = 1) {
      if (number === null) number = 0;
      return math.format(number, { notation: "fixed", precision: places });
    },
    selectRow(row) {
      if (this.drillDown) {
        if (this.selectedRow != row) {
          this.selectedRow = row;
        } else {
          this.selectedRow = null;
        }
      }
    },
  },
  watch: {
    dataUrl(newUrl) {
      if (newUrl !== this.justFetchingUrl) this.fetchData();
    },
  },
  mounted() {
    this.fetchData();
  },
};
</script>

<style lang="scss">
tr.active {
  background-color: #e0e0e0;
}

span.active {
  font-weight: 900;
}

span.clickable {
  cursor: pointer;
}
</style>
