<template>
  <v-card class="char-card">
    <v-card-title class="pb-0 d-flex justify-space-between">
      <div v-if="title">
        {{ title }}
        <v-tooltip v-if="titleInfo" bottom>
          <template v-slot:activator="{ on, attrs }">
            <v-icon v-bind="attrs" v-on="on" small class="ml-2">
              fa-info-circle
            </v-icon>
          </template>
          <span>{{ titleInfo }}</span>
        </v-tooltip>
      </div>
      <div>
        <v-tooltip v-if="clickInfo && title" bottom>
          <template v-slot:activator="{ on, attrs }">
            <v-icon v-bind="attrs" v-on="on" small color="info" class="mr-2">
              fa-info-circle
            </v-icon>
          </template>
          <span>{{ clickInfoText }}</span>
        </v-tooltip>
        <v-btn-toggle v-model="activeTab" mandatory>
          <v-btn><v-icon small>fas fa-chart-bar</v-icon></v-btn>
          <v-btn><v-icon small>fas fa-table</v-icon></v-btn>
        </v-btn-toggle>
      </div>
      <div v-if="!title">
        <v-tooltip v-if="clickInfo" bottom>
          <template v-slot:activator="{ on, attrs }">
            <v-icon v-bind="attrs" v-on="on" small color="info">
              fa-info-circle
            </v-icon>
          </template>
          <span>{{ clickInfoText }}</span>
        </v-tooltip>
      </div>
    </v-card-title>
    <v-tabs color="accent-4" grow>
      <v-tabs-items v-model="activeTab">
        <v-tab-item :style="`height: ${chartHeight}px`">
          <BarChart
            v-if="!loading"
            :rawData="rawData"
            :dimension="dynamicDimension"
            :metrics="dynamicMetrics"
            :yAxis="yAxis"
            :chartHeight="chartHeight"
            :allowClick="allowClick"
            @bar-clicked="handleClick"
          />
          <div v-else class="loader">
            <span class="fas fa-cog fa-spin fa-4x"></span>
          </div>
        </v-tab-item>

        <v-tab-item>
          <ChartTable
            :columns="[dynamicDimension, ...dynamicMetrics]"
            :rawData="rawData"
            :height="chartHeight"
          />
        </v-tab-item>
      </v-tabs-items>
    </v-tabs>
  </v-card>
</template>

<script>
import axios from "axios";
import { mapActions, mapGetters } from "vuex";
import BarChart from "./BarChart";
import ChartTable from "./ChartTable";
import numeral from "numeral";

export default {
  name: "BarChartCard",
  components: { BarChart, ChartTable },
  props: {
    title: { required: false, type: String },
    titleInfo: { required: false, type: String },
    url: { required: true, type: String },
    dimension: { required: false, type: Object },
    metrics: { required: false, type: Array },
    requestParams: { required: false, type: Object },
    yAxis: { default: () => [{}], type: Array },
    chartHeight: { default: 400, type: Number },
    dataProp: { default: "", type: String },
    formater: { required: false, type: String },
    allowClick: { default: false, type: Boolean },
    clickInfo: { default: false, type: Boolean },
    clickInfoText: { required: false, type: String },
    metricsFromMeta: { default: false, type: Boolean },
    dimensionFromMeta: { default: false, type: Boolean },
    dimensionValueProp: { required: false, type: String },
  },
  data() {
    return {
      rawData: [],
      justFetchingUrl: null,
      loading: false,
      activeTab: 0,
      labelMap: null,
    };
  },

  computed: {
    ...mapGetters({
      chartColors: "chartColors",
      worksetUUID: "selectedWorksetUUID",
    }),
    dataUrl() {
      if (!this.worksetUUID) return null;
      return this.url.replace("WORKSET_UID", this.worksetUUID);
    },
    dataFormater() {
      if (!this.formater) return null;
      return {
        formatRelativeAcqScore: this.formatRelativeAcqScore,
      }[this.formater];
    },
    dynamicMetrics() {
      if (!this.metricsFromMeta) return this.metrics;
      if (!this.labelMap) return [];
      let metrics = [];
      for (let key in this.labelMap) {
        if (!["score", "date"].includes(key)) {
          metrics.push({
            name: this.labelMap[key],
            value: key,
            type: "bar",
          });
        }
      }
      return metrics;
    },
    dynamicDimension() {
      if (!this.dimensionFromMeta) return this.dimension;
      if (!this.labelMap) return {};
      return {
        name: this.labelMap[this.dimensionValueProp],
        value: this.dimensionValueProp,
      };
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

  methods: {
    ...mapActions({
      showSnackbar: "showSnackbar",
    }),

    async fetchData() {
      if (!this.dataUrl) return null;
      this.loading = true;
      this.justFetchingUrl = this.dataUrl;
      try {
        const response = await axios.get(this.dataUrl, {
          params: this.requestParams,
        });
        let data = this.dataProp ? response.data[this.dataProp] : response.data;
        if (this.metricsFromMeta) {
          this.labelMap = response.data.meta.labelMap;
        }
        this.rawData = this.dataFormater ? data.map(this.dataFormater) : data;
        this.rawData.forEach(
          (item) =>
            (item.catalog_year = item.catalog_year
              ? item.catalog_year.slice(0, 4)
              : item.catalog_year)
        );
      } catch (error) {
        this.showSnackbar({
          content: "Error fetching data: " + error,
          color: "error",
        });
      } finally {
        this.loading = false;
      }
    },

    formatRelativeAcqScore(obj) {
      if (obj.acquisition_score_sum != 0) {
        obj.acquisition_score_sum = numeral(obj.acquisition_score_sum).format(
          "0.0[0]"
        );
      }
      return obj;
    },

    handleClick(bin) {
      if (this.allowClick) this.$emit("bar-clicked", bin);
    },
  },
};
</script>
<style scoped>
.char-card
  >>> div.v-item-group.theme--light.v-slide-group.v-tabs-bar.accent-4--text {
  height: 10px;
}
</style>
