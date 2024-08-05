<template>
  <v-chart
    :style="`height: ${chartHeight}px`"
    class="chart"
    :option="option"
    @click="handleClick"
  />
</template>

<script>
import { use } from "echarts/core";
import { CanvasRenderer } from "echarts/renderers";
import { BarChart, LineChart } from "echarts/charts";
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
} from "echarts/components";
import VChart from "vue-echarts";
import { labelKFormatter } from "../../libs/numbers";
import { mapGetters } from "vuex";

use([
  CanvasRenderer,
  BarChart,
  LineChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
]);

export default {
  name: "BarChart",
  components: { VChart },
  props: {
    dimension: { required: true, type: Object },
    metrics: { required: true, type: Array },
    yAxis: { required: true, type: Array },
    rawData: { required: true, type: Array },
    chartHeight: { required: true, type: Number },
    xLabel: { required: false, type: String },
    allowClick: { default: false, type: Boolean },
  },

  computed: {
    ...mapGetters({
      chartColors: "chartColors",
    }),
    yAxisProps() {
      return this.yAxis.map((obj) => {
        return {
          ...obj,
          type: "value",
          axisLabel: { formatter: labelKFormatter },
        };
      });
    },
    option() {
      return {
        color: this.chartColors,
        title: { show: false },
        grid: { bottom: this.dimension.name ? 60 : 30, top: 30 },
        legend: {},
        tooltip: {
          trigger: "axis",
          axisPointer: {
            type: "shadow",
          },
        },
        xAxis: [
          {
            type: "category",
            data: this.rawData.map((el) => el[this.dimension.value]),
            name: this.dimension.name,
            nameLocation: "center",
            nameGap: 30,
          },
        ],
        yAxis: this.yAxisProps,
        series: this.metrics.map((obj) => {
          let seriesObj = {
            name: obj.name,
            type: obj.type,
            data: this.rawData.map((el) => el[obj.value]),
            yAxisIndex: obj.yAxisIndex || 0,
          };
          if (obj.type == "bar") seriesObj.stack = "stack_1";
          return seriesObj;
        }),
      };
    },
  },
  methods: {
    labelKFormatter,
    handleClick(evtData) {
      if (!this.allowClick) return null;
      this.$emit("bar-clicked", evtData.name);
    },
  },
};
</script>

<style>
.chart {
  width: 100%;
}
</style>
