<i18n>
en:
  rows:
    title: Title
    id: ID
    category: Category
    authors: Authors
    lang: Language
    psh: PSH
    publisher: Publisher
    yop: Year of publication
    institution: Fund
  cover: Cover
  score: Score
  hit_score: Hit score
  topic_score: Topic score
  interest_in_time: Interest in time
  no_data: No loan or online interest data.
  total: Total
  by_year: By year
  by_week: By week
  by_month: By month
  acquisition: Acquisition
  acquisition_year: Acquisition year
  acquisition_score: Acquisition score
  acquisition_score_desc: Number of loans in 12 month period after acquisition
  date: Date
  loans_24: Standard loans
  loans_25: In-house loans
  missing_date: Date not recorded
  total_num_copies: Total number of copies
  relative_score: Relative score
  rel_score_info: Total number of loans divided by number of copies
  num_copies: Number of copies
cs:
  rows:
    title: Název
    id: ID
    category: Kategorie
    authors: Autoři
    lang: Jazyk
    psh: PSH
    publisher: Vydavatel
    yop: Rok vydání
    institution: Fond
  cover: Obálka
  score: Zájem
  hit_score: Zájem o dílo
  topic_score: Zájem o témata
  interest_in_time: Zájem v čase
  no_data: Žádná data o výpůjčkách nebo online zájmu.
  total: Celkem
  by_year: Po rocích
  by_week: Po týdnech
  by_month: Po měsících
  acquisition: Akvizice
  acquisition_year: Rok akvizice
  acquisition_score: Akviziční skóre
  acquisition_score_desc: Počet výpůjček během 12 měsíců po akvizici
  date: Datum
  loans_24: Absenční výpůjčky
  loans_25: Prezenční výpůjčky
  missing_date: Datum není dostupné
  total_num_copies: Celkový počet kopií
  relative_score: Relativní skóre
  rel_score_info: Celkový počet výpůjček vztažený na jeden výtisk
  num_copies: Počet výtisků
</i18n>

