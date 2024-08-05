<i18n>
en:
  absolute_acquisition_score: Absolute acquisition score in time
  absolute_acquisition_score_info: Sum of loans made in 12 month period after work acquisition
  relative_acquisition_score: Relative acquisition score summary
  relative_acquisition_score_info: Absolute acquisition score divided by number of works acquired in given year
  year: Year
  acq_score: Acquisition score
  num_works: Number of works
  click_info: Click on chart to change selected catalog year
cs:
  absolute_acquisition_score: Absolutní akviziční skóre v čase
  absolute_acquisition_score_info: Celkový počet výpůjček děl získaných v daném roce v následujících 12 měsících
  relative_acquisition_score: Relativní akviziční skóre v čase
  relative_acquisition_score_info: Absolutní akviziční skóre vztažené na počet akvizic v daném roce
  year: Rok
  acq_score: Akviziční skóre
  num_works: Počet děl
  click_info: Kliknutím na graf změníte vybraný rok katalogizace
</i18n>
<template>
  <v-container fluid>
    <v-row>
      <v-col cols="6">
        <BarChartCard
          :url="`/api/bookrank/workset/WORKSET_UID/works/absolute_acquisition_score_summary/`"
          :title="$t('absolute_acquisition_score')"
          :titleInfo="$t('absolute_acquisition_score_info')"
          :dimension="{ name: $t('year'), value: 'catalog_year' }"
          :metrics="[
            {
              name: $t('acq_score'),
              value: 'acquisition_score_sum',
              type: 'bar',
            },
            {
              name: $t('num_works'),
              value: 'work_count',
              type: 'line',
              yAxisIndex: 1,
            },
          ]"
          :yAxis="[
            {
              name: $t('acq_score'),
            },
            {
              name: $t('num_works'),
              splitLine: { lineStyle: { opacity: 0.4 } },
            },
          ]"
          :chartHeight="300"
          :allowClick="true"
          @bar-clicked="handleBarClick"
          :clickInfo="true"
          :clickInfoText="$t('click_info')"
        />
      </v-col>
      <v-col cols="6">
        <BarChartCard
          :url="`/api/bookrank/workset/WORKSET_UID/works/relative_acquisition_score_summary/`"
          :title="$t('relative_acquisition_score')"
          :titleInfo="$t('relative_acquisition_score_info')"
          :dimension="{ name: $t('year'), value: 'catalog_year' }"
          :metrics="[
            {
              name: $t('acq_score'),
              value: 'acquisition_score_sum',
              type: 'bar',
            },
          ]"
          formater="formatRelativeAcqScore"
          :chartHeight="300"
          :allowClick="true"
          @bar-clicked="handleBarClick"
          :clickInfo="true"
          :clickInfoText="$t('click_info')"
        />
      </v-col>
    </v-row>
    <v-row>
      <v-col :cols="12">
        <WorksTable
          :showCatalogYearFilter="true"
          scoreType="acquisition_score"
          :catalogYear="catalogYear"
        />
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import WorksTable from "@/components/WorksTable";
import BarChartCard from "../components/charts/BarChartCard";

export default {
  name: "AcquisitionsPage",
  components: { WorksTable, BarChartCard },

  data() {
    return {
      catalogYear: null,
    };
  },

  methods: {
    handleBarClick(bin) {
      this.catalogYear = bin;
    },
  },
};
</script>
