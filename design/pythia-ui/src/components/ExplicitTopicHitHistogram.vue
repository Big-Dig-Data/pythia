<i18n>
en:
    item_count: Number
    interest: Number of loans

cs:
    item_count: Počet
    interest: Počet výpůjček
</i18n>

<template>
  <ve-histogram
    v-if="!loading"
    :data="histogramChartData"
    :xAxis="{
      type: 'category',
      name: $t('interest'),
      nameLocation: 'middle',
      nameGap: 80,
      axisLabel: { rotate: 90 },
      data: histogramChartXAxisData,
    }"
    :yAxis="{ type: logScale ? 'log' : 'value', min: logScale ? 0.1 : 0 }"
    :settings="{ labelMap: { count: this.$t('item_count') } }"
    :colors="chartColors"
    height="400px"
  ></ve-histogram>
  <div v-else class="loader">
    <span class="fas fa-cog fa-spin fa-4x"></span>
  </div>
</template>

<script>
import VeHistogram from "v-charts/lib/histogram.common";
import { topicTypeToQueryParam } from "../libs/api";
import { mapActions, mapGetters } from "vuex";
import axios from "axios";
import { stringify } from "query-string";

export default {
  name: "ExplicitTopicHitHistogram",

  components: {
    VeHistogram,
  },

  props: {
    topicType: {
      required: true,
      type: String,
      validator: (value) => value in topicTypeToQueryParam,
    },
    logScale: {
      default: false,
      type: Boolean,
    },
    rootNode: { required: false, type: String },
  },

  data() {
    return {
      histogramData: [],
      loading: false,
      cancelTokenSource: null,
    };
  },

  computed: {
    ...mapGetters({
      worksetUUID: "selectedWorksetUUID",
      queryParams: "workQueryParams",
      chartColors: "chartColors",
    }),
    dataUrl() {
      if (this.worksetUUID) {
        let params = { ...this.queryParams };
        return `/api/hits/workhit/histogram/${this.worksetUUID}/${
          this.topicType
        }?${stringify(params)}`;
      } else return null;
    },
    histogramChartXAxisData() {
      return [...new Set(this.histogramData.map((item) => item.name))];
    },
    histogramChartData() {
      if (this.histogramData) {
        return {
          columns: ["name", "count"],
          rows: this.histogramData,
        };
      }
      return null;
    },
  },

  methods: {
    ...mapActions({
      showSnackbar: "showSnackbar",
    }),
    async fetchData() {
      if (this.cancelTokenSource) {
        this.cancelTokenSource.cancel("new data requested");
        this.cancelTokenSource = null;
      }
      if (this.dataUrl) {
        this.loading = true;
        this.histogramData = [];
        this.cancelTokenSource = axios.CancelToken.source();
        try {
          const response = await axios.get(this.dataUrl, {
            cancelToken: this.cancelTokenSource.token,
            params: { root_node: this.rootNode },
          });
          this.histogramData = response.data;
          this.loading = false;
        } catch (error) {
          if (axios.isCancel(error)) {
            console.debug("Request cancelled");
          } else {
            this.showSnackbar({
              content: "Error fetching histogram data: " + error,
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

<style scoped lang="scss">
div.loader {
  width: 400px;
  height: 400px;
  text-align: center;
  padding-top: 100px;
  //border: solid 1px #eeeeee;
  border-radius: 5px;
  background: rgba(227, 252, 249, 0.25);

  span.fas {
    color: var(--v-primary-base);
  }
}
</style>