<template>
  <v-container fluid>
    <v-row v-if="record" class="mr-6" justify="space-between">
      <v-col cols="7" md="4">
        <div class="overview">
          <table class="listing">
            <tr>
              <th>{{ $t("rows.title") }}</th>
              <td>{{ record.name }}</td>
            </tr>
            <tr>
              <th>{{ $t("rows.id") }}</th>
              <td>
                {{ record.uid }}
                <a
                  v-if="vufindLink"
                  :href="vufindLink"
                  class="ml-3"
                  target="_blank"
                  >VuFind
                  <v-icon x-small color="primary"
                    >fa fa-external-link-alt</v-icon
                  >
                </a>
              </td>
            </tr>
            <tr>
              <th>{{ $t("rows.category") }}</th>
              <td>
                <ExplicitTopicLink
                  v-if="record.category"
                  topic-type="work-type"
                  :topic-id="record.category.pk"
                >
                  {{ record.category.name }}
                </ExplicitTopicLink>
                <span v-else>-</span>
              </td>
            </tr>
            <tr>
              <th>{{ $t("rows.authors") }}</th>
              <td>
                <ul class="simple">
                  <li v-for="author in record.authors" :key="author.pk">
                    <strong>
                      <ExplicitTopicLink
                        topic-type="author"
                        :topic-id="author.pk"
                      >
                        {{ author.name }}
                      </ExplicitTopicLink>
                    </strong>
                  </li>
                </ul>
              </td>
            </tr>
            <tr>
              <th>{{ $t("rows.publisher") }}</th>
              <td>
                <div v-for="publisher in record.publishers" :key="publisher.pk">
                  <ExplicitTopicLink
                    topic-type="publisher"
                    :topic-id="publisher.pk"
                  >
                    {{ publisher.name }}
                  </ExplicitTopicLink>
                </div>
              </td>
            </tr>
            <tr>
              <th>{{ $t("rows.yop") }}</th>
              <td v-if="record.end_yop != record.start_yop">
                {{ record.start_yop }}&ndash;{{
                  record.end_yop ? record.end_yop : ""
                }}
              </td>
              <td v-else>
                {{ record.start_yop ? record.start_yop : "-" }}
              </td>
            </tr>
            <tr>
              <th>{{ $t("rows.lang") }}</th>
              <td>
                <ExplicitTopicLink
                  v-if="record.lang"
                  topic-type="language"
                  :topic-id="record.lang.pk"
                >
                  {{ record.lang.name.toUpperCase() }}
                </ExplicitTopicLink>
                <span v-else>-</span>
              </td>
            </tr>
            <tr>
              <th>{{ $t("rows.institution") }}</th>
              <td>
                <ExplicitTopicLink
                  v-if="record.owner_institution"
                  topic-type="owner"
                  :topic-id="record.owner_institution.pk"
                >
                  {{ record.owner_institution.name }}
                </ExplicitTopicLink>
                <span v-else>-</span>
              </td>
            </tr>
            <tr v-for="(val, schema) in record.subjects" :key="schema">
              <th>{{ schema.toUpperCase() }}</th>
              <td>
                <ul class="simple">
                  <li v-for="subject in val" :key="subject.pk">
                    <ExplicitTopicLink topic-type="psh" :topic-id="subject.pk">
                      {{ subject.name }}
                    </ExplicitTopicLink>
                  </li>
                </ul>
              </td>
            </tr>
          </table>
        </div>
      </v-col>

      <v-col cols="auto" order="1" order-md="3" v-if="record.cover_image_url">
        <img
          :src="record.cover_image_url"
          :alt="$t('cover')"
          class="book-cover"
        />
      </v-col>

      <v-col
        cols="6"
        md="2"
        v-if="record.acquisition_date || !isEmpty(hitSummaryData)"
        order="3"
        order-md="2"
      >
        <div v-if="record.acquisition_date">
          <h2 class="title mb-2">{{ $t("acquisition") }}</h2>
          <div class="overview">
            <table class="listing">
              <tr>
                <th>{{ $t("acquisition_year") }}</th>
                <td class="text-right">
                  {{ record.acquisition_date.slice(0, 4) }}
                </td>
              </tr>
              <tr>
                <th>
                  {{ $t("acquisition_score") }}
                  <v-tooltip bottom>
                    <template v-slot:activator="{ on, attrs }">
                      <v-icon v-bind="attrs" v-on="on" x-small>
                        fa-info-circle
                      </v-icon>
                    </template>
                    <span>{{ $t("acquisition_score_desc") }}</span>
                  </v-tooltip>
                </th>
                <td class="text-right">
                  {{ record.acquisition_score }}
                </td>
              </tr>
            </table>
          </div>
        </div>
        <div v-if="!isEmpty(hitSummaryData)">
          <h2 class="title mb-2">{{ $t("score") }}</h2>
          <div class="overview">
            <table class="listing">
              <tr v-for="rec in hitSummaryData" :key="rec.name">
                <th>{{ rec.name }}</th>
                <td class="text-right">{{ rec.score }}</td>
              </tr>
              <tr class="sum">
                <th>{{ $t("total") }}</th>
                <td class="text-right">{{ totalScore }}</td>
              </tr>
            </table>
          </div>
        </div>
      </v-col>

      <v-col
        cols="6"
        md="3"
        v-if="copiesData && copiesData.totalNumCopies"
        order="2"
        order-md="1"
      >
        <div class="overview">
          <table class="listing">
            <tr>
              <th>{{ $t("total_num_copies") }}</th>
              <td class="text-right">
                {{ copiesData.totalNumCopies }}
              </td>
            </tr>
            <tr v-if="copiesData.years.length">
              <th>
                {{ $t("relative_score") }}
                <v-tooltip bottom>
                  <template v-slot:activator="{ on, attrs }">
                    <v-icon v-bind="attrs" v-on="on" x-small>
                      fa-info-circle
                    </v-icon>
                  </template>
                  <span>{{ $t("rel_score_info") }}</span>
                </v-tooltip>
              </th>
              <td class="text-right">
                {{ copiesData.relativeScore }}
              </td>
            </tr>
          </table>
        </div>
        <v-simple-table
          dense
          v-if="copiesData.years.length"
          fixed-header
          height="200px"
        >
          <template v-slot:default>
            <thead>
              <tr>
                <th class="text-left">{{ $t("acquisition_year") }}</th>
                <th class="text-left">{{ $t("num_copies") }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in copiesData.years" :key="item.year">
                <td>{{ item.year }}</td>
                <td>{{ item.numCopies }}</td>
              </tr>
            </tbody>
          </template>
        </v-simple-table>
      </v-col>
    </v-row>

    <div v-if="record">
      <h2>{{ $t("interest_in_time") }}</h2>
      <div v-if="hitData.length">
        <v-row>
          <v-col align="right" class="flex-column">
            <v-btn-toggle v-model="axisToggle" mandatory>
              <v-btn>{{ $t("by_week") }}</v-btn>
              <v-btn>{{ $t("by_month") }}</v-btn>
              <v-btn>{{ $t("by_year") }}</v-btn>
            </v-btn-toggle>
          </v-col>
        </v-row>
        <BarChartCard
          :url="hitChartDataUrl"
          dataProp="stats"
          :dimensionFromMeta="true"
          dimensionValueProp="date"
          :metricsFromMeta="true"
        />
      </div>
      <div v-else>
        <v-alert :value="true" outlined color="grey" icon="fa-info-circle">{{
          $t("no_data")
        }}</v-alert>
      </div>
    </div>
  </v-container>
</template>

<script>
import axios from "axios";
import "echarts/lib/component/markArea";
import isEmpty from "lodash/isEmpty";
import { mapActions, mapGetters } from "vuex";
import { stringify } from "query-string";
import ExplicitTopicLink from "./ExplicitTopicLink";
import BarChartCard from "./charts/BarChartCard";
import { format2SignificantPlaces } from "../libs/numbers";

export default {
  name: "WorkDetail",

  components: {
    ExplicitTopicLink,
    BarChartCard,
  },

  props: {
    workId: { required: true, type: Number },
  },

  data() {
    return {
      record: null,
      isLoading: false,
      queryText: "",
      alephRecord: null,
      hitData: [],
      hitDataExtra: {},
      hitDataMeta: {},
      hitSummaryData: {},
      axisToggle: 2,
      copiesData: null,
    };
  },

  computed: {
    ...mapGetters({
      selectedWorksetUUID: "selectedWorksetUUID",
      dateRangeQueryParams: "dateRangeQueryParams",
      vufindUrl: "vufindUrl",
      subjectSchemas: "subjectSchemas",
    }),
    workDataUrl() {
      if (this.selectedWorksetUUID && this.workId) {
        return `/api/bookrank/workset/${this.selectedWorksetUUID}/works/${this.workId}/`;
      }
      return null;
    },
    copiesDataUrl() {
      if (this.selectedWorksetUUID && this.workId) {
        return `/api/bookrank/workset/${this.selectedWorksetUUID}/works/${this.workId}/copies/`;
      }
      return null;
    },

    step() {
      return ["week", "month", "year"][this.axisToggle];
    },
    hitChartDataUrl() {
      if (this.workId) {
        const params = {
          step: this.step,
          ...this.dateRangeQueryParams,
        };
        return `/api/hits/workhit/time-stats/${this.workId}/?${stringify(
          params
        )}`;
      }
      return null;
    },
    hitSummaryUrl() {
      if (this.workId) {
        const params = {
          ...this.dateRangeQueryParams,
        };
        return `/api/hits/workhit/hits/${this.workId}/?${stringify(params)}`;
      }
      return null;
    },
    totalScore() {
      return this.hitSummaryData.map((x) => x.score).reduce((x, y) => x + y);
    },
    vufindLink() {
      if (this.vufindUrl && this.record) {
        return this.vufindUrl + "Record/" + this.record.uid;
      }
    },
  },
  methods: {
    ...mapActions({
      showSnackbar: "showSnackbar",
    }),
    format2SignificantPlaces,
    async loadWork() {
      if (this.workDataUrl) {
        this.isLoading = true;
        try {
          const response = await axios.get(this.workDataUrl);
          this.record = response.data;
          this.record.subjects = this.subjectSchemas.reduce((acc, next) => {
            let subjectList = this.record.subject_categories.filter(
              (e) => e.root_node.toLowerCase() == next
            );
            if (subjectList.length) acc[next] = subjectList;
            return acc;
          }, {});
        } catch (error) {
          this.showSnackbar({
            content: "Error fetching data: " + error,
            color: "error",
          });
          console.log("Error fetching data", error);
        } finally {
          this.isLoading = false;
        }
      }
    },
    async loadHitData() {
      if (this.hitChartDataUrl) {
        try {
          const response = await axios.get(this.hitChartDataUrl);
          this.hitData = response.data.stats;
          this.hitDataExtra = response.data.extra;
          this.hitDataMeta = response.data.meta;
        } catch (error) {
          this.showSnackbar({
            content: "Error fetching hit statistics: " + error,
            color: "error",
          });
          console.log("Error fetching data", error);
        }
      }
    },
    async loadHitSummary() {
      if (this.hitSummaryUrl) {
        try {
          const response = await axios.get(this.hitSummaryUrl);
          this.hitSummaryData = response.data;
        } catch (error) {
          this.showSnackbar({
            content: "Error fetching hit summary: " + error,
            color: "error",
          });
          console.log("Error fetching data", error);
        }
      }
    },
    async loadCopiesData() {
      if (!this.copiesDataUrl) return null;
      try {
        const resp = await axios.get(this.copiesDataUrl);
        this.copiesData = {
          totalNumCopies: resp.data.total_num_copies,
          relativeScore: format2SignificantPlaces(resp.data.relative_score),
          years: resp.data.years.map((el) => {
            return {
              year: el.year
                ? el.year.slice(0, 4)
                : this.$i18n.t("missing_date"),
              numCopies: el.num_copies,
            };
          }),
        };
      } catch (error) {
        this.showSnackbar({
          content: "Error fetching hit summary: " + error,
          color: "error",
        });
        console.log("Error fetching data", error);
      }
    },
    isEmpty(obj) {
      return isEmpty(obj);
    },
  },
  watch: {
    workDataUrl() {
      this.loadWork();
    },
    hitChartDataUrl() {
      this.loadHitData();
    },
    hitSummaryUrl() {
      this.loadHitSummary();
    },
    copiesDataUrl() {
      this.loadCopiesData();
    },
  },
  created() {
    this.loadWork();
    this.loadHitData();
    this.loadHitSummary();
    this.loadCopiesData();
  },
};
</script>

<style scoped lang="scss">
div.fields {
  margin-top: 1rem;
}

div.overview {
  padding: 0 0 1rem 0;
}

table.listing {
  font-size: 0.875rem;
  border-collapse: collapse;

  tr {
    th,
    td {
      border-bottom: solid 1px #dddddd;
    }

    &:last-of-type {
      th,
      td {
        border-bottom: none;
      }
    }

    &.sum {
      th,
      td {
        border-top: double 3px #dddddd;
      }
    }
  }

  th {
    text-align: left;
    padding-right: 2.5rem;
  }
}

ul.simple {
  list-style: none;
  padding-left: 0;
}

.v-application ul.simple {
  padding-left: 0;
}

img.book-cover {
  max-height: 240px;
}
</style>
