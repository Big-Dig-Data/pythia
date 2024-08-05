<i18n src="@/locales/topic-types.yaml"></i18n>
<i18n src="@/locales/common.yaml"></i18n>
<i18n>
en:
    work_count: Most frequent
    score: Most demanded
    absolute_growth: Absolute growth
    relative_growth: Relative growth
    new_works_acquisition_score: New works growth
    infos:
      absolute_growth: Difference between loans made in past year and year before
      relative_growth: Absolute growth expresed in percentage
      new_works_acquisition_score: Loans of works acquired in last 2 years made in 12 months after acquisition
cs:
    work_count: Největší zastoupení
    score: Nejpoptávanější
    absolute_growth: Absolutní růst
    relative_growth: Relativní růst
    new_works_acquisition_score: Růst nových prací
    infos:
      absolute_growth: Rozdíl mezi počtem výpůjček za poslední rok oproti předchozímu roku - absolutní počet
      relative_growth: Rozdíl mezi počtem výpůjček za poslední rok oproti předchozímu roku - relativní vyjádření
      new_works_acquisition_score: Akviziční skóre (počet výpůjček 12 měsíců po akvizici) u akvizic za poslední dva roky
</i18n>

<template>
  <v-card>
    <v-card-title>
      {{ $t(orderBy) }}
      <v-tooltip v-if="includeInfo" bottom>
        <template v-slot:activator="{ on, attrs }">
          <span v-bind="attrs" v-on="on">
            <v-icon class="ml-4">fa-info-circle</v-icon>
          </span>
        </template>
        <span>{{ $t("infos." + orderBy) }}</span>
      </v-tooltip>
    </v-card-title>
    <v-card-text>
      <table v-if="!loading">
        <thead>
          <tr>
            <td></td>
            <td class="text-right" v-text="$t('columns.' + orderBy)"></td>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in rows" :key="row.pk">
            <td class="text-left pr-4">
              <ExplicitTopicLink
                v-if="itemType == 'explicit_topic'"
                :topic-type="topicType"
                :topic-id="row.pk"
              >
                {{ row.name }}
              </ExplicitTopicLink>
              <router-link
                v-else
                :to="{ name: 'work detail', params: { workId: row.pk } }"
              >
                {{ row.name }}
              </router-link>
            </td>
            <td
              class="text-right"
              style="white-space: nowrap"
              v-text="row[orderBy]"
            ></td>
          </tr>
        </tbody>
      </table>
      <v-progress-circular v-else indeterminate> </v-progress-circular>
    </v-card-text>
  </v-card>
</template>

<script>
import axios from "axios";
import { mapActions, mapGetters } from "vuex";
import { stringify } from "query-string";
import { formatInteger } from "../libs/numbers";
import ExplicitTopicLink from "./ExplicitTopicLink";

export default {
  name: "TopItemsWidget",
  components: { ExplicitTopicLink },
  props: {
    topicType: { required: false, type: String },
    itemNumber: { default: 10, type: Number },
    orderBy: {
      default: "size",
      type: String,
      validator: (value) =>
        [
          "work_count",
          "score",
          "absolute_growth",
          "relative_growth",
          "new_works_acquisition_score",
        ].indexOf(value) >= 0,
    },
    rootNode: { required: false, type: String },
    includeInfo: { default: false, type: Boolean },
    itemType: {
      default: "explicit_topic",
      type: String,
      validator: (value) => ["explicit_topic", "work"].includes(value),
    },
  },
  data() {
    return {
      rows: [],
      loading: false,
      cancelTokenSource: null,
      growthFormat: {
        absolute_growth: this.absGrowthFormater,
        relative_growth: this.relGrowthFormater,
      },
    };
  },
  computed: {
    ...mapGetters({
      worksetUUID: "selectedWorksetUUID",
      queryParams: "workQueryParams",
    }),
    dataUrl() {
      if (this.worksetUUID) {
        let params = {
          page_size: this.itemNumber,
          page: 1,
          order_by: this.orderBy,
          ...this.queryParams,
        };
        let url;
        if (this.itemType === "explicit_topic") {
          url = `/api/hits/workhit/stats/${this.worksetUUID}/${this.topicType}`;
        } else {
          // url = `/api/hits/workhit/works/${this.worksetUUID}/top_works`; TODO
          url = `/api/bookrank/workset/${this.worksetUUID}/works/top_items/`;
        }
        return `${url}?${stringify(params)}`;
      } else return null;
    },
  },
  methods: {
    ...mapActions({
      showSnackbar: "showSnackbar",
    }),
    formatInteger,
    async fetchData() {
      if (this.cancelTokenSource) {
        this.cancelTokenSource.cancel("new data requested");
        this.cancelTokenSource = null;
      }
      if (this.dataUrl) {
        this.loading = true;
        this.rows = [];
        this.cancelTokenSource = axios.CancelToken.source();
        try {
          const response = await axios.get(this.dataUrl, {
            cancelToken: this.cancelTokenSource.token,
            params: { root_node: this.rootNode },
          });
          const mapFunc = ["absolute_growth", "relative_growth"].includes(
            this.orderBy
          )
            ? this.growthFormat[this.orderBy]
            : this.relGrowthFormater;
          this.rows = response.data.results.map(mapFunc);
          this.loading = false;
        } catch (error) {
          if (axios.isCancel(error)) {
            console.debug("Request cancelled");
          } else {
            this.showSnackbar({
              content: "Error fetching data: " + error,
              color: "error",
            });
            this.loading = false;
          }
        } finally {
          // normally, we would do this.loading = false here, but we do not want to do it
          // in case the request was cancelled, as it means there are more data arriving later
          // and this is not the most recent request
        }
      }
    },

    absGrowthFormater(row) {
      const sign = row.absolute_growth > 0 ? "+" : "";
      row.absolute_growth = `${sign}${row.absolute_growth}
                              (${row.score_yr_b4} -> ${row.score_past_yr})`;
      return row;
    },
    relGrowthFormater(row) {
      const sign = row.relative_growth > 0 ? "+" : "";
      row.relative_growth = `${sign}${
        Math.round(row.relative_growth * 1000) / 10
      }%
                              (${row.score_yr_b4} -> ${row.score_past_yr})`;
      return row;
    },
    regularFormater(row) {
      row[this.orderBy] = this.formatInteger(row[this.orderBy]);
      return row;
    },
  },
  watch: {
    dataUrl() {
      this.fetchData();
    },
  },
  mounted() {
    this.fetchData();
  },
};
</script>

<style lang="scss" scoped>
table {
  width: 100%;
}
</style>
