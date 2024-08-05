<i18n>
en:
  score: Score
  work_count: Work count
cs:
  score: Skóre
  work_count: Počet prací
</i18n>

<template>
  <v-chart
    :option="option"
    autoresize
    :update-options="{
      replaceMerge: ['series'],
    }"
  ></v-chart>
</template>

<script>
import * as echarts from "echarts";
import { use } from "echarts/core";
import { CanvasRenderer } from "echarts/renderers";
import { TreeChart } from "echarts/charts";
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
} from "echarts/components";
import VChart from "vue-echarts";
import { mapGetters } from "vuex";
import axios from "axios";

use([
  CanvasRenderer,
  TreeChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
]);

export default {
  name: "SubjectTreeMap",

  components: { VChart },

  props: {
    parentUid: { required: true, type: String },
    valueAttr: { default: "acc_score", type: String },
    chartType: {
      default: "treemap",
      type: String,
      validator: (value) => ["treemap", "sunburst"].includes(value),
    },
  },

  data() {
    return {
      tree: [],
      loading: false,
    };
  },

  computed: {
    ...mapGetters({
      worksetUUID: "selectedWorksetUUID",
    }),
    dataUrl() {
      if (!this.worksetUUID) return null;
      return `/api/bookrank/workset/${this.worksetUUID}/subjects/${this.parentUid}/`;
    },
    option() {
      let that = this;
      return {
        series: {
          type: this.chartType,
          data: this.tree,
          visibleMin: 300,
          right: 0,
          left: 0,
          top: 0,
          bottom: 28,
          leafDepth: 2,
          label: {
            show: this.chartType === "treemap",
            //formatter: "{b}",
          },
          upperLabel: {
            show: true,
            height: 20,
            color: "white",
            textBorderColor: "inherit",
          },
          itemStyle: {
            borderColorSaturation: 0.7,
          },
          levels: [
            // 1
            {
              itemStyle: {
                borderColor: "#777",
                borderWidth: 0,
                gapWidth: 1,
              },
              upperLabel: {
                show: false,
              },
            },
            // 2
            {
              itemStyle: {
                //borderColor: "#555",
                borderWidth: 3,
                //gapWidth: 1,
                borderColorSaturation: 0.4,
              },
            },
            // 3
            {
              colorSaturation: [0.35, 0.5],
              itemStyle: {
                borderWidth: 5,
                gapWidth: 1,
                borderColorSaturation: 0.45,
              },
            },
            // 4
            {
              colorSaturation: [0.35, 0.5],
              itemStyle: {
                borderWidth: 5,
                gapWidth: 1,
                borderColorSaturation: 0.5,
              },
            },
            // 5
            {
              colorSaturation: [0.35, 0.5],
              itemStyle: {
                borderWidth: 5,
                gapWidth: 1,
                borderColorSaturation: 0.55,
              },
            },
            // 6
            {
              colorSaturation: [0.35, 0.5],
              itemStyle: {
                borderWidth: 5,
                gapWidth: 1,
                borderColorSaturation: 0.6,
              },
            },
          ],
        },
        tooltip: {
          formatter: function (info) {
            const formatUtil = echarts.format;
            let treePath = info.treePathInfo
              .filter((item, index) => index > 0)
              .map((item) => item.name);
            const wc_class =
              that.valueAttr === "acc_work_count" ? "font-weight-bold" : "";
            const score_class =
              that.valueAttr === "acc_score" ? "font-weight-bold" : "";
            return `<div class="font-weight-bold">
                  ${formatUtil.encodeHTML(treePath.join(" / "))}
               </div>
               <span>${that.$t("score")}</span>:
               <span class="${score_class}">${formatUtil.addCommas(
              info.data.acc_score
            )}</span>
               <br>
               <span>${that.$t("work_count")}</span>:
               <span class="${wc_class}"> ${formatUtil.addCommas(
              info.data.acc_work_count
            )}</span>
               `;
          },
        },
      };
    },
  },

  methods: {
    async fetchData() {
      if (!this.dataUrl) return null;
      this.loading = true;
      this.justFetchingUrl = this.dataUrl;
      try {
        const response = await axios.get(this.dataUrl);
        let tree = response.data.tree;
        this.processTree(tree);
        this.tree = tree;
      } catch (error) {
        this.showSnackbar({
          content: "Error fetching data: " + error,
          color: "error",
        });
      } finally {
        this.loading = false;
      }
    },
    processTree(tree) {
      tree.forEach((item) => {
        item.value = item[this.valueAttr];
        if (item.children && item.children.length)
          this.processTree(item.children);
      });
    },
  },

  mounted() {
    this.fetchData();
  },

  watch: {
    dataUrl() {
      this.fetchData();
    },
    valueAttr() {
      this.processTree(this.tree);
    },
  },
};
</script>

<style scoped></style>
