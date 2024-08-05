<i18n src="../locales/common.yaml"></i18n>
<i18n>
en:
  general_stats: General stats
  num_loans: Number of loans
  num_subjects: Number of subjects
  interest_distribution: Interest distribution
  interest_distribution_info: Distribution of subjects based on number of loans
  size_measure: Chart metric
  score: Score
  work_count: Work count
  topic_map: Topic map
cs:
  general_stats: Celkové statistiky
  num_loans: Počet výpůjček
  num_subjects: Počet témat
  interest_distribution: Rozložení zájmu
  interest_distribution_info: Rozložení zájmu o témata podle počtu výpůjček
  size_measure: Metrika grafu
  score: Skóre
  work_count: Počet prací
  topic_map: Mapa témat
</i18n>

<template>
  <v-container fluid>
    <v-row>
      <v-col :cols="12">
        <v-expansion-panels>
          <v-expansion-panel>
            <v-expansion-panel-header
              >{{ $t("topic_map") }}
            </v-expansion-panel-header>

            <v-expansion-panel-content>
              <v-row>
                <v-col>
                  <div class="pb-2">
                    <span class="text-caption pr-2"
                      >{{ $t("size_measure") }}:</span
                    >
                    <v-btn-toggle v-model="scoreMeasure" mandatory>
                      <v-btn small value="acc_score">{{ $t("score") }}</v-btn>
                      <v-btn small value="acc_work_count">{{
                        $t("work_count")
                      }}</v-btn>
                    </v-btn-toggle>
                  </div>
                  <div :style="{ height: chartHeight }" v-resize="onResize">
                    <SubjectTreeMap
                      :parent-uid="rootNodeUid"
                      :value-attr="scoreMeasure"
                      chart-type="treemap"
                    />
                  </div>
                </v-col>
              </v-row>
            </v-expansion-panel-content>
          </v-expansion-panel>

          <v-expansion-panel>
            <v-expansion-panel-header>
              {{ $t("general_stats") }}
            </v-expansion-panel-header>
            <v-expansion-panel-content>
              <v-row>
                <v-col :cols="4">
                  <TopItemsWidget
                    topic-type="psh"
                    order-by="work_count"
                    :rootNode="rootNode"
                  />
                </v-col>
                <v-col :cols="4">
                  <TopItemsWidget
                    topic-type="psh"
                    order-by="score"
                    :rootNode="rootNode"
                  />
                </v-col>
                <v-col cols="4">
                  <BarChartCard
                    :url="`/api/hits/workhit/histogram/WORKSET_UID/psh?root_node=${rootNode}`"
                    :dimension="{ name: $t('num_loans'), value: 'name' }"
                    :metrics="[
                      { name: $t('num_subjects'), value: 'count', type: 'bar' },
                    ]"
                    :title="$t('interest_distribution')"
                    :titleInfo="$t('interest_distribution_info')"
                    :chartHeight="272"
                  />
                </v-col>
              </v-row>
              <v-row>
                <v-col :cols="6">
                  <TopItemsWidget
                    topic-type="psh"
                    order-by="absolute_growth"
                    :rootNode="rootNode"
                    :includeInfo="true"
                  />
                </v-col>
                <v-col :cols="6">
                  <TopItemsWidget
                    topic-type="psh"
                    order-by="relative_growth"
                    :rootNode="rootNode"
                    :includeInfo="true"
                  />
                </v-col>
              </v-row>
            </v-expansion-panel-content>
          </v-expansion-panel>
        </v-expansion-panels>
      </v-col>
    </v-row>
    <v-row>
      <v-col :cols="12" :md="4">
        <SubjectTree
          v-model="selectedTopics"
          :withLinks="true"
          :parent_uid="rootNodeUid"
        />
      </v-col>
      <v-col v-if="showCandidates" :cols="12" :md="8">
        <v-tabs grow v-model="tab">
          <v-tab>
            {{ $t("pages.works") }}
          </v-tab>
          <v-tab>
            {{ $t("pages.candidates") }}
          </v-tab>
        </v-tabs>
        <v-tabs-items v-model="tab">
          <v-tab-item>
            <WorksTable
              :filters="filters"
              :excludeHeaders="['isbn', 'lang.name', 'catalog_date']"
            />
          </v-tab-item>
          <v-tab-item>
            <CandidatesTable
              :filters="filters"
              :excludeHeaders="['isbn', 'langs', 'score']"
            />
          </v-tab-item>
        </v-tabs-items>
      </v-col>
      <v-col v-else>
        <WorksTable
          :filters="filters"
          :excludeHeaders="['isbn', 'lang.name', 'catalog_date']"
        />
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import CandidatesTable from "@/components/CandidatesTable";
import SubjectTree from "@/components/SubjectTree";
import WorksTable from "@/components/WorksTable";
import TopItemsWidget from "@/components/TopItemsWidget";
import BarChartCard from "../components/charts/BarChartCard";
import SubjectTreeMap from "@/components/charts/SubjectTreeMap";

export default {
  name: "SubjectTreePage",
  components: {
    SubjectTreeMap,
    CandidatesTable,
    SubjectTree,
    WorksTable,
    TopItemsWidget,
    BarChartCard,
  },
  props: {
    rootNode: { required: true, type: String },
    rootNodeUid: { required: true, type: String },
    showCandidates: { default: true, type: Boolean },
  },

  data() {
    return {
      tab: null,
      selectedTopics: [],
      scoreMeasure: "acc_score",
      height: window.innerHeight,
    };
  },

  computed: {
    filters() {
      if (this.selectedTopics.length) {
        return { psh: this.selectedTopics };
      }
      return {};
    },
    chartHeight() {
      return this.height < 940 ? "700px" : `${this.height - 240}px`;
    },
  },

  methods: {
    onResize() {
      this.height = window.innerHeight;
    },
  },
};
</script>
